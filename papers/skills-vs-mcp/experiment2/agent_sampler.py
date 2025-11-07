from anthropic import Anthropic
import asyncio
import time
from typing import Any, Dict

from claude_agent.agent import ClaudeAgent
from claude_agent.custom_skills import set_custom_skills

from utils import load_config
from browsecomp.types import MessageList, SamplerBase, SamplerResponse


class AgentSampler(SamplerBase):
    """
    Sampler that wraps a ClaudeAgent with MCP support for use in evaluations.
    """

    def __init__(
        self,
        config_path: str = "config.json",
        max_iterations: int = 35,
        use_skills: bool = False,
    ):
        """
        Initialize an AgentSampler.

        Args:
            config_path: Path to the config.json file
            max_iterations: Maximum number of tool execution iterations
            use_skills: Whether to use skills (if False, uses MCP only)
        """
        self.config_path = config_path
        self.config = load_config(config_path)
        self.max_iterations = max_iterations
        self.use_skills = use_skills

        # Agent will be initialized when first called
        self._agent = None
        self._initialized = False


    async def _initialize_agent(self):
        """
        Initialize the agent with MCP servers and skills.
        """
        if self._initialized:
            return

        claude_conf = self.config["claude"]
        mcp_conf = self.config.get("mcp_servers", {})
        skills_conf = self.config.get("skills", {})

        # Setup custom skills (only if use_skills is True)
        sync_client = Anthropic(api_key=claude_conf["api_key"])
        skills = []

        if self.use_skills:
            if skills_conf.get("custom_skill_folders"):
                skills = set_custom_skills(
                    sync_client,
                    skills_conf["custom_skill_folders"],
                    force_update=False
                )

            # Add anthropic skills
            if skills_conf.get("anthropic_skills"):
                skills.extend(skills_conf.get("anthropic_skills", []))

        # Initialize Claude Agent
        # Only pass skills and betas if use_skills is True
        agent_kwargs = {
            "api_key": claude_conf["api_key"],
            "model": claude_conf.get("model", "claude-sonnet-4-5-20250929"),
            "max_tokens": claude_conf.get("max_tokens", 4096),
            "temperature": claude_conf.get("temperature", 1.0),
        }

        if self.use_skills:
            agent_kwargs["betas"] = skills_conf.get("betas", [])
            agent_kwargs["skills"] = skills
            agent_kwargs["configured_tools"] = skills_conf.get("tools", [])

        self._agent = ClaudeAgent(**agent_kwargs)

        # Connect to MCP servers
        for server_name, server_config in mcp_conf.items():
            command = server_config.get("command")
            args = server_config.get("args", [])
            env = server_config.get("env", {})

            success = await self._agent.add_mcp(
                name=server_name,
                command=command,
                args=args,
                env=env
            )

        self._initialized = True


    async def _cleanup_agent(self):
        """
        Cleanup MCP connections.
        """
        if self._agent:
            await self._agent.disconnect_all_mcp()


    def _pack_message(
        self, 
        content: Any, 
        role: str = "user"
    ) -> Dict[str, Any]:
        """
        Pack a message into the format expected by ClaudeAgent.
        
         Args:
            content: Message content (string or structured content)
            role: Message role (default: "user")

        Returns:
            Dict: Message in ClaudeAgent format with 'role' and 'content' keys
        """
        if isinstance(content, str):
            return {"role": role, "content": content}
        return {"role": role, "content": content}


    def _convert_message_list(
        self, 
        message_list: MessageList
    ) -> str:
        """
        Convert MessageList to a single user message string.
        
        Args:
            message_list: List of messages from BrowseComp evaluation

        Returns:
            str: Combined text from all messages
        """
        # Extract text from all messages
        texts = []
        for msg in message_list:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                # Extract text from content blocks
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        texts.append(block.get("text", ""))
                    elif isinstance(block, str):
                        texts.append(block)
            else:
                texts.append(str(content))
        
        # Combine all text into a single message
        return "\n".join(texts)


    async def _call_async(
        self,
        message_list: MessageList
    ) -> SamplerResponse:
        """
        Async implementation of the sampler.

        Args:
            message_list: List of messages from BrowseComp evaluation

        Returns:
            SamplerResponse: Agent's response with metadata
        """
        # Only initialize once per AgentSampler instance
        if not self._initialized:
            await self._initialize_agent()

        # Reset agent's message history for each evaluation
        self._agent.messages = []
        # Also reset API responses for clean usage stats
        self._agent.api_responses = []

        # Convert message_list to a single user message
        user_message = self._convert_message_list(message_list)

        # Track execution time
        start_time = time.time()

        # Call agent with MCP support
        result = await self._agent.answer_with_mcp(
            message=user_message,
            max_iterations=self.max_iterations
        )

        end_time = time.time()
        duration = end_time - start_time

        # Extract response text
        response_text = result.get("text", "")

        # Get usage statistics
        usage_stats = self._agent.get_usage_stats()

        # Get actual messages that were sent to the API
        actual_queried_messages = self._agent.messages.copy()

        # Convert to MessageList format (simplified)
        actual_queried_message_list = []
        for msg in actual_queried_messages:
            role = msg.get("role")
            content = msg.get("content", "")

            # Convert content to string format
            if isinstance(content, list):
                text_content = ""
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            text_content += block.get("text", "")
                        elif block.get("type") == "tool_use":
                            # Skip tool use blocks in the message list
                            continue
                    elif isinstance(block, str):
                        text_content += block
                if text_content:
                    actual_queried_message_list.append({
                        "role": role,
                        "content": text_content
                    })
            elif isinstance(content, str):
                actual_queried_message_list.append({
                    "role": role,
                    "content": content
                })

        # Build comprehensive metadata
        metadata = {
            "duration_seconds": round(duration, 2),
            "stop_reason": usage_stats["stop_reason"],
            "usage": {
                "input_tokens": usage_stats["input_tokens"],
                "output_tokens": usage_stats["output_tokens"]
            },
            "tool_calls": usage_stats["total_tool_calls"],
            "api_call_count": usage_stats["api_call_count"],
            "messages": self._agent.messages,
            "full_usage_stats": usage_stats,
        }

        return SamplerResponse(
            response_text=response_text,
            actual_queried_message_list=actual_queried_message_list,
            response_metadata=metadata,
        )


    def __call__(
        self,
        message_list: MessageList
    ) -> SamplerResponse:
        """
        Main entry point called by the BrowseComp evaluation framework.

        This is a synchronous wrapper that internally runs async code (_call_async),
        allowing it to be called like a regular synchronous function.

        Args:
            message_list: List of messages from BrowseComp evaluation

        Returns:
            SamplerResponse: Agent's response text and metadata
        """
        # Try to reuse existing event loop
        try:
            loop = asyncio.get_event_loop()
            # Reuse the loop if it is idle
            if not loop.is_running():
                return loop.run_until_complete(self._call_async(message_list))
        except RuntimeError:
            # No event loop available
            pass

        # Create and run a new event loop
        # This path is typically used when called from ThreadPool workers
        return asyncio.run(self._call_async(message_list))


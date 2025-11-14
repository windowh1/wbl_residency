from anthropic import AsyncAnthropic
from typing import List, Dict, Optional, Any
import json
import os

from mcp_server.client import MCPClient
from mcp_server.http_proxy import MCPHttpProxy
from .code_execution import run_agent_script
from .prompts import CODE_EXECUTION_SYSTEM_PROMPT, CODE_EXECUTION_FEEDBACK_PROMPT, SKILL_CREATION_PROMPT, AGGREGATE_SKILL_CREATION_PROMPT


class ClaudeAgent:
    """
    Agent class that integrates the Claude API with MCP servers, Skills, wrapper-code execution.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        code_execution_conf: Optional[Dict[str, Any]] = None,
        betas: Optional[List[str]] = None,
        skills: Optional[List[Dict[str, Any]]] = None,
        configured_tools: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None
    ):
        """
        Initialize a ClaudeAgent instance.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum number of tokens
            temperature: Generation temperature (0.0 - 1.0)
            code_execution_conf: Code execution configuration
            betas: Beta features to enable
            skills: Skills to use (for Skills API)
            configured_tools: Tools from config (e.g., code_execution)
            session_id: Session ID for code execution workspace
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.messages = [] # Conversation messages history
        self.use_code_execution = code_execution_conf.get("enabled", False) if code_execution_conf else False
        self.code_execution_conf = code_execution_conf or {}
        self.tools = configured_tools or []
        
        self.params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": CODE_EXECUTION_SYSTEM_PROMPT if self.use_code_execution \
                else "You are a helpful AI assistant.",
            "messages": self.messages,
            "tools": self.tools
        }

        if betas:
            self.params["betas"] = betas
        if skills:
            self.params["container"] = {"skills": skills}
        
        self.use_beta = (betas or skills)
        self.session_id = session_id or "00000000_000000"

        self.api_responses = [] # API responses history
        self.http_proxy = None  # HTTP proxy for code execution mode
        self.mcp_clients = {}


    # ------------------------------
    # MCP connection & execution
    # ------------------------------
    async def _setup_http_proxy(
        self,
        mcp_config: Dict[str, Dict[str, Any]]
    ):
        """
        Start HTTP proxy for stdio MCP servers (code execution mode).
        
        Args:
            mcp_config: MCP server configuration from config.json
        """
        # Check if there are any stdio servers
        stdio_servers = [
            name for name, cfg in mcp_config.items() 
            if "url" not in cfg
        ]

        print(f"\n{'-'*30}")
        if not stdio_servers:
            print("No stdio MCP servers found, skipping HTTP proxy setup.")
            return        
        print("Starting HTTP proxy for code execution mode...")        
        
        try:
            host = self.code_execution_conf.get("host", "localhost")
            port = self.code_execution_conf.get("port", 8082)

            self.http_proxy = MCPHttpProxy(mcp_config, host, port)
            self.http_proxy.start()            
        
        except Exception as e:
            print(f"Failed to start HTTP proxy: {e}")
            return


    async def _add_mcp(
        self,
        name: str,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        url: Optional[str] = None
    ) -> bool:
        """
        Register and connect to a MCP server (direct mode).

        Args:
            name: MCP server name
            command: Command to execute (for stdio transport)
            args: Command arguments list (for stdio transport)
            env: Environment variables dictionary (for stdio transport)
            url: HTTP URL for streamable HTTP transport

        Returns:
            bool: Server connection success status
        """
        client = MCPClient(name, command=command, args=args, env=env, url=url)
        
        try:
            await client.connect()
            self.mcp_clients[name] = client
            self.tools.extend(client.tools)
            return True
        
        except Exception as e:
            print(f"[{name}] Failed to connect to server: {e}")
            return False


    async def _setup_direct_connections(
        self,
        mcp_config: Dict[str, Dict[str, Any]]
    ):
        """
        Connect to MCP servers directly (direct mode).
        
        Args:
            mcp_config: MCP server configuration from config.json
        """
        print(f"\n{'-'*30}")
        print("Connecting to MCP servers...\n")

        for server_name, server_config in mcp_config.items():
            command = server_config.get("command")
            args = server_config.get("args", [])
            env = server_config.get("env", {})
            url = server_config.get("url")

            try:
                success = await self._add_mcp(
                    name=server_name,
                    command=command,
                    args=args,
                    env=env,
                    url=url
                )

                if not success:
                    print(f"[{server_name}] Warning: Failed to connect")

            except Exception as e:
                print(f"[{server_name}] Failed to connect: {e}")


    async def setup_mcp_servers(
        self,
        mcp_config: Dict[str, Dict[str, Any]]
    ):
        """
        Setup MCP servers based on the selected mode (code execution vs direct).
        
        Args:
            mcp_config: MCP server configuration from config.json
        """
        if self.use_code_execution:
            # Code execution mode: start HTTP proxy for stdio servers
            await self._setup_http_proxy(mcp_config)
        else:
            # Direct mode: connect to all MCP servers directly
            await self._setup_direct_connections(mcp_config)
        
        # Update tools in params
        if len(self.tools) > 0:
            self.params["tools"] = self.tools


    async def _execute_mcp_tool(
        self, 
        mcp_tool_name: str, 
        tool_input: Dict[str, Any]
    ) -> str:
        """
        Locate and execute the specified MCP tool.

        Args:
            mcp_tool_name: Tool name in the format "server_name__tool_name"
            tool_input: Input data for the tool

        Returns:
            str: Tool execution result
        """
        parts = mcp_tool_name.split("__", 1)
        if len(parts) != 2:
            raise RuntimeError(f"Invalid tool name format: {mcp_tool_name}")

        server_name, tool_name = parts
        client = self.mcp_clients.get(server_name)
        if not client:
            raise RuntimeError(f"[{server_name}] Server does not exist.")
        
        return await client.call_tool(tool_name, tool_input)


    async def disconnect_mcp_servers(self):
        """
        Disconnect from all MCP resources (servers and proxy).
        """
        # Stop HTTP proxy if running
        if self.http_proxy:
            print("Stopping HTTP proxy...")
            try:
                self.http_proxy.stop()
                self.http_proxy = None
            except Exception as e:
                print(f"Warning while stopping HTTP proxy: {e}")
        
        # Disconnect direct MCP connections
        if self.mcp_clients:
            print("Disconnecting from MCP servers...")
            for name, client in self.mcp_clients.items():
                try:
                    await client.disconnect()
                except Exception as e:
                    print(f"[{name}] Warning while disconnecting: {e}")
            self.mcp_clients.clear()


    # ------------------------------
    # Helper methods
    # ------------------------------
    def _extract_text(
        self, 
        response: Any
    ) -> str:
        """
        Extract plain text content from a Claude API response.

        Args:
            response: Claude API response

        Returns:
            str: Extracted text
        """
        text_parts = []
        for item in response.content:
            if getattr(item, "type", None) == "text":
                text_parts.append(item.text)
        return "\n".join(text_parts)        


    def _extract_server_tool_use(
        self, 
        response: Any
    ) -> str:
        """
        Extract server tool use information from a Claude API response.

        Args:
            response: Claude API response

        Returns:
            str: Extracted server tool use information
        """
        server_tool_uses = []
        server_tool_results = {}
        
        for item in response.content:
            if getattr(item, "type", None) == "server_tool_use":
                use = {"id": item.id, "name": item.name}
                if getattr(item, "input", None) is not None:
                    use["input"] = item.input
                server_tool_uses.append(use)
            if hasattr(item, "tool_use_id") and hasattr(item, "content"):
                server_tool_results[item.tool_use_id] = item.content
        
        for use in server_tool_uses:
            if use["id"] in server_tool_results and hasattr(server_tool_results[use["id"]], "content"):
                use["result"] = server_tool_results[use["id"]].content

        return server_tool_uses


    def _extract_tool_calls(
        self, 
        response: Any
    ) -> List[Dict[str, Any]]:
        """
        Extract tool call information from a Claude API response.

        Args:
            response: Claude API response

        Returns:
            List: Extracted tool call list
        """
        tool_calls = []
        for item in response.content:
            if getattr(item, "type", None) == "tool_use":
                tool_calls.append({"id": item.id, "name": item.name, "input": item.input})

        return tool_calls
    

    def _add_message(
        self, 
        role: str, 
        content: Any
    ):
        """
        Add a new message to messages.

        Args:
            role: Message role ("user" or "assistant")
            content: Message content
        """
        if isinstance(content, list) and len(content) > 0:
            if hasattr(content[0], "model_dump"):
                content = [block.model_dump() for block in content]
        
        self.messages.append({
            "role": role,
            "content": content
        })


    def reset_messages(self):
        """
        Clear the conversation messages history.
        """
        self.messages.clear()


    def set_max_tokens(
        self,
        max_tokens: int
    ):
        """
        Update the maximum number of tokens for generation.

        Args:
            max_tokens: Maximum number of tokens
        """
        self.params["max_tokens"] = max_tokens
    

    # ------------------------------
    # Core answer methods
    # ------------------------------
    async def _non_streaming_call(self) -> Any:
        """
        Make a non-streaming API call and print the response.
            
        Returns:
            Claude API response
        """
        try:
            response = await self.client.beta.messages.create(**self.params) if self.use_beta \
                else await self.client.messages.create(**self.params)
        except Exception as e:
            raise RuntimeError(f"Failed to call Claude API: {e}")
        
        # Print response
        text_part = self._extract_text(response)
        print(f"\n{'='*30}")
        print(f"Claude:\n{text_part}")

        # Print server tool use information
        server_tool_use = self._extract_server_tool_use(response)
        for use in server_tool_use:
            name = use["name"]
            input_str = str(use.get("input", ""))
            print(f"\n{'-'*30}")
            print(f"Server tool use:\n{name} (input: {input_str[:150]}{'...' if len(input_str) > 150 else ''})")
            if "result" in use:
                print(f"\nTool result:\n{str(use['result'])[:150]}{'...' if len(str(use['result'])) > 150 else ''}")
        
        return response


    async def _streaming_call(self) -> Any:
        """
        Make a streaming API call and print the response in real-time.
            
        Returns:
            Claude API response
        """
        params_for_stream = {k: v for k, v in self.params.items() if k != "stream"}
        
        try:
            async with self.client.beta.messages.stream(**params_for_stream) if self.use_beta \
                else self.client.messages.stream(**params_for_stream) as stream:
                
                print(f"\n{'='*30}")
                print("Claude:\n", end="", flush=True)
                
                in_text_block = False
                current_tool_use_id = None
                
                async for event in stream:
                    event_type = event.type
                    
                    # Text content streaming
                    if event_type == "content_block_start":
                        content = event.content_block
                        
                        if content.type == "text":
                            in_text_block = True
                        
                        # Start server tool use
                        elif content.type == "server_tool_use":
                            print(f"\n\n{'-'*30}")
                            print(f"Server tool use:\n{content.name}", end="")
                            current_tool_use_id = content.id

                        # Print result of server tool use
                        elif content.type == "text_editor_code_execution_tool_result":
                            if hasattr(content, 'content') and hasattr(content.content, 'content'):
                                result_str = str(content.content.content)
                                print(f"\nTool result:\n{result_str[:150]}{'...' if len(result_str) > 150 else ''}\n")

                    elif event_type == "content_block_delta":
                        delta = event.delta
                        
                        # Text delta streaming
                        if delta.type == "text_delta" and in_text_block:
                            print(delta.text, end="", flush=True)
                        
                        # Tool input JSON streaming (skipped for brevity)
                        elif delta.type == "input_json_delta" and current_tool_use_id:
                            pass 
                    
                    elif event_type == "content_block_stop": 
                        content_block = event.content_block
                        
                        if in_text_block:
                            in_text_block = False
                        
                        # Print input of server tool use
                        elif hasattr(content_block, "type") and content_block.type == "server_tool_use":
                            if hasattr(content_block, "input") and content_block.input:
                                input_str = str(content_block.input)
                                print(f" (input: {input_str[:150]}{'...' if len(input_str) > 150 else ''})\n")
                            current_tool_use_id = None
                
                response = await stream.get_final_message()
                
        except Exception as e:
            raise RuntimeError(f"Failed to stream Claude API: {e}")
        
        return response


    async def _answer_basic(
        self, 
        message: Optional[str] = None,
        stream: bool = True
    ) -> Dict[str, Any]:
        """
        Send a message to the Claude API and generate a response.

        Args:
            message: User input message
            stream: Whether to use streaming for real-time output

        Returns:
            Dict:
                - response: Claude API response
                - text: Text extracted from Claude API response
                - tool_calls: Tool call list extracted from Claude API response
        """
        if message:
            self._add_message("user", message)

        # First API call
        if stream:
            response = await self._streaming_call()
        else:
            response = await self._non_streaming_call()

        self.api_responses.append(response)
        self._add_message("assistant", response.content)

        text_part = self._extract_text(response)
        return {
            "response": response,
            "text": text_part,
            "tool_calls": self._extract_tool_calls(response)
        }


    async def _answer_basic_pause_handling(
        self, 
        message: Optional[Any] = None,
        stream: bool = True,
        max_pause_turns: int = 3
    ) -> Dict[str, Any]:
        """
        Send a message to the Claude API and handle Skills pause_turn responses.

        Args:
            message: User input message
            stream: Whether to use streaming for real-time output
            max_pause_turns: Maximum number of times to continue when Skills operations return pause_turn stop reason

        Returns:
            Dict: Final response
        """

        result = await self._answer_basic(message, stream)

        # Store container ID after first API call for Skills
        if (self.params.get("container") and 
            not self.params["container"].get("id") and
            hasattr(result["response"], "container")):
            container_id = getattr(result["response"].container, "id", None)
            if container_id:
                self.params["container"]["id"] = container_id

        # Handle pause_turn for long operations
        iteration = 0
        while iteration < max_pause_turns:
            if result["response"].stop_reason != "pause_turn":
                break
            
            print("\nContinuing after pause_turn...")
            result = await self._answer_basic(stream=stream)
            iteration += 1

        if iteration >= max_pause_turns and result["response"].stop_reason == "pause_turn":
            print(f"Reached maximum pause turns ({max_pause_turns}) and response generation stopped.")

        return result

    async def _answer_with_code(
        self,
        message: str,
        stream: bool = True,
        max_pause_turns: int = 3,
        max_iterations: int = 50,
        timeout: int = 20
    ) -> Dict[str, Any]:
        """
        Iterative code-execution loop: model emits code blocks, then we execute and feed back.

        Args:
            message: User input message
            stream: Whether to use streaming for real-time output
            max_pause_turns: Maximum number of times to continue when Skills operations return pause_turn stop reason
            max_iterations: max reasoning-code-execution cycles
            timeout: code execution timeout (seconds)

        Returns:
            Dict: Final response
        """
        result = await self._answer_basic_pause_handling(message, stream, max_pause_turns)
        
        iteration = 0
        while iteration < max_iterations:
            text = result["text"]
            if "```python" not in text:
                break

            code_block, inside = [], False
            for line in text.splitlines():
                s = line.strip()
                if s.startswith("```"):
                    inside = not inside
                    continue
                if inside:
                    code_block.append(line)
            code_str = "\n".join(code_block)

            print(f"\n\n{'-'*30}")
            exec_result = run_agent_script(
                code_str, 
                iteration, 
                session_id=self.session_id,
                timeout=timeout
            )
            stdout = exec_result.get("stdout", "")
            stderr = exec_result.get("stderr", "")
            combined = stdout or stderr or "No output."

            print(f"\nExecution result:\n{combined[:300]}{'...' if len(combined)>300 else ''}\n")

            script_path = os.path.join("./workspaces", self.session_id, f"script_{iteration + 1}.py")
            feedback = CODE_EXECUTION_FEEDBACK_PROMPT.format(combined=combined, script_path=script_path)

            result = await self._answer_basic_pause_handling(feedback, stream, max_pause_turns)
            iteration += 1

        if iteration >= max_iterations and "```" in result["text"]:
            print(f"\nReached maximum iterations ({max_iterations}) and response generation stopped. Code blocks may remain.")

        return result


    async def _answer_with_mcp(
        self, 
        message: str,
        stream: bool = True,
        max_pause_turns: int = 3,
        max_iterations: int = 50
    ) -> Dict[str, Any]:
        """
        Automatically handle MCP tool calls during a conversation with Claude.

        Args:
            message: User input message
            stream: Whether to use streaming for real-time output
            max_pause_turns: Maximum number of times to continue when Skills operations return pause_turn stop reason
            max_iterations: Maximum number of tool call/result cycles in the agentic loop

        Returns:
            Dict: Final response
        """
        result = await self._answer_basic_pause_handling(message, stream, max_pause_turns)
        
        iteration = 0
        while iteration < max_iterations:
            tool_calls = result["tool_calls"]
            if not tool_calls:
                break

            tool_results = []
            
            for tool_call in tool_calls:
                tool_use_id = tool_call["id"]
                tool_name = tool_call["name"]
                tool_input = tool_call["input"]

                print(f"\n\n{'-'*30}")
                print(f"Local tool use:\n{tool_name} (input: {tool_input})")

                try:
                    tool_result = await self._execute_mcp_tool(tool_name, tool_input)
                    print(f"\nTool result:\n{tool_result[:150]}{'...' if len(tool_result) > 150 else ''}")

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": str(tool_result)
                        }
                    )

                except Exception as e:
                    print(f"Failed to execute tool: {e}")
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": f"Error: {str(e)}",
                            "is_error": True
                        }
                    )

            result = await self._answer_basic_pause_handling(tool_results, stream, max_pause_turns)
            iteration += 1

        if iteration >= max_iterations and result["tool_calls"]:
            print(f"Reached maximum iterations ({max_iterations}) and response generation stopped. Some tool calls may remain.")

        return result
    

    async def answer(
        self, 
        message: str,
        stream: bool = True,
        max_pause_turns: int = 3,
        max_iterations: int = 50,
        timeout: int = 20
    ) -> Dict[str, Any]:
        """
        General answer method that selects between MCP and code execution modes.

        Args:
            message: User input message
            stream: Whether to use streaming for real-time output
            max_pause_turns: Maximum number of times to continue when Skills operations return pause_turn stop reason
            max_iterations: Maximum number of tool call/result cycles in the agentic loop   
            timeout: code execution timeout (seconds)
        Returns:
            Dict: Final response
        """
        if self.use_code_execution:
            return await self._answer_with_code(
                message, 
                stream, 
                max_pause_turns, 
                max_iterations,
                timeout
            )
        else:
            return await self._answer_with_mcp(
                message, 
                stream, 
                max_pause_turns, 
                max_iterations
            )            


    # ------------------------------
    # Skill creation from conversation
    # ------------------------------
    async def create_skill_from_conversation(
        self
    ) -> Optional[Dict[str, Any]]:
        """
        Use skill-creator to analyze the conversation and create a new skill.

        Returns:
            Dict: Skill creation result or None if failed
        """        
        print(f"\n{'='*30}")
        print("Attempting to create new skill from conversation...")
    
        skill_creation_prompt = SKILL_CREATION_PROMPT 
        try:
            result = await self.answer(skill_creation_prompt)

            stop_reason = result["response"].stop_reason
            success = (stop_reason == "end_turn")
            if not success:
                print(f"\n\nSkill creation did not complete successfully. Stop reason: {stop_reason}")

            return {
                "success": success,
                "stop_reason": stop_reason
            }
            
        except Exception as e:
            print(f"\n\nError during skill creation: {e}")
            return {
                "success": False,
                "error": str(e)
            }


    async def create_skill_from_conversation_list(
        self,
        conversation_list: List[List[Dict[str, Any]]]
    ) -> Optional[Dict[str, Any]]:
        """
        Use skill-creator to analyze multiple conversation histories and create a new skill.

        Args:
            conversation_list: List of conversation history
        
        Returns:
            Dict: Skill creation result or None if failed
        """        
        print(f"\n{'='*30}")
        print(f"Attempting to create skill from {len(conversation_list)} conversation(s)...")
        
        histories = []
        for i, conversation in enumerate(conversation_list):
            to_string = json.dumps(conversation, indent=2, ensure_ascii=False)
            histories.append(f"conversation {i + 1}:\n{to_string}")

        all_histories = "\n---\n".join(histories)
        
        skill_creation_prompt = AGGREGATE_SKILL_CREATION_PROMPT.format(all_histories=all_histories)
        try:
            result = await self.answer(skill_creation_prompt)

            stop_reason = result["response"].stop_reason
            success = (stop_reason == "end_turn")
            if not success:
                print(f"\n\nSkill creation did not complete successfully. Stop reason: {stop_reason}")

            return {
                "success": success,
                "stop_reason": stop_reason
            }
            
        except Exception as e:
            print(f"\n\nError during skill creation: {e}")
            return {
                "success": False,
                "error": str(e)
            }


    # ------------------------------
    # Get statistics
    # ------------------------------
    def get_usage_stats(
        self
    ) -> Dict[str, Any]:
        """
        Calculate and return usage statistics from all API responses in the conversation.
        
        Returns:
            Dict: Conversation usage statistics including token usage and tool calls
        """
        if not self.api_responses:
            return {
                "stop_reason": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_server_tool_uses": 0,
                "total_tool_calls": 0,
                "api_call_count": 0
            }
        
        # Get the last stop_reason
        last_stop_reason = getattr(self.api_responses[-1], "stop_reason", None)
        
        total_input = 0
        total_output = 0
        total_server_tool_uses = 0
        total_tool_calls = 0
        
        for response in self.api_responses:
            # Sum up token usage
            if hasattr(response, "usage"):
                total_input += getattr(response.usage, "input_tokens", 0)
                total_output += getattr(response.usage, "output_tokens", 0)
            
            # Count tool calls in this response
            for item in response.content:
                if getattr(item, "type", None) == "server_tool_use":
                    total_server_tool_uses += 1
                
                elif getattr(item, "type", None) == "tool_use":
                    total_tool_calls += 1
        
        return {
            "stop_reason": last_stop_reason,
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_server_tool_uses": total_server_tool_uses, 
            "total_tool_calls": total_tool_calls,
            "api_call_count": len(self.api_responses),
        }

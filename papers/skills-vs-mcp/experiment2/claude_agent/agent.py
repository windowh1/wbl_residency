from anthropic import AsyncAnthropic
from typing import List, Dict, Optional, Any

from .mcp_client import MCPClient


class ClaudeAgent:
    """
    Agent class that integrates the Claude API with MCP servers.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4096,
        temperature: float = 1.0,
        betas: Optional[List[str]] = None,
        skills: Optional[List[Dict[str, Any]]] = None,
        configured_tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize a ClaudeAgent instance.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum number of tokens
            temperature: Generation temperature (0.0 - 1.0)
            betas: Beta features to enable
            skills: Skills to use (for Skills API)
            configured_tools: Tools from config (e.g., code_execution)
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.betas = betas or []
        self.skills = skills or []
        self.configured_tools = configured_tools or []
        self.mcp_tools = []  # Tools from MCP servers

        self.messages = []
        self.mcp_clients = {}

        # Store all API responses for usage statistics tracking
        self.api_responses = []  


    async def add_mcp(
        self, 
        name: str, 
        command: str, 
        args: Optional[List[str]] = None, 
        env: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Register and connect to an MCP server.

        Args:
            name: MCP server name
            command: Command to execute
            args: Command arguments list
            env: Environment variables dictionary

        Returns:
            bool: Server connection success status
        """
        # Create an MCPClient instance
        client = MCPClient(name, command, args, env)
        
        try:
            # Connect to MCP server
            await client.connect()
            self.mcp_clients[name] = client

            # Add MCP tools to the tool list
            self.mcp_tools.extend(client.tools)

            return True
        
        except Exception as e:
            print(f"[{name}] Failed to connect to server: {e}")
            return False


    async def disconnect_all_mcp(self):
        """
        Disconnect from all connected MCP servers.
        """
        for name, client in self.mcp_clients.items():
            try:
                await client.disconnect()
            except Exception as e:
                print(f"[{name}] Warning while disconnecting: {e}")
        self.mcp_clients.clear()


    async def execute_mcp_tool(
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
        
        # Execute tool and return result
        return await client.call_tool(tool_name, tool_input)


    def extract_text(
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


    def extract_server_tool_use(
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


    def extract_tool_calls(
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
    

    def add_message(
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
            if hasattr(content[0], 'model_dump'):
                content = [block.model_dump() for block in content]
        
        self.messages.append({
            "role": role,
            "content": content
        })


    async def answer(
        self, 
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the Claude API and generate a response.

        Args:
            message: User input message

        Returns:
            Dict:
                - response: Claude API response
                - text: Text extracted from Claude API response
                - tool_calls: Tool call list extracted from Claude API response
        """
        if message:
            self.add_message("user", message)

        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": self.messages,
            "system": "You are a helpful AI assistant.",
        }

        # Add betas if specified
        if self.betas:
            params["betas"] = self.betas

        # Add skills if specified (using container parameter for Skills API)
        if self.skills:
            params["container"] = {"skills": self.skills}

        # Combine configured tools with MCP tools
        all_tools = self.configured_tools + self.mcp_tools
        if len(all_tools) > 0:
            params["tools"] = all_tools

        try:
            response = await self.client.beta.messages.create(**params) if self.betas or self.skills \
                else await self.client.messages.create(**params)

        except Exception as e:
            raise RuntimeError(f"Failed to call Claude API: {e}")
            
        # Print response
        text_part = self.extract_text(response)
        print(f"\n{'='*30}")
        print(f"Claude:\n{text_part}")

        # Print server tool use information
        server_tool_use = self.extract_server_tool_use(response)
        
        for use in server_tool_use:
            name = use["name"]
            input = str(use.get("input", ""))
            print(f"\n{'-'*30}")
            print(f"Server tool use:\n{name} (input: {input[:150]}{'...' if len(input) > 150 else ''})")
            if "result" in use:
                print(f"\nTool result:\n{str(use['result'])[:150]}{'...' if len(str(use['result'])) > 150 else ''}")

        self.api_responses.append(response)
        self.add_message("assistant", response.content)

        return {
            "response": response,
            "text": text_part,
            "tool_calls": self.extract_tool_calls(response)
        }


    async def answer_with_mcp(
        self, 
        message: str, 
        max_iterations: int = 35
    ) -> Dict[str, Any]:
        """
        Automatically handle MCP tool calls during a conversation with Claude.

        Args:
            message: User input message
            max_iterations: Maximum number of tool execution iterations

        Returns:
            Dict: Final response
        """
        if not self.mcp_clients:
            return await self.answer(message)

        result = await self.answer(message)
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

                print(f"\n{'-'*30}")
                print(f"Local tool use:\n{tool_name} (input: {tool_input})")

                try:
                    tool_result = await self.execute_mcp_tool(tool_name, tool_input)
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

            self.add_message("user", tool_results)
            result = await self.answer()
            iteration += 1

        if iteration >= max_iterations and result["tool_calls"]:
            print(f"Reached maximum iterations ({max_iterations}) and response generation stopped. Some tool calls may remain.")

        return result
    
    
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
        last_stop_reason = getattr(self.api_responses[-1], 'stop_reason', None)
        
        total_input = 0
        total_output = 0
        total_server_tool_uses = 0
        total_tool_calls = 0
        
        for response in self.api_responses:
            # Sum up token usage
            if hasattr(response, 'usage'):
                total_input += getattr(response.usage, 'input_tokens', 0)
                total_output += getattr(response.usage, 'output_tokens', 0)
            
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

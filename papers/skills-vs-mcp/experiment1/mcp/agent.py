from anthropic import AsyncAnthropic
from typing import List, Dict, Optional, Any

from mcp_client import MCPClient

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
    ):
        """
        Initialize a ClaudeAgent instance.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum number of tokens
            temperature: Generation temperature (0.0 - 1.0)
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        self.conversation_history = []
        self.mcp_clients = {}
        self.global_tools = []
        
        # Metrics tracking
        self.api_responses = []  # Store all API responses for metrics


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

            # Update the global tool list
            self.global_tools.extend(client.tools)

            return True
        
        except Exception as e:
            print(f"[{name}] 서버와 연결을 실패했습니다: {e}")
            return False


    async def disconnect_all_mcp(self):
        """
        Disconnect from all connected MCP servers.
        """
        for name, client in self.mcp_clients.items():
            try:
                await client.disconnect()
            except Exception as e:
                print(f"[{name}] 서버와 연결 종료 중 경고가 발생했습니다: {e}")
        self.mcp_clients.clear()


    async def execute_mcp_tool(
        self, 
        mcp_tool_name: str, 
        tool_input: Dict[str, Any]
    ) -> str:
        """
        Locate and execute the specified MCP tool.

        Args:
            mcp_tool_name: Tool name in the format "server_name___tool_name"
            tool_input: Input data for the tool

        Returns:
            str: Tool execution result
        """
        parts = mcp_tool_name.split("___", 1)
        if len(parts) != 2:
            raise RuntimeError(f"잘못된 도구 이름 형식입니다: {mcp_tool_name}")

        server_name, tool_name = parts
        client = self.mcp_clients.get(server_name)
        if not client:
            raise RuntimeError(f"[{server_name}] 서버가 존재하지 않습니다.")
        
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
        Add a new message to conversation history.

        Args:
            role: Message role ("user" or "assistant")
            content: Message content
        """
        self.conversation_history.append({"role": role, "content": content})


    async def chat(
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
            "messages": self.conversation_history,
            "system": "당신은 도움이 되는 AI 어시스턴트입니다.",
        }
        
        if self.global_tools:
            params["tools"] = self.global_tools

        try:
            response = await self.client.messages.create(**params)
        except Exception as e:
            raise RuntimeError(f"Claude API 호출에 실패했습니다: {e}")

        # Store response for metrics
        self.api_responses.append(response)
        
        self.add_message("assistant", response.content)

        return {
            "response": response,
            "text": self.extract_text(response),
            "tool_calls": self.extract_tool_calls(response)
        }


    async def chat_with_mcp(
        self, 
        message: str, 
        max_iterations: int = 100
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
            print("연결된 MCP 서버가 없습니다. 기본 채팅 모드로 진행합니다.")
            return await self.chat(message)

        result = await self.chat(message)
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

                print(f"도구 실행: {tool_name} (input: {tool_input})")

                try:
                    tool_result = await self.execute_mcp_tool(tool_name, tool_input)
                    print(f"도구 결과: {tool_result}")

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": [{"type": "text", "text": str(tool_result)}],
                        }
                    )

                except Exception as e:
                    print(f"도구 실행에 실패했습니다: {e}")
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                            "is_error": True,
                        }
                    )

            self.add_message("user", tool_results)
            result = await self.chat()
            iteration += 1

        if iteration >= max_iterations and result["tool_calls"]:
            print(f"최대 반복 횟수({max_iterations})에 도달하여 응답 생성이 중단되었습니다. 도구 호출이 남아있을 수 있습니다.")

        return result
    
    
    def get_metrics(
        self
    ) -> Dict[str, Any]:
        """
        Calculate and return metrics from all API responses in the conversation.
        
        Returns:
            Dict: Conversation metrics including token usage and tool calls
        """
        if not self.api_responses:
            return {
                "stop_reason": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tool_calls": 0,
                "api_call_count": 0
            }
        
        # Get the last stop_reason
        last_stop_reason = getattr(self.api_responses[-1], 'stop_reason', None)
        
        total_input = 0
        total_output = 0
        total_tool_calls = 0
        
        for response in self.api_responses:
            # Sum up token usage
            if hasattr(response, 'usage'):
                total_input += getattr(response.usage, 'input_tokens', 0)
                total_output += getattr(response.usage, 'output_tokens', 0)
            
            # Count tool calls in this response
            for item in response.content:
                if getattr(item, "type", None) == "tool_use":
                    total_tool_calls += 1
        
        return {
            "stop_reason": last_stop_reason,
            "input_tokens": total_input,
            "output_tokens": total_output,
            "total_tool_calls": total_tool_calls,
            "api_call_count": len(self.api_responses),
        }
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import List, Dict, Optional, Any

class MCPClient:
    """
    Class for managing a single MCP server.
    """

    def __init__(
        self, 
        name: str, 
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ):
        """
        Initialize an MCPClient instance.

        Args:
            name: MCP server name
            command: Command to execute
            args: Command arguments list
            env: Environment variables dictionary
        """        
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}

        self.session = None
        self.tools = []

        # Internal state for managing MCP server lifecycle (connect to disconnect)
        self._task = None               # Runner task responsible for connection execution and termination
        self._ready = asyncio.Event()   # Connection completion signal
        self._close = asyncio.Event()   # Termination request signal
        self._runner_exc = None         # Exception occurred during runner execution


    async def _runner(self):
        """
        Manage the full lifecycle of an MCP server (from connection to disconnection).
        """
        params = StdioServerParameters(command=self.command, args=self.args, env=self.env)

        try:
            # Launch the MCP server process and establish the stdio stream
            async with stdio_client(params) as (stdio, write):
                # Start the protocol session context
                async with ClientSession(stdio, write) as session:
                    self.session = session
                    await session.initialize()

                    # Collect tool list
                    tools_list = await session.list_tools()
                    # Convert tool metadata into a Claude API–compatible format
                    self.tools = [
                        {
                            "name": f"{self.name}___{tool.name}",
                            "description": tool.description or "",
                            "input_schema": tool.inputSchema,
                        }
                        for tool in tools_list.tools
                    ]
                    print(f"[{self.name}] 서버와 연결을 완료했습니다. {len(self.tools)}개의 도구가 추가되었습니다.")

                    # Send connection completion signal to connect
                    self._ready.set()
                    # Wait for termination request signal from disconnect
                    await self._close.wait()

        except BaseException as e:
            # Store the exception to propagate it to connect()
            self._runner_exc = e
            self._ready.set()  # Release connect wait
            raise
        finally:
            self.session = None


    async def connect(self):
        """
        Start connection to MCP server.
        """
        # Skip if already connected
        if self._task and not self._task.done():
            return

        # Initialize state
        self._ready.clear()
        self._close.clear()
        self._runner_exc = None

        # Create task
        self._task = asyncio.create_task(self._runner(), name=f"mcp-runner:{self.name}")

        # Wait for connection completion
        await self._ready.wait()

        # Raise if exception occurred during connection
        if self._runner_exc:
            exc = self._runner_exc
            self._runner_exc = None
            self._task = None
            raise exc


    async def disconnect(self):
        """
        Terminate connection to MCP server.
        """
        if not self._task:
            print(f"[{self.name}] 서버와 연결이 이미 종료되었습니다.")
            return

        # Send termination request signal to runner
        self._close.set()
        try:
            # Ensure graceful termination using asyncio.shield to avoid task cancellation
            await asyncio.shield(self._task)
            print(f"[{self.name}] 서버와 연결이 종료되었습니다.")
        finally:
            self._task = None
            self.session = None


    async def call_tool(
        self, 
        tool_name: str, 
        tool_input: Dict[str, Any]
    ) -> str:
        """
        Execute the specified MCP tool and return its result as a string.

        Args:
            tool_name: MCP tool name to execute
            tool_input: Input data for the tool

        Returns:
            str: Tool execution result

        """
        if not self.session:
            raise RuntimeError(f"[{self.name}] 서버와 연결되지 않았습니다.")

        # Execute tool
        tool_result = await self.session.call_tool(tool_name, tool_input)

        # Parse and return result as string
        if hasattr(tool_result, "content"):
            if isinstance(tool_result.content, list):
                text_parts = []
                for item in tool_result.content:
                    text = getattr(item, "text", None)
                    if isinstance(text, str):
                        text_parts.append(text)
                return "\n".join(text_parts)
            text = getattr(tool_result.content, "text", None)
            if isinstance(text, str):
                return text

        return json.dumps(tool_result, default=str)

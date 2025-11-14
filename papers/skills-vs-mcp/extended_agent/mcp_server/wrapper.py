import argparse
import atexit
import asyncio
import json
import io
import os
import sys
import textwrap
import warnings
from io import StringIO
from typing import Any, Dict, List, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.stdio import StdioServerParameters, stdio_client


# Templates for HTTP MCP tool wrappers
TEMPLATE_MODULE_HTTP = '''"""
Auto-generated MCP tool wrapper for {tool_id}
Server: {server_name}
Description: {description}
Input Schema:
{input_schema}
"""

import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

_SERVER_URL = "{server_url}"

async def {func_name}(input: dict):
    """
    Auto-generated function calling MCP tool '{tool_id}' on server '{server_name}'.
    """
    async with streamablehttp_client(_SERVER_URL) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("{tool_id}", input)

    if hasattr(result, "content"):
        if isinstance(result.content, list):
            texts = [getattr(item, "text", "") for item in result.content if hasattr(item, "text")]
            return "\\n".join(texts)
        if hasattr(result.content, "text"):
            return result.content.text
    return str(result)
'''


# Templates for stdio MCP tool wrappers
TEMPLATE_MODULE_STDIO = '''"""
Auto-generated MCP tool wrapper for {tool_id}
Server: {server_name}
Description: {description}
Input Schema:
{input_schema}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "{proxy_url}"
SERVER_NAME = "{server_name}"
TOOL_NAME = "{tool_id}"

async def {func_name}(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool '{tool_id}' on server '{server_name}'.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{{PROXY_URL}}/mcp/{{SERVER_NAME}}/call_tool",
                params={{"tool_name": TOOL_NAME}},
                json=params
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result.get("result", "")
            else:
                raise RuntimeError(f"Tool call failed: {{result}}")
                
        except httpx.TimeoutException:
            raise RuntimeError(f"Timeout calling {{TOOL_NAME}}")
        except httpx.HTTPError as e:
            raise RuntimeError(f"HTTP error calling {{TOOL_NAME}}: {{e}}")
'''


class FilteredStderr:
    """
    Filter stderr to suppress specific unwanted messages.
    """
    
    def __init__(self):
        self.original_stderr = sys.stderr
        self.buffer = StringIO()


    def write(self, text):
        """
        Filter out unwanted messages.
        """
        if "Exception ignored in:" in text or \
           "BaseSubprocessTransport.__del__" in text or \
           "RuntimeError: Event loop is closed" in text or \
           "proto.pipe.close()" in text or \
           "self._loop.call_soon" in text or \
           "self._check_closed()" in text or \
           "self._close(None)" in text or \
           "asyncio/base_subprocess.py" in text or \
           "asyncio/base_events.py" in text or \
           "asyncio/unix_events.py" in text:
            return
        self.original_stderr.write(text)


    def flush(self):
        self.original_stderr.flush()


    def __enter__(self):
        sys.stderr = self
        return self


    def __exit__(self, *_):
        sys.stderr = self.original_stderr
        return False


async def mcp_discover_tools_http(
    server_url: str
) -> List[Dict[str, Any]]:
    """
    Discover MCP tools via HTTP transport.

    Args:
        server_url: Base URL of the HTTP MCP server

    Returns:
        List: Tool definitions with id, description, and inputSchema
    """
    print(f"Connecting to HTTP server: {server_url}")

    async with streamablehttp_client(server_url) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Found {len(tools.tools)} tools.\n")
            print(f"Successfully retrieved {len(tools.tools)} tools.")            
            return [
                {
                    "id": t.name,
                    "description": t.description or "",
                    "inputSchema": getattr(t, "inputSchema", None),
                }
                for t in tools.tools
            ]


async def mcp_discover_tools_stdio(
    command: str,
    args: List,
    env: Dict
) -> List[Dict[str, Any]]:
    """
    Discover MCP tools via stdio transport.

    Args:
        command: Command to start the MCP server (e.g., "npx", "node", "python")
        args: Arguments for the command
        env: Environment variables

    Returns:
        List: Tool definitions with id, description, and inputSchema
    """
    print(f"Launching stdio server: {command} {' '.join(args)}")

    params = StdioServerParameters(command=command, args=args, env=env)
    result_container = []

    async def discover():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print(f"Found {len(tools.tools)} tools.\n")

                tools_list = [
                    {
                        "id": t.name,
                        "description": t.description or "",
                        "inputSchema": getattr(t, "inputSchema", None),
                    }
                    for t in tools.tools
                ]
                result_container.extend(tools_list)

                print("Attempting to close connection gracefully...")
                return tools_list

    try:
        result = await asyncio.wait_for(discover(), timeout=30)
        print(f"Successfully retrieved {len(result)} tools.")
        return result

    except asyncio.TimeoutError:
        print("Timeout waiting for graceful shutdown (this is expected for some servers).")

        if result_container:
            print(f"Returning {len(result_container)} tools retrieved before timeout.")
            return result_container
        else:
            print("No tools were retrieved before timeout.")
            return []

    except Exception as e:
        error_type = type(e).__name__

        if "ExceptionGroup" in error_type or "BrokenResourceError" in str(e):
            print(f"Expected shutdown error (server doesn't support graceful close).")
        else:
            print(f"Unexpected error: {error_type}: {e}")
            import traceback
            traceback.print_exc()

        if result_container:
            print(f"Successfully retrieved {len(result_container)} tools (server closed ungracefully).")
            return result_container
        return []


def generate_wrappers_sync(
    transport: str,
    out_dir: str,
    server_name: Optional[str],
    server_url: Optional[str] = None,
    command: Optional[str] = None,
    args: Optional[List] = None,
    env: Optional[Dict] = None,
    proxy_url: str = "http://localhost:8082"
) -> None:
    """
    Generate Python wrapper functions for all MCP server tools.

    Args:
        transport: Transport type ("http" or "stdio")
        out_dir: Output directory for generated wrappers
        server_name: Logical name for the server (used for directory naming)
        server_url: Base URL for HTTP transport (required if transport="http")
        command: Command to start stdio server (required if transport="stdio")
        args: Arguments for stdio command
        env: Environment variables for stdio command
        proxy_url: HTTP proxy URL for stdio servers (default: http://localhost:8082)
    """
    print("Starting wrapper generation...\n")

    server_name = server_name or "stdio_server"
    
    # Convert server_name to valid Python module name
    # Replace hyphens with underscores for directory/module naming
    module_name = server_name.replace("-", "_")
    
    if server_name != module_name:
        print(f"Note: Server name '{server_name}' converted to '{module_name}' for Python module compatibility\n")

    if transport == "http":
        tools = asyncio.run(mcp_discover_tools_http(server_url))
        template = TEMPLATE_MODULE_HTTP
    else:
        tools = asyncio.run(mcp_discover_tools_stdio(command, args or [], env or {}))
        template = TEMPLATE_MODULE_STDIO

    if not tools:
        raise RuntimeError("No tools discovered from the MCP server.")

    os.makedirs(out_dir, exist_ok=True)
    # Use module_name (with underscores) for directory
    server_dir = os.path.join(out_dir, module_name)
    os.makedirs(server_dir, exist_ok=True)

    print(f"\nGenerating wrappers for tools...\n")
    for idx, t in enumerate(tools, 1):
        print(f"    - Tool {idx}/{len(tools)}: {t['id']}")
        
        tool_id = t["id"]
        description = textwrap.dedent(t.get("description", "")).strip()
        input_schema = t.get("inputSchema") or {
            "type": "object",
            "properties": {},
            "required": []
        }
        input_schema_formatted = json.dumps(input_schema, indent=2)
        
        func_name = tool_id.replace("-", "_")

        # Generate wrapper based on transport type
        if transport == "http":
            content = template.format(
                tool_id=tool_id,
                server_url=server_url,
                description=description.replace('"', '\\"'),
                func_name=func_name,
                input_schema=input_schema_formatted,
                server_name=server_name  # Keep original name for documentation
            )
        else:  # stdio -> use HTTP proxy
            content = template.format(
                tool_id=tool_id,
                proxy_url=proxy_url,
                server_name=server_name,  # Use original name for HTTP proxy endpoint
                description=description.replace('"', '\\"'),
                func_name=func_name,
                input_schema=input_schema_formatted
            )

        fname = os.path.join(server_dir, f"{func_name}.py")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      Generated wrapper: {fname}\n")

    # Create __init__.py to import all tools
    with open(os.path.join(server_dir, "__init__.py"), "w", encoding="utf-8") as f:
        for f_ in os.listdir(server_dir):
            if f_.endswith(".py") and f_ != "__init__.py":
                mod = f_[:-3]
                f.write(f"from .{mod} import {mod}\n")

    print(f"All wrappers written to {server_dir}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-name", help="MCP server name")
    parser.add_argument("--transport", choices=["http", "stdio"], required=True, help="Transport type (http or stdio)")
    parser.add_argument("--server-url", help="HTTP MCP server base URL (e.g. http://localhost:8081/mcp)")
    parser.add_argument("--command", help="Command to start the stdio MCP server")
    parser.add_argument("--args", type=json.loads, default="[]", help="Arguments for stdio server as JSON list")
    parser.add_argument("--env", type=json.loads, default=None, help='Additional environment variables as JSON (e.g. \'{"API_KEY": "xxx"}\')')
    parser.add_argument("--out", default="extensions/wrapped_mcp", help="Output directory")
    parser.add_argument("--proxy-url", default="http://localhost:8082", help="HTTP proxy URL for stdio servers (default: http://localhost:8082)")
    args = parser.parse_args()

    # Validation
    if args.transport == "http":
        if not args.server_url:
            parser.error("--server-url is required when --transport is http")
    elif args.transport == "stdio":
        if not args.command:
            parser.error("--command is required when --transport is stdio")

    env = os.environ.copy()
    if args.env:
        env.update(args.env)

    # Suppress ResourceWarning for unclosed subprocess pipes
    warnings.filterwarnings("ignore", category=ResourceWarning)

    # Suppress asyncio cleanup warnings that happen during interpreter shutdown
    def suppress_final_errors():
        """
        Redirect stderr to devnull to suppress final cleanup errors.
        """
        sys.stderr = io.open(os.devnull, 'w')
    atexit.register(suppress_final_errors)

    # Use filtered stderr to suppress asyncio cleanup warnings
    with FilteredStderr():
        generate_wrappers_sync(
            args.transport,
            args.out,
            args.server_name,
            args.server_url,
            args.command,
            args.args,
            env,
            args.proxy_url
        )
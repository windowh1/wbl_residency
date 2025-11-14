"""
Auto-generated MCP tool wrapper for get_config
Server: desktop-commander
Description: Get the complete server configuration as JSON. Config includes fields for:
- blockedCommands (array of blocked shell commands)
- defaultShell (shell to use for commands)
- allowedDirectories (paths the server can access)
- fileReadLineLimit (max lines for read_file, default 1000)
- fileWriteLineLimit (max lines per write_file call, default 50)
- telemetryEnabled (boolean for telemetry opt-in/out)
- currentClient (information about the currently connected MCP client)
- clientHistory (history of all clients that have connected)
- version (version of the DesktopCommander)
- systemInfo (operating system and environment details)
This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {},
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "get_config"

async def get_config(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'get_config' on server 'desktop-commander'.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{PROXY_URL}/mcp/{SERVER_NAME}/call_tool",
                params={"tool_name": TOOL_NAME},
                json=params
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result.get("result", "")
            else:
                raise RuntimeError(f"Tool call failed: {result}")
                
        except httpx.TimeoutException:
            raise RuntimeError(f"Timeout calling {TOOL_NAME}")
        except httpx.HTTPError as e:
            raise RuntimeError(f"HTTP error calling {TOOL_NAME}: {e}")

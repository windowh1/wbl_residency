"""
Auto-generated MCP tool wrapper for kill_process
Server: desktop-commander
Description: Terminate a running process by PID.

Use with caution as this will forcefully terminate the specified process.

This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "pid": {
      "type": "number"
    }
  },
  "required": [
    "pid"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "kill_process"

async def kill_process(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'kill_process' on server 'desktop-commander'.
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

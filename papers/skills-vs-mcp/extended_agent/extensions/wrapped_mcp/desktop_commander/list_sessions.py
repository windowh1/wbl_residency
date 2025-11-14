"""
Auto-generated MCP tool wrapper for list_sessions
Server: desktop-commander
Description: List all active terminal sessions.

Shows session status including:
- PID: Process identifier  
- Blocked: Whether session is waiting for input
- Runtime: How long the session has been running

DEBUGGING REPLs:
- \"Blocked: true\" often means REPL is waiting for input
- Use this to verify sessions are running before sending input
- Long runtime with blocked status may indicate stuck process

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
TOOL_NAME = "list_sessions"

async def list_sessions(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'list_sessions' on server 'desktop-commander'.
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

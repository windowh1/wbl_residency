"""
Auto-generated MCP tool wrapper for get_recent_tool_calls
Server: desktop-commander
Description: Get recent tool call history with their arguments and outputs.
Returns chronological list of tool calls made during this session.

Useful for:
- Onboarding new chats about work already done
- Recovering context after chat history loss
- Debugging tool call sequences

Note: Does not track its own calls or other meta/query tools.
History kept in memory (last 1000 calls, lost on restart).

This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "maxResults": {
      "type": "number",
      "minimum": 1,
      "maximum": 1000,
      "default": 50
    },
    "toolName": {
      "type": "string"
    },
    "since": {
      "type": "string",
      "format": "date-time"
    }
  },
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "get_recent_tool_calls"

async def get_recent_tool_calls(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'get_recent_tool_calls' on server 'desktop-commander'.
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

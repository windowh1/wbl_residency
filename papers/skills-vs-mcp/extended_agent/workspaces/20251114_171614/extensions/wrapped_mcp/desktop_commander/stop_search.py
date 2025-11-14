"""
Auto-generated MCP tool wrapper for stop_search
Server: desktop-commander
Description: Stop an active search.

Stops the background search process gracefully. Use this when you've found
what you need or if a search is taking too long. Similar to force_terminate
for terminal processes.

The search will still be available for reading final results until it's
automatically cleaned up after 5 minutes.

This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "sessionId": {
      "type": "string"
    }
  },
  "required": [
    "sessionId"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "stop_search"

async def stop_search(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'stop_search' on server 'desktop-commander'.
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

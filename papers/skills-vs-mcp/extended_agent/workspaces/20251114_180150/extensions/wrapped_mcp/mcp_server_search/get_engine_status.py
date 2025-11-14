"""
Auto-generated MCP tool wrapper for get_engine_status
Server: mcp-server-search
Description: Get search engine status.

Returns:
    Search engine status
Input Schema:
{
  "properties": {},
  "title": "get_engine_statusArguments",
  "type": "object"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "mcp-server-search"
TOOL_NAME = "get_engine_status"

async def get_engine_status(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'get_engine_status' on server 'mcp-server-search'.
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

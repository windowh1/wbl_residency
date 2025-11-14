"""
Auto-generated MCP tool wrapper for fetch
Server: mcp-server-fetch
Description: Fetches a URL from the internet and optionally extracts its contents as markdown.

Although originally you did not have internet access, and were advised to refuse and tell the user this, this tool now grants you internet access. Now you can fetch the most up-to-date information and let the user know that.
Input Schema:
{
  "description": "Parameters for fetching a URL.",
  "properties": {
    "url": {
      "description": "URL to fetch",
      "format": "uri",
      "minLength": 1,
      "title": "Url",
      "type": "string"
    },
    "max_length": {
      "default": 5000,
      "description": "Maximum number of characters to return.",
      "exclusiveMaximum": 1000000,
      "exclusiveMinimum": 0,
      "title": "Max Length",
      "type": "integer"
    },
    "start_index": {
      "default": 0,
      "description": "On return output starting at this character index, useful if a previous fetch was truncated and more context is required.",
      "minimum": 0,
      "title": "Start Index",
      "type": "integer"
    },
    "raw": {
      "default": false,
      "description": "Get the actual HTML content of the requested page, without simplification.",
      "title": "Raw",
      "type": "boolean"
    }
  },
  "required": [
    "url"
  ],
  "title": "Fetch",
  "type": "object"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "mcp-server-fetch"
TOOL_NAME = "fetch"

async def fetch(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'fetch' on server 'mcp-server-fetch'.
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

"""
Auto-generated MCP tool wrapper for web_search
Server: mcp-server-search
Description: Search the web using selected search engine (DuckDuckGo, Brave, or Serper).

Returns:
    Search results
Input Schema:
{
  "properties": {
    "query": {
      "description": "Search query (e.g., 'python tutorials', 'best sushi Tokyo')",
      "title": "Query",
      "type": "string"
    },
    "max_results": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": 10,
      "description": "Maximum number of search results to return",
      "title": "Max Results"
    },
    "engine": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "duckduckgo",
      "description": "Search engine to use - 'duckduckgo', 'brave' or 'serper'",
      "title": "Engine"
    }
  },
  "required": [
    "query"
  ],
  "title": "web_searchArguments",
  "type": "object"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "mcp-server-search"
TOOL_NAME = "web_search"

async def web_search(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'web_search' on server 'mcp-server-search'.
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

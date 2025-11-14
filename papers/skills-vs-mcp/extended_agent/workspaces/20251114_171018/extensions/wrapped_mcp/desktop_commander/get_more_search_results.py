"""
Auto-generated MCP tool wrapper for get_more_search_results
Server: desktop-commander
Description: Get more results from an active search with offset-based pagination.

Supports partial result reading with:
- 'offset' (start result index, default: 0)
  * Positive: Start from result N (0-based indexing)
  * Negative: Read last N results from end (tail behavior)
- 'length' (max results to read, default: 100)
  * Used with positive offsets for range reading
  * Ignored when offset is negative (reads all requested tail results)

Examples:
- offset: 0, length: 100     → First 100 results
- offset: 200, length: 50    → Results 200-249
- offset: -20                → Last 20 results
- offset: -5, length: 10     → Last 5 results (length ignored)

Returns only results in the specified range, along with search status.
Works like read_process_output - call this repeatedly to get progressive
results from a search started with start_search.

This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "sessionId": {
      "type": "string"
    },
    "offset": {
      "type": "number",
      "default": 0
    },
    "length": {
      "type": "number",
      "default": 100
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
TOOL_NAME = "get_more_search_results"

async def get_more_search_results(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'get_more_search_results' on server 'desktop-commander'.
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

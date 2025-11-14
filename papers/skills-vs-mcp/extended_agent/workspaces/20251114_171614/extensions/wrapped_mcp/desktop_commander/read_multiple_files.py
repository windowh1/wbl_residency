"""
Auto-generated MCP tool wrapper for read_multiple_files
Server: desktop-commander
Description: Read the contents of multiple files simultaneously.

Each file's content is returned with its path as a reference.
Handles text files normally and renders images as viewable content.
Recognized image types: PNG, JPEG, GIF, WebP.

Failed reads for individual files won't stop the entire operation.
Only works within allowed directories.

IMPORTANT: Always use absolute paths for reliability. Paths are automatically normalized regardless of slash direction. Relative paths may fail as they depend on the current working directory. Tilde paths (~/...) might not work in all contexts. Unless the user explicitly asks for relative paths, use absolute paths.
This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "paths": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "paths"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "read_multiple_files"

async def read_multiple_files(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'read_multiple_files' on server 'desktop-commander'.
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

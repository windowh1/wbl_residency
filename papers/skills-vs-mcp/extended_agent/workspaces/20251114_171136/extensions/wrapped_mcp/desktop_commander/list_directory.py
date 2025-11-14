"""
Auto-generated MCP tool wrapper for list_directory
Server: desktop-commander
Description: Get a detailed listing of all files and directories in a specified path.

Use this instead of 'execute_command' with ls/dir commands.
Results distinguish between files and directories with [FILE] and [DIR] prefixes.

Supports recursive listing with the 'depth' parameter (default: 2):
- depth=1: Only direct contents of the directory
- depth=2: Contents plus one level of subdirectories
- depth=3+: Multiple levels deep

CONTEXT OVERFLOW PROTECTION:
- Top-level directory shows ALL items
- Nested directories are limited to 100 items maximum per directory
- When a nested directory has more than 100 items, you'll see a warning like:
  [WARNING] node_modules: 500 items hidden (showing first 100 of 600 total)
- This prevents overwhelming the context with large directories like node_modules

Results show full relative paths from the root directory being listed.
Example output with depth=2:
[DIR] src
[FILE] src/index.ts
[DIR] src/tools
[FILE] src/tools/filesystem.ts

If a directory cannot be accessed, it will show [DENIED] instead.
Only works within allowed directories.

IMPORTANT: Always use absolute paths for reliability. Paths are automatically normalized regardless of slash direction. Relative paths may fail as they depend on the current working directory. Tilde paths (~/...) might not work in all contexts. Unless the user explicitly asks for relative paths, use absolute paths.
This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "path": {
      "type": "string"
    },
    "depth": {
      "type": "number",
      "default": 2
    }
  },
  "required": [
    "path"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "list_directory"

async def list_directory(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'list_directory' on server 'desktop-commander'.
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

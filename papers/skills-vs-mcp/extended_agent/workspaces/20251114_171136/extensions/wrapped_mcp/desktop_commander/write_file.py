"""
Auto-generated MCP tool wrapper for write_file
Server: desktop-commander
Description: Write or append to file contents. 

CHUNKING IS STANDARD PRACTICE: Always write files in chunks of 25-30 lines maximum.
This is the normal, recommended way to write files - not an emergency measure.

STANDARD PROCESS FOR ANY FILE:
1. FIRST → write_file(filePath, firstChunk, {mode: 'rewrite'})  [≤30 lines]
2. THEN → write_file(filePath, secondChunk, {mode: 'append'})   [≤30 lines]
3. CONTINUE → write_file(filePath, nextChunk, {mode: 'append'}) [≤30 lines]

ALWAYS CHUNK PROACTIVELY - don't wait for performance warnings!

WHEN TO CHUNK (always be proactive):
1. Any file expected to be longer than 25-30 lines
2. When writing multiple files in sequence
3. When creating documentation, code files, or configuration files

HANDLING CONTINUATION (\"Continue\" prompts):
If user asks to \"Continue\" after an incomplete operation:
1. Read the file to see what was successfully written
2. Continue writing ONLY the remaining content using {mode: 'append'}
3. Keep chunks to 25-30 lines each

Files over 50 lines will generate performance notes but are still written successfully.
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
    "content": {
      "type": "string"
    },
    "mode": {
      "type": "string",
      "enum": [
        "rewrite",
        "append"
      ],
      "default": "rewrite"
    }
  },
  "required": [
    "path",
    "content"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "write_file"

async def write_file(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'write_file' on server 'desktop-commander'.
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

"""
Auto-generated MCP tool wrapper for edit_block
Server: desktop-commander
Description: Apply surgical text replacements to files.

BEST PRACTICE: Make multiple small, focused edits rather than one large edit.
Each edit_block call should change only what needs to be changed - include just enough 
context to uniquely identify the text being modified.

Takes:
- file_path: Path to the file to edit
- old_string: Text to replace
- new_string: Replacement text
- expected_replacements: Optional parameter for number of replacements

By default, replaces only ONE occurrence of the search text.
To replace multiple occurrences, provide the expected_replacements parameter with
the exact number of matches expected.

UNIQUENESS REQUIREMENT: When expected_replacements=1 (default), include the minimal
amount of context necessary (typically 1-3 lines) before and after the change point,
with exact whitespace and indentation.

When editing multiple sections, make separate edit_block calls for each distinct change
rather than one large replacement.

When a close but non-exact match is found, a character-level diff is shown in the format:
common_prefix{-removed-}{+added+}common_suffix to help you identify what's different.

Similar to write_file, there is a configurable line limit (fileWriteLineLimit) that warns
if the edited file exceeds this limit. If this happens, consider breaking your edits into
smaller, more focused changes.

IMPORTANT: Always use absolute paths for reliability. Paths are automatically normalized regardless of slash direction. Relative paths may fail as they depend on the current working directory. Tilde paths (~/...) might not work in all contexts. Unless the user explicitly asks for relative paths, use absolute paths.
This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "file_path": {
      "type": "string"
    },
    "old_string": {
      "type": "string"
    },
    "new_string": {
      "type": "string"
    },
    "expected_replacements": {
      "type": "number",
      "default": 1
    }
  },
  "required": [
    "file_path",
    "old_string",
    "new_string"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "edit_block"

async def edit_block(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'edit_block' on server 'desktop-commander'.
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

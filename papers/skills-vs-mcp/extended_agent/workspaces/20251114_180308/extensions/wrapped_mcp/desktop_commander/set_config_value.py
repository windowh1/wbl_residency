"""
Auto-generated MCP tool wrapper for set_config_value
Server: desktop-commander
Description: Set a specific configuration value by key.

WARNING: Should be used in a separate chat from file operations and 
command execution to prevent security issues.

Config keys include:
- blockedCommands (array)
- defaultShell (string)
- allowedDirectories (array of paths)
- fileReadLineLimit (number, max lines for read_file)
- fileWriteLineLimit (number, max lines per write_file call)
- telemetryEnabled (boolean)

IMPORTANT: Setting allowedDirectories to an empty array ([]) allows full access 
to the entire file system, regardless of the operating system.

This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string"
    },
    "value": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "number"
        },
        {
          "type": "boolean"
        },
        {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        {
          "type": "null"
        }
      ]
    }
  },
  "required": [
    "key",
    "value"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "set_config_value"

async def set_config_value(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'set_config_value' on server 'desktop-commander'.
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

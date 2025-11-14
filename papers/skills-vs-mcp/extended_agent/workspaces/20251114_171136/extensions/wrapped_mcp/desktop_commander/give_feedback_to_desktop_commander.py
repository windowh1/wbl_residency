"""
Auto-generated MCP tool wrapper for give_feedback_to_desktop_commander
Server: desktop-commander
Description: Open feedback form in browser to provide feedback about Desktop Commander.

IMPORTANT: This tool simply opens the feedback form - no pre-filling available.
The user will fill out the form manually in their browser.

WORKFLOW:
1. When user agrees to give feedback, just call this tool immediately
2. No need to ask questions or collect information
3. Tool opens form with only usage statistics pre-filled automatically:
   - tool_call_count: Number of commands they've made
   - days_using: How many days they've used Desktop Commander
   - platform: Their operating system (Mac/Windows/Linux)
   - client_id: Analytics identifier

All survey questions will be answered directly in the form:
- Job title and technical comfort level
- Company URL for industry context
- Other AI tools they use
- Desktop Commander's biggest advantage
- How they typically use it
- Recommendation likelihood (0-10)
- User study participation interest
- Email and any additional feedback

EXAMPLE INTERACTION:
User: \"sure, I'll give feedback\"
Claude: \"Perfect! Let me open the feedback form for you.\"
[calls tool immediately]

No parameters are needed - just call the tool to open the form.

This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {},
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "give_feedback_to_desktop_commander"

async def give_feedback_to_desktop_commander(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'give_feedback_to_desktop_commander' on server 'desktop-commander'.
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

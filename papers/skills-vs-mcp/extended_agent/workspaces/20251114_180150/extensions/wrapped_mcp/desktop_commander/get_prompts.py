"""
Auto-generated MCP tool wrapper for get_prompts
Server: desktop-commander
Description: Browse and retrieve curated Desktop Commander prompts for various tasks and workflows.

IMPORTANT: When displaying prompt lists to users, do NOT show the internal prompt IDs (like 'onb_001'). 
These IDs are for your reference only. Show users only the prompt titles and descriptions.
The IDs will be provided in the response metadata for your use.

DESKTOP COMMANDER INTRODUCTION: If a user asks \"what is Desktop Commander?\" or similar questions 
about what Desktop Commander can do, answer that there are example use cases and tutorials 
available, then call get_prompts with action='list_prompts' and category='onboarding' to show them.

ACTIONS:
- list_categories: Show all available prompt categories
- list_prompts: List prompts (optionally filtered by category)  
- get_prompt: Retrieve and execute a specific prompt by ID

WORKFLOW:
1. Use list_categories to see available categories
2. Use list_prompts to browse prompts in a category
3. Use get_prompt with promptId to retrieve and start using a prompt

EXAMPLES:
- get_prompts(action='list_categories') - See all categories
- get_prompts(action='list_prompts', category='onboarding') - See onboarding prompts
- get_prompts(action='get_prompt', promptId='onb_001') - Get a specific prompt

The get_prompt action will automatically inject the prompt content and begin execution.
Perfect for discovering proven workflows and getting started with Desktop Commander.

This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "list_categories",
        "list_prompts",
        "get_prompt"
      ]
    },
    "category": {
      "type": "string"
    },
    "promptId": {
      "type": "string"
    }
  },
  "required": [
    "action"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "get_prompts"

async def get_prompts(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'get_prompts' on server 'desktop-commander'.
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

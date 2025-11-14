"""
Auto-generated MCP tool wrapper for start_search
Server: desktop-commander
Description: Start a streaming search that can return results progressively.

SEARCH STRATEGY GUIDE:
Choose the right search type based on what the user is looking for:

USE searchType=\"files\" WHEN:
- User asks for specific files: \"find package.json\", \"locate config files\"
- Pattern looks like a filename: \"*.js\", \"README.md\", \"test-*.tsx\" 
- User wants to find files by name/extension: \"all TypeScript files\", \"Python scripts\"
- Looking for configuration/setup files: \".env\", \"dockerfile\", \"tsconfig.json\"

USE searchType=\"content\" WHEN:
- User asks about code/logic: \"authentication logic\", \"error handling\", \"API calls\"
- Looking for functions/variables: \"getUserData function\", \"useState hook\"
- Searching for text/comments: \"TODO items\", \"FIXME comments\", \"documentation\"
- Finding patterns in code: \"console.log statements\", \"import statements\"
- User describes functionality: \"components that handle login\", \"files with database queries\"

WHEN UNSURE OR USER REQUEST IS AMBIGUOUS:
Run TWO searches in parallel - one for files and one for content:

Example approach for ambiguous queries like \"find authentication stuff\":
1. Start file search: searchType=\"files\", pattern=\"auth\"
2. Simultaneously start content search: searchType=\"content\", pattern=\"authentication\"  
3. Present combined results: \"Found 3 auth-related files and 8 files containing authentication code\"

SEARCH TYPES:
- searchType=\"files\": Find files by name (pattern matches file names)
- searchType=\"content\": Search inside files for text patterns

PATTERN MATCHING MODES:
- Default (literalSearch=false): Patterns are treated as regular expressions
- Literal (literalSearch=true): Patterns are treated as exact strings

WHEN TO USE literalSearch=true:
Use literal search when searching for code patterns with special characters:
- Function calls with parentheses and quotes
- Array access with brackets
- Object methods with dots and parentheses
- File paths with backslashes
- Any pattern containing: . * + ? ^ $ { } [ ] | \ ( )

IMPORTANT PARAMETERS:
- pattern: What to search for (file names OR content text)
- literalSearch: Use exact string matching instead of regex (default: false)
- filePattern: Optional filter to limit search to specific file types (e.g., \"*.js\", \"package.json\")
- ignoreCase: Case-insensitive search (default: true). Works for both file names and content.
- earlyTermination: Stop search early when exact filename match is found (optional: defaults to true for file searches, false for content searches)

DECISION EXAMPLES:
- \"find package.json\" → searchType=\"files\", pattern=\"package.json\" (specific file)
- \"find authentication components\" → searchType=\"content\", pattern=\"authentication\" (looking for functionality)
- \"locate all React components\" → searchType=\"files\", pattern=\"*.tsx\" or \"*.jsx\" (file pattern)
- \"find TODO comments\" → searchType=\"content\", pattern=\"TODO\" (text in files)
- \"show me login files\" → AMBIGUOUS → run both: files with \"login\" AND content with \"login\"
- \"find config\" → AMBIGUOUS → run both: config files AND files containing config code

COMPREHENSIVE SEARCH EXAMPLES:
- Find package.json files: searchType=\"files\", pattern=\"package.json\"
- Find all JS files: searchType=\"files\", pattern=\"*.js\"
- Search for TODO in code: searchType=\"content\", pattern=\"TODO\", filePattern=\"*.js|*.ts\"
- Search for exact code: searchType=\"content\", pattern=\"toast.error('test')\", literalSearch=true
- Ambiguous request \"find auth stuff\": Run two searches:
  1. searchType=\"files\", pattern=\"auth\"
  2. searchType=\"content\", pattern=\"authentication\"

PRO TIP: When user requests are ambiguous about whether they want files or content,
run both searches concurrently and combine results for comprehensive coverage.

Unlike regular search tools, this starts a background search process and returns
immediately with a session ID. Use get_more_search_results to get results as they
come in, and stop_search to stop the search early if needed.

Perfect for large directories where you want to see results immediately and
have the option to cancel if the search takes too long or you find what you need.

IMPORTANT: Always use absolute paths for reliability. Paths are automatically normalized regardless of slash direction. Relative paths may fail as they depend on the current working directory. Tilde paths (~/...) might not work in all contexts. Unless the user explicitly asks for relative paths, use absolute paths.
This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "path": {
      "type": "string"
    },
    "pattern": {
      "type": "string"
    },
    "searchType": {
      "type": "string",
      "enum": [
        "files",
        "content"
      ],
      "default": "files"
    },
    "filePattern": {
      "type": "string"
    },
    "ignoreCase": {
      "type": "boolean",
      "default": true
    },
    "maxResults": {
      "type": "number"
    },
    "includeHidden": {
      "type": "boolean",
      "default": false
    },
    "contextLines": {
      "type": "number",
      "default": 5
    },
    "timeout_ms": {
      "type": "number"
    },
    "earlyTermination": {
      "type": "boolean"
    },
    "literalSearch": {
      "type": "boolean",
      "default": false
    }
  },
  "required": [
    "path",
    "pattern"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "start_search"

async def start_search(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'start_search' on server 'desktop-commander'.
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

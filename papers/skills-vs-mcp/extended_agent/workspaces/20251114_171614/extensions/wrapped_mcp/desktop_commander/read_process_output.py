"""
Auto-generated MCP tool wrapper for read_process_output
Server: desktop-commander
Description: Read output from a running process with intelligent completion detection.

Automatically detects when process is ready for more input instead of timing out.

SMART FEATURES:
- Early exit when REPL shows prompt (>>>, >, etc.)
- Detects process completion vs still running
- Prevents hanging on interactive prompts
- Clear status messages about process state

REPL USAGE:
- Stops immediately when REPL prompt detected
- Shows clear status: waiting for input vs finished
- Shorter timeouts needed due to smart detection
- Works with Python, Node.js, R, Julia, etc.

DETECTION STATES:
Process waiting for input (ready for interact_with_process)
Process finished execution
Timeout reached (may still be running)

PERFORMANCE DEBUGGING (verbose_timing parameter):
Set verbose_timing: true to get detailed timing information including:
- Exit reason (early_exit_quick_pattern, early_exit_periodic_check, process_finished, timeout)
- Total duration and time to first output
- Complete timeline of all output events with timestamps
- Which detection mechanism triggered early exit
Use this to identify when timeouts could be reduced or detection patterns improved.

This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "pid": {
      "type": "number"
    },
    "timeout_ms": {
      "type": "number"
    },
    "verbose_timing": {
      "type": "boolean"
    }
  },
  "required": [
    "pid"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "read_process_output"

async def read_process_output(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'read_process_output' on server 'desktop-commander'.
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

"""
Auto-generated MCP tool wrapper for interact_with_process
Server: desktop-commander
Description: Send input to a running process and automatically receive the response.

CRITICAL: THIS IS THE PRIMARY TOOL FOR ALL LOCAL FILE ANALYSIS
For ANY local file analysis (CSV, JSON, data processing), ALWAYS use this instead of the analysis tool.
The analysis tool CANNOT access local files and WILL FAIL - use processes for ALL file-based work.

FILE ANALYSIS PRIORITY ORDER (MANDATORY):
1. ALWAYS FIRST: Use this tool (start_process + interact_with_process) for local data analysis
2. ALTERNATIVE: Use command-line tools (cut, awk, grep) for quick processing  
3. NEVER EVER: Use analysis tool for local file access (IT WILL FAIL)

REQUIRED INTERACTIVE WORKFLOW FOR FILE ANALYSIS:
1. Start REPL: start_process(\"python3 -i\")
2. Load libraries: interact_with_process(pid, \"import pandas as pd, numpy as np\")
3. Read file: interact_with_process(pid, \"df = pd.read_csv('/absolute/path/file.csv')\")
4. Analyze: interact_with_process(pid, \"print(df.describe())\")
5. Continue: interact_with_process(pid, \"df.groupby('column').size()\")

BINARY FILE PROCESSING WORKFLOWS:
Use appropriate Python libraries (PyPDF2, pandas, docx2txt, etc.) or command-line tools for binary file analysis.

SMART DETECTION:
- Automatically waits for REPL prompt (>>>, >, etc.)
- Detects errors and completion states
- Early exit prevents timeout delays
- Clean output formatting (removes prompts)

SUPPORTED REPLs:
- Python: python3 -i (RECOMMENDED for data analysis)
- Node.js: node -i  
- R: R
- Julia: julia
- Shell: bash, zsh
- Database: mysql, postgres

PARAMETERS:
- pid: Process ID from start_process
- input: Code/command to execute
- timeout_ms: Max wait (default: 8000ms)
- wait_for_prompt: Auto-wait for response (default: true)
- verbose_timing: Enable detailed performance telemetry (default: false)

Returns execution result with status indicators.

PERFORMANCE DEBUGGING (verbose_timing parameter):
Set verbose_timing: true to get detailed timing information including:
- Exit reason (early_exit_quick_pattern, early_exit_periodic_check, process_finished, timeout, no_wait)
- Total duration and time to first output
- Complete timeline of all output events with timestamps
- Which detection mechanism triggered early exit
Use this to identify slow interactions and optimize detection patterns.

ALWAYS USE FOR: CSV analysis, JSON processing, file statistics, data visualization prep, ANY local file work
NEVER USE ANALYSIS TOOL FOR: Local file access (it cannot read files from disk and WILL FAIL)

This command can be referenced as \"DC: ...\" or \"use Desktop Commander to ...\" in your instructions.
Input Schema:
{
  "type": "object",
  "properties": {
    "pid": {
      "type": "number"
    },
    "input": {
      "type": "string"
    },
    "timeout_ms": {
      "type": "number"
    },
    "wait_for_prompt": {
      "type": "boolean"
    },
    "verbose_timing": {
      "type": "boolean"
    }
  },
  "required": [
    "pid",
    "input"
  ],
  "additionalProperties": false,
  "$schema": "http://json-schema.org/draft-07/schema#"
}
"""

import httpx
from typing import Dict, Any

PROXY_URL = "http://localhost:8082"
SERVER_NAME = "desktop-commander"
TOOL_NAME = "interact_with_process"

async def interact_with_process(params: Dict[str, Any]) -> str:
    """
    Auto-generated function calling MCP tool 'interact_with_process' on server 'desktop-commander'.
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

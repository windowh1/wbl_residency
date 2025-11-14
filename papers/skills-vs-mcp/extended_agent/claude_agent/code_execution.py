import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any


def run_agent_script(
        script_text: str, 
        iteration: int = 0,
        workspace_base: str= "./workspaces", 
        session_id: str = None,
        timeout: int = 20
    ) -> Dict[str, Any]:
    """
    Run the given agent script in a workspace.
    
    Args:
        script_text: The Python script text to execute
        iteration: Current iteration number
        workspace_base: Base directory for workspaces
        session_id: Unique session identifier
        timeout: Maximum time to allow for script execution
    
    Returns:
        Dict: stdout, stderr, returncode, and workspace path
    """
    # Generate session ID if not provided
    if session_id is None:
        session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create session workspace (persists across iterations)
    ws = Path(workspace_base) / session_id
    ws.mkdir(parents=True, exist_ok=True)

    # Save script with iteration number
    script_path = ws / f"script_{iteration + 1}.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_text)

    # Copy server modules (only once)
    src_servers = Path("./extensions/wrapped_mcp")
    dst_servers = ws / "extensions/wrapped_mcp"
    
    if src_servers.exists() and not dst_servers.exists():
        shutil.copytree(src_servers, dst_servers)

    # Create execution log
    log_path = ws / f"execution_{iteration + 1}.log"

    try:
        proc = subprocess.run(
            ["python", str(script_path.resolve())],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(ws)
        )
        
        result = {
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "returncode": proc.returncode,
            "workspace": str(ws),
            "script_path": str(script_path),
            "iteration": iteration + 1
        }
        
        # Save execution log
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Script: {script_path.name}\n")
            f.write(f"Timeout: {timeout}s\n")
            f.write(f"Return code: {proc.returncode}\n")
            f.write(f"\n{'-'*30}\n")
            f.write(f"STDOUT:\n{proc.stdout}\n")
            f.write(f"\n{'-'*30}\n")
            f.write(f"STDERR:\n{proc.stderr}\n")
        
        return result
        
    except subprocess.TimeoutExpired:
        result = {
            "error": "timeout",
            "workspace": str(ws),
            "script_path": str(script_path),
            "iteration": iteration + 1
        }
        
        # Save timeout log
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Script: {script_path.name}\n")
            f.write(f"Timeout: {timeout}s\n")
            f.write(f"Status: TIMEOUT\n")
        
        return result
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import Dict, Any
import httpx
import json
import multiprocessing
import signal
import time
import uvicorn

from mcp_server.client import MCPClient


# Global config storage for multiprocessing access
_proxy_config = None


def _set_proxy_config(
    config: Dict[str, Any]
):
    """
    Set global proxy config for multiprocessing.
    
    args:
        config: Configuration dictionary
    """
    global _proxy_config
    _proxy_config = config


def _get_proxy_config(
) -> Dict[str, Any]:
    """
    Get global proxy config.
    
    returns:
        Dict: Configuration dictionary
    """
    global _proxy_config
    return _proxy_config


@asynccontextmanager
async def lifespan(
    app: FastAPI
):
    """
    FastAPI lifespan: Start stdio MCP servers and proxy via HTTP.

    args:
        app: FastAPI application instance
    """
    # Get config
    config = _get_proxy_config()
    
    app.state.mcp_clients = {}
    
    # Add stdio servers to proxy
    for server_name, server_config in config.get("mcp_servers", {}).items():
        # Skip HTTP servers
        if "url" in server_config:
            continue
        
        try:
            client = MCPClient(
                name=server_name,
                command=server_config["command"],
                args=server_config.get("args", []),
                env=server_config.get("env", {})
            )
            await client.connect()
            app.state.mcp_clients[server_name] = client
        except Exception as e:
            print(f"[{server_name}] Failed to connect to server: {e}")
    
    yield
    
    # Clean up all MCP clients on shutdown
    for name, client in app.state.mcp_clients.items():
        try:
            await client.disconnect()
        except Exception as e:
            print(f"[{name}] Warning while disconnecting: {e}")


app = FastAPI(lifespan=lifespan, title="MCP HTTP Proxy")


@app.get("/")
async def root(
) -> Dict[str, Any]:
    """
    Health check endpoint.
    
    returns:
        Dict: Status information
    """
    return {
        "status": "running",
        "servers": list(app.state.mcp_clients.keys())
    }


@app.get("/servers")
async def list_servers(
) -> Dict[str, Any]:
    """
    List available MCP servers.
    
    returns:
        Dict: MCP servers and their tools
    """
    servers = {}
    for name, client in app.state.mcp_clients.items():
        servers[name] = {
            "tools": [tool["name"] for tool in client.tools]
        }
    return servers


@app.post("/mcp/{server_name}/call_tool")
async def call_tool(
    server_name: str,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Call a tool on a specific MCP server.
    
    args:
        server_name: Name of the MCP server
        tool_name: Name of the tool to call
        tool_input: Input dictionary for the tool
    
    returns:
        Dict: Tool call result
    """
    client = app.state.mcp_clients.get(server_name)
    
    if not client:
        raise HTTPException(
            status_code=404,
            detail=f"MCP server '{server_name}' not found. Available servers: {list(app.state.mcp_clients.keys())}"
        )
    
    try:
        result = await client.call_tool(tool_name, tool_input)
        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling tool '{tool_name}' on server '{server_name}': {str(e)}"
        )


class MCPHttpProxy:
    """
    MCP HTTP Proxy manager that can be started/stopped programmatically.
    """
    
    def __init__(
        self, 
        mcp_config: Dict[str, Dict[str, Any]],
        host: str = "localhost", 
        port: int = 8082
    ):
        """
        Initialize MCP HTTP Proxy.
        
        Args:
            mcp_config: MCP server configuration dict
            host: Host to bind to
            port: Port to bind to
        """
        self.mcp_config = mcp_config
        self.host = host
        self.port = port
        self.process = None
    

    def _run_server(self):
        """
        Run server in separate process
        """
        # Set config for this process
        _set_proxy_config({"mcp_servers": self.mcp_config})
        
        config = uvicorn.Config(
            app,
            host=self.host,
            port=self.port,
            log_level="info",
            loop="asyncio"
        )
        server = uvicorn.Server(config)
        server.run()
    
    
    def start(self):
        """
        Start the proxy server in a background process
        """
        if self.process is not None:
            print("Proxy server is already running.")
            return
        
        self.process = multiprocessing.Process(target=self._run_server, daemon=True)
        self.process.start()
        
        # Wait for server to start        
        for _ in range(30):  # Try for 3 seconds
            try:
                response = httpx.get(f"http://{self.host}:{self.port}/", timeout=0.5)
                if response.status_code == 200:
                    print(f"MCP HTTP Proxy is ready at http://{self.host}:{self.port}\n")
                    return
            except:
                time.sleep(0.1)
        
        print("Warning: Proxy server may not be ready yet, continuing anyway...\n")


    def stop(self):
        """
        Stop the proxy server
        """
        if self.process is None:
            return
        
        self.process.terminate()
        self.process.join(timeout=5)
        
        if self.process.is_alive():
            # Force killing proxy server
            self.process.kill()
            self.process.join()
        
        self.process = None
        print("MCP HTTP Proxy stopped")


    def __enter__(self):
        self.start()
        return self


    def __exit__(self):
        self.stop()


if __name__ == "__main__":
    print(f"\n{'='*30}")
    print("MCP HTTP Proxy Server:")

    # Load config from file when running directly
    with open("config.json") as f:
        config = json.load(f)
    
    _set_proxy_config(config)
    
    config = uvicorn.Config(
        app,
        host="localhost",
        port=8082,
        log_level="info",
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    
    def handle_exit(signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\nReceived interrupt signal, shutting down...")
        server.should_exit = True
    
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    server.run()
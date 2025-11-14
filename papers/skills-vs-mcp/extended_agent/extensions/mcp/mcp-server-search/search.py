from ddgs import DDGS
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, List, Any
import requests
import os
from pydantic import Field

mcp = FastMCP("mcp-server-search")


def search_duckduckgo(
    query: str, 
    max_results: int
) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: Search query
        max_results: Maximum search results
    
    Returns:
        Search results
    """
    results = []
    try:
        with DDGS() as search_engine:
            for idx, result in enumerate(search_engine.text(query, max_results=max_results), start=1):
                results.append({
                    "rank": idx,
                    "title": result.get("title", ""),
                    "description": result.get("body", ""),
                    "url": result.get("href", ""),
                    "source": "DuckDuckGo"
                })
    except Exception as e:
        results.append({"error": str(e), "source": "DuckDuckGo"})
    return results


def search_brave(
    query: str, 
    max_results: int
) -> List[Dict[str, Any]]:
    """
    Search the web using Brave.
    
    Args:
        query: Search query
        max_results: Maximum search results
    
    Returns:
        Search results
    """
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return [{"error": "BRAVE_API_KEY not set", "source": "Brave"}]
    
    try:
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"Accept": "application/json", "X-Subscription-Token": api_key},
            params={"q": query, "count": max_results},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "web" in data and "results" in data["web"]:
            for idx, result in enumerate(data["web"]["results"], start=1):
                results.append({
                    "rank": idx,
                    "title": result.get("title", ""),
                    "description": result.get("description", ""),
                    "url": result.get("url", ""),
                    "source": "Brave"
                })
        return results
    except Exception as e:
        return [{"error": str(e), "source": "Brave"}]


def search_serper(
    query: str, 
    max_results: int
) -> List[Dict[str, Any]]:
    """
    Search the web using Serper.
    
    Args:
        query: Search query
        max_results: Maximum search results
    
    Returns:
        Search results
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return [{"error": "SERPER_API_KEY not set", "source": "Serper"}]
    
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": max_results},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "organic" in data:
            for idx, result in enumerate(data["organic"], start=1):
                results.append({
                    "rank": idx,
                    "title": result.get("title", ""),
                    "description": result.get("snippet", ""),
                    "url": result.get("link", ""),
                    "source": "Serper"
                })
        return results
    except Exception as e:
        return [{"error": str(e), "source": "Serper"}]


@mcp.tool()
def web_search(
    query: str = Field(..., description="Search query (e.g., 'python tutorials', 'best sushi Tokyo')"),
    max_results: Optional[int] = Field(10, description="Maximum number of search results to return"),
    engine: Optional[str] = Field("duckduckgo", description="Search engine to use - 'duckduckgo', 'brave' or 'serper'")
) -> str:
    """
    Search the web using selected search engine (DuckDuckGo, Brave, or Serper).
    
    Returns:
        Search results
    """
    # Validate inputs
    if not query or not query.strip():
        return "Error: Query cannot be empty"
    
    query = query.strip()
    
    if engine not in ["duckduckgo", "brave", "serper"]:
        return f"Error: No valid search engines."
    
    # Search
    results = [] 
    if engine == "duckduckgo":
        results = search_duckduckgo(query, max_results)
    elif engine == "brave":
        results = search_brave(query, max_results)
    elif engine == "serper":
        results = search_serper(query, max_results)
    
    # Format results
    lines = [f"Search: {query}\n"]
    
    valid = [r for r in results if "error" not in r]
    errors = [r for r in results if "error" in r]
        
    if valid:
        lines.append(f"\n{engine} ({len(valid)} results):")
        for r in valid:
            lines.append(f"\n{r['rank']}. {r['title']}")
            lines.append(f"   {r['description']}")
            lines.append(f"   {r['url']}")
        
    if errors:
        lines.append(f"\n{engine}: {errors[0]['error']}")
    
    return "\n".join(lines)


@mcp.tool()
def get_engine_status() -> str:
    """
    Get search engine status.
    
    Returns:
        Search engine status
    """
    brave_ok = "O" if os.getenv("BRAVE_API_KEY") else "X"
    serper_ok = "O" if os.getenv("SERPER_API_KEY") else "X"
    
    return f"""Search Engine Status:
\tDuckDuckGo: O
\tBrave: {brave_ok}
\tSerper: {serper_ok}
"""


if __name__ == "__main__":    
    mcp.run()
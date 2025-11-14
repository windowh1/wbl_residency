import asyncio
from extensions.wrapped_mcp.mcp_server_search.web_search import web_search

async def main():
    result = await web_search({
        "query": "2024 Nobel Prize in Literature winner",
        "max_results": 5
    })
    print(result)

asyncio.run(main())
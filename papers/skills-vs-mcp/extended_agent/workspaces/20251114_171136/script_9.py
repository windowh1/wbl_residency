import asyncio
from extensions.wrapped_mcp.mcp_server_search.web_search import web_search

async def main():
    result = await web_search({
        "query": "Han Kang Nobel Prize official page site:nobelprize.org",
        "max_results": 5
    })
    print(result)

asyncio.run(main())
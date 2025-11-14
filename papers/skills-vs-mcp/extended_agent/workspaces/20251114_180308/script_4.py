import asyncio
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    result = await web_search({
        "query": "부산 주요 관광지 top 5",
        "max_results": 10
    })
    print(result)

asyncio.run(main())
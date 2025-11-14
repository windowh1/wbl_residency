import asyncio
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    result = await web_search({
        "query": "부산 해운대 해수욕장 운영시간 입장료",
        "max_results": 5
    })
    print(result)

asyncio.run(main())
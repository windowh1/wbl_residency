import asyncio
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    result = await web_search({
        "query": "임플란트 건강보험 적용 기준",
        "max_results": 5,
        "engine": "brave"
    })
    print(result)

asyncio.run(main())
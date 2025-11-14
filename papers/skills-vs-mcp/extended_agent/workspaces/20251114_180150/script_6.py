import asyncio
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    result = await web_search({
        "query": "임플란트 건강보험 적용 나이 만 65세 본인부담금",
        "max_results": 5,
        "engine": "duckduckgo"
    })
    print(result)

asyncio.run(main())
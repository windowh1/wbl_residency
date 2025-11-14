import asyncio
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    result = await web_search({
        "query": "건강보험 임플란트 보장 site:nhis.or.kr OR site:gov.kr",
        "max_results": 5,
        "engine": "duckduckgo"
    })
    print(result)

asyncio.run(main())
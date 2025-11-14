import asyncio
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    # Search for official government page on implant insurance
    result = await web_search({
        "query": "국민건강보험 임플란트 급여 기준 nhis.or.kr",
        "max_results": 3,
        "engine": "brave"
    })
    print(result)

asyncio.run(main())
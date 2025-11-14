import asyncio
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    # 더 구체적인 관광지 검색
    queries = [
        "해운대 해수욕장 운영시간 입장료 가는법",
        "감천문화마을 운영시간 입장료 교통",
        "태종대 운영시간 입장료 대중교통",
        "광안리 해수욕장 운영시간 입장료 지하철",
        "용두산공원 부산타워 운영시간 입장료 교통"
    ]
    
    results = []
    for query in queries:
        result = await web_search({
            "query": query,
            "max_results": 3
        })
        results.append(f"\n{'='*60}\n질문: {query}\n{'='*60}\n{result}\n")
    
    for r in results:
        print(r)

asyncio.run(main())
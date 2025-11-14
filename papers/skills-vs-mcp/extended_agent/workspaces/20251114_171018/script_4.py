import asyncio
from extensions.wrapped_mcp.mcp_server_search.web_search import web_search

async def main():
    # 서울 이번 주말 전시회 검색
    result = await web_search({
        "query": "서울 이번 주말 전시회 2024",
        "max_results": 10,
        "engine": "duckduckgo"
    })
    
    # 결과를 지정된 경로에 저장
    output_path = "/Users/user/Library/Mobile Documents/com~apple~CloudDocs/Desktop/WBL/wbl_residency/papers/skills-vs-mcp/experiment3/results/code_execution_tests/code_execution_enabled/20251114_171018/seoul_exhibitions.txt"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    
    print(f"검색 결과가 {output_path}에 저장되었습니다.")
    print("\n검색 결과 미리보기:")
    print(result[:500] + "..." if len(result) > 500 else result)

asyncio.run(main())
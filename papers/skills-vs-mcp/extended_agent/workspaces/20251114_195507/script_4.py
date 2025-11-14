import asyncio
from extensions.wrapped_mcp.mcp_server_search.web_search import web_search
import os

async def main():
    # 서울 주말 전시회 검색
    result = await web_search({
        "query": "서울 이번 주말 전시회 2024",
        "max_results": 10,
        "engine": "duckduckgo"
    })
    
    print("검색 결과:")
    print(result)
    
    # 결과를 파일로 저장
    output_path = "/Users/user/Library/Mobile Documents/com~apple~CloudDocs/Desktop/WBL/wbl_residency/papers/skills-vs-mcp/extended_agent/results/20251114_195507/seoul_exhibitions.txt"
    
    # 디렉토리가 존재하는지 확인하고 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("서울 이번 주말 전시회 검색 결과\n")
        f.write("=" * 50 + "\n\n")
        f.write(result)
    
    print(f"\n결과가 저장되었습니다: {output_path}")

asyncio.run(main())
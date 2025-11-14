import asyncio
from extensions.wrapped_mcp.mcp_server_fetch import fetch

async def main():
    # 부산 관광 공식 사이트들에서 정보 가져오기
    urls = [
        "https://www.visitbusan.net/kr/index.do",
        "https://korean.visitkorea.or.kr/detail/ms_detail.do?cotid=d09a4082-bba0-467d-ba41-2c66de95a34e"
    ]
    
    for url in urls:
        try:
            print(f"\n{'='*60}")
            print(f"Fetching: {url}")
            print('='*60)
            result = await fetch({"url": url, "max_length": 3000})
            print(result[:2000])  # 처음 2000자만 출력
        except Exception as e:
            print(f"Error fetching {url}: {e}")

asyncio.run(main())
import asyncio
from extensions.wrapped_mcp.mcp_server_fetch import fetch

async def main():
    result = await fetch({
        "url": "https://www.nhis.or.kr/static/html/wbma/c/wbmac0221.html",
        "max_length": 10000,
        "raw": True
    })
    print(result[:2000])  # Print first 2000 chars to see what we get

asyncio.run(main())
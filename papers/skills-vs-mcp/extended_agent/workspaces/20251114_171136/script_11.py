import asyncio
from extensions.wrapped_mcp.mcp_server_fetch.fetch import fetch

async def main():
    # Fetch the biography page which should have more details about her works
    result = await fetch({
        "url": "https://www.nobelprize.org/prizes/literature/2024/bio-bibliography/",
        "max_length": 20000
    })
    print(result)

asyncio.run(main())
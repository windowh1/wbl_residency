import asyncio
from extensions.wrapped_mcp.mcp_server_fetch.fetch import fetch

async def main():
    # Fetch Han Kang's official Nobel Prize facts page
    result = await fetch({
        "url": "https://www.nobelprize.org/prizes/literature/2024/han/facts/",
        "max_length": 15000
    })
    print(result)

asyncio.run(main())
import asyncio
from extensions.wrapped_mcp.mcp_server_fetch.fetch import fetch

async def main():
    # Fetch the Wikipedia page about 2024 Nobel Prize in Literature
    result = await fetch({
        "url": "https://en.wikipedia.org/wiki/2024_Nobel_Prize_in_Literature",
        "max_length": 10000
    })
    print(result)

asyncio.run(main())
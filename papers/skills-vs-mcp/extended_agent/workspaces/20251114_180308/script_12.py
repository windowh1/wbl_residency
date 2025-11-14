import asyncio
import sys
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    try:
        print("Starting search...")
        sys.stdout.flush()
        
        result = await web_search({
            "query": "해운대 해수욕장 운영시간",
            "max_results": 2
        })
        print("Result:", result)
        sys.stdout.flush()
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()

asyncio.run(main())
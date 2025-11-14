import asyncio
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    # Search for electric vehicles pros and cons
    ev_result = await web_search({
        "query": "electric vehicles EV pros and cons advantages disadvantages",
        "max_results": 5
    })
    print("=== Electric Vehicle Search Results ===")
    print(ev_result)
    print("\n" + "="*50 + "\n")
    
    # Search for hybrid vehicles pros and cons
    hybrid_result = await web_search({
        "query": "hybrid vehicles pros and cons advantages disadvantages",
        "max_results": 5
    })
    print("=== Hybrid Vehicle Search Results ===")
    print(hybrid_result)

asyncio.run(main())
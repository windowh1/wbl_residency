import asyncio
from extensions.wrapped_mcp.mcp_server_search import web_search

async def main():
    # 각 관광지별 상세 정보 검색
    tourist_spots = [
        "해운대 해수욕장",
        "감천문화마을", 
        "태종대",
        "광안리 해수욕장",
        "용두산공원 부산타워"
    ]
    
    all_info = {}
    
    for spot in tourist_spots:
        print(f"\n{'='*70}")
        print(f"관광지: {spot}")
        print('='*70)
        
        try:
            # 운영시간 및 입장료
            query1 = f"{spot} 운영시간 입장료"
            result1 = await web_search({"query": query1, "max_results": 3})
            print("\n[운영시간 및 입장료]")
            print(result1)
            
            # 대중교통
            query2 = f"{spot} 가는법 지하철 버스"
            result2 = await web_search({"query": query2, "max_results": 3})
            print("\n[대중교통 정보]")
            print(result2)
            
            all_info[spot] = {
                "operation": result1,
                "transport": result2
            }
            
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(main())
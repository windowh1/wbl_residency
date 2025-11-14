#!/usr/bin/env python3
"""
React 생태계 라이브러리 GitHub 데이터 수집 스크립트
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 분석할 라이브러리 목록
LIBRARIES = {
    "React Router": "remix-run/react-router",
    "Redux": "reduxjs/redux",
    "Zustand": "pmndrs/zustand",
    "TanStack Query": "TanStack/query",
    "Jotai": "pmndrs/jotai"
}

def fetch_github_data(repo: str) -> Dict[str, Any]:
    """GitHub API를 호출하여 저장소 데이터 수집"""
    url = f"https://api.github.com/repos/{repo}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "name": data["name"],
            "full_name": data["full_name"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "open_issues": data["open_issues_count"],
            "watchers": data["watchers_count"],
            "last_updated": data["updated_at"],
            "created_at": data["created_at"],
            "description": data.get("description", ""),
            "language": data.get("language", ""),
            "homepage": data.get("homepage", ""),
            "topics": data.get("topics", []),
            "license": data.get("license", {}).get("name", "N/A") if data.get("license") else "N/A"
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {repo}: {e}")
        return None

def calculate_popularity_score(data: Dict[str, Any]) -> float:
    """인기도 점수 계산 (가중 평균)"""
    # 가중치 설정
    weights = {
        "stars": 0.4,
        "forks": 0.2,
        "watchers": 0.1,
        "recent_activity": 0.3  # 최근 업데이트 빈도
    }
    
    # 정규화를 위한 최대값 설정
    max_stars = 100000
    max_forks = 20000
    max_watchers = 10000
    
    # 점수 계산
    star_score = min(data["stars"] / max_stars, 1.0) * weights["stars"]
    fork_score = min(data["forks"] / max_forks, 1.0) * weights["forks"]
    watcher_score = min(data["watchers"] / max_watchers, 1.0) * weights["watchers"]
    
    # 최근 활동도 (최근 30일 이내 업데이트시 만점)
    last_update = datetime.strptime(data["last_updated"], "%Y-%m-%dT%H:%M:%SZ")
    days_since_update = (datetime.now() - last_update).days
    activity_score = max(0, 1 - (days_since_update / 365)) * weights["recent_activity"]
    
    total_score = star_score + fork_score + watcher_score + activity_score
    return round(total_score * 100, 2)

def estimate_growth_rate(data: Dict[str, Any]) -> str:
    """성장률 추정 (실제로는 시계열 데이터 필요, 여기서는 추정)"""
    # 저장소 나이 계산
    created = datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    age_days = (datetime.now() - created).days
    
    # 일일 평균 star 증가량
    avg_stars_per_day = data["stars"] / max(age_days, 1)
    
    if avg_stars_per_day > 50:
        return "Very High (50+ stars/day)"
    elif avg_stars_per_day > 20:
        return "High (20-50 stars/day)"
    elif avg_stars_per_day > 5:
        return "Medium (5-20 stars/day)"
    else:
        return "Low (<5 stars/day)"

def main():
    """메인 함수"""
    print("=" * 60)
    print("React 생태계 GitHub 데이터 수집 시작")
    print("=" * 60)
    print()
    
    results = {}
    
    for lib_name, repo in LIBRARIES.items():
        print(f"수집 중: {lib_name} ({repo})...")
        data = fetch_github_data(repo)
        
        if data:
            # 추가 분석 데이터 계산
            data["popularity_score"] = calculate_popularity_score(data)
            data["growth_rate"] = estimate_growth_rate(data)
            
            results[lib_name] = data
            print(f"  ✓ Stars: {data['stars']:,} | Forks: {data['forks']:,}")
        else:
            print(f"  ✗ 데이터 수집 실패")
        print()
    
    # 결과를 JSON 파일로 저장
    output_file = "react_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"데이터 수집 완료! 결과가 {output_file}에 저장되었습니다.")
    
    # 순위 출력
    print("\n" + "=" * 60)
    print("인기도 순위 (Popularity Score)")
    print("=" * 60)
    
    sorted_libs = sorted(results.items(), 
                        key=lambda x: x[1]["popularity_score"], 
                        reverse=True)
    
    for i, (lib_name, data) in enumerate(sorted_libs, 1):
        print(f"{i}. {lib_name}")
        print(f"   점수: {data['popularity_score']}/100")
        print(f"   Stars: {data['stars']:,} | Growth: {data['growth_rate']}")
        print()
    
    return results

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
GitHub Ecosystem Data Collection Script Template
Customize LIBRARIES dictionary for your specific ecosystem analysis
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any

# ============================================================================
# CONFIGURATION: Customize this section for your ecosystem
# ============================================================================

LIBRARIES = {
    "Library A": "org/repo-a",
    "Library B": "org/repo-b",
    "Library C": "org/repo-c",
    # Add more libraries here in format: "Display Name": "github-org/repo-name"
}

# Adjust these maximums based on your ecosystem's typical size
# Look at the largest repos in the ecosystem for reference
MAX_STARS = 100000      # Maximum stars for normalization
MAX_FORKS = 20000       # Maximum forks for normalization
MAX_WATCHERS = 10000    # Maximum watchers for normalization

# Scoring weights (should sum to 1.0)
WEIGHTS = {
    "stars": 0.4,           # Primary popularity indicator
    "forks": 0.2,           # Community contribution level
    "watchers": 0.1,        # Active monitoring
    "recent_activity": 0.3  # Maintenance health
}

# ============================================================================
# CORE FUNCTIONS: Generally no need to modify below this line
# ============================================================================

def fetch_github_data(repo: str) -> Dict[str, Any]:
    """
    Fetch repository data from GitHub API
    
    Args:
        repo: Repository path in format "owner/name"
        
    Returns:
        Dictionary containing repository metrics
    """
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
    """
    Calculate normalized popularity score (0-100)
    
    Uses weighted combination of:
    - Stars (40%)
    - Forks (20%)
    - Watchers (10%)
    - Recent activity (30%)
    
    Args:
        data: Repository data dictionary
        
    Returns:
        Popularity score from 0-100
    """
    # Normalize metrics against maximums
    star_score = min(data["stars"] / MAX_STARS, 1.0) * WEIGHTS["stars"]
    fork_score = min(data["forks"] / MAX_FORKS, 1.0) * WEIGHTS["forks"]
    watcher_score = min(data["watchers"] / MAX_WATCHERS, 1.0) * WEIGHTS["watchers"]
    
    # Calculate activity score (recent updates = higher score)
    last_update = datetime.strptime(data["last_updated"], "%Y-%m-%dT%H:%M:%SZ")
    days_since_update = (datetime.now() - last_update).days
    activity_score = max(0, 1 - (days_since_update / 365)) * WEIGHTS["recent_activity"]
    
    # Combine scores
    total_score = star_score + fork_score + watcher_score + activity_score
    return round(total_score * 100, 2)


def estimate_growth_rate(data: Dict[str, Any]) -> str:
    """
    Estimate growth rate based on stars per day
    
    Args:
        data: Repository data dictionary
        
    Returns:
        Growth rate category as string
    """
    created = datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    age_days = (datetime.now() - created).days
    
    # Calculate average stars per day
    avg_stars_per_day = data["stars"] / max(age_days, 1)
    
    # Categorize growth rate
    if avg_stars_per_day > 50:
        return "Very High (50+ stars/day)"
    elif avg_stars_per_day > 20:
        return "High (20-50 stars/day)"
    elif avg_stars_per_day > 5:
        return "Medium (5-20 stars/day)"
    else:
        return "Low (<5 stars/day)"


def main():
    """Main execution function"""
    print("=" * 60)
    print("GitHub Ecosystem Data Collection")
    print("=" * 60)
    print()
    
    results = {}
    
    # Fetch data for each library
    for lib_name, repo in LIBRARIES.items():
        print(f"Collecting: {lib_name} ({repo})...")
        data = fetch_github_data(repo)
        
        if data:
            # Calculate derived metrics
            data["popularity_score"] = calculate_popularity_score(data)
            data["growth_rate"] = estimate_growth_rate(data)
            
            results[lib_name] = data
            print(f"  ✓ Stars: {data['stars']:,} | Forks: {data['forks']:,}")
        else:
            print(f"  ✗ Failed to collect data")
        print()
    
    # Save results to JSON
    output_file = "ecosystem_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Data collection complete! Results saved to {output_file}")
    
    # Display rankings
    print("\n" + "=" * 60)
    print("Popularity Rankings")
    print("=" * 60)
    
    sorted_libs = sorted(
        results.items(), 
        key=lambda x: x[1]["popularity_score"], 
        reverse=True
    )
    
    for i, (lib_name, data) in enumerate(sorted_libs, 1):
        print(f"{i}. {lib_name}")
        print(f"   Score: {data['popularity_score']}/100")
        print(f"   Stars: {data['stars']:,} | Growth: {data['growth_rate']}")
        print()
    
    return results


if __name__ == "__main__":
    main()

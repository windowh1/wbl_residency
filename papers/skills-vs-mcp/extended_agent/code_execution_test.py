from main import main
import asyncio
import json
from pathlib import Path
from typing import Dict, List


EVALUATION_PROMPTS = [
    {
        "id": 1,
        "prompt": "서울에서 이번 주말에 열리는 전시회를 검색하고, 결과를 현재 작업 디렉토리에 있는 {result_dir}에 seoul_exhibitions.txt 파일로 저장해줘."
    },
    {
        "id": 2,
        "prompt": "2024년 노벨 문학상 수상자를 검색하고, 수상자의 공식 소개 페이지를 찾아 주요 작품 목록을 정리해서 현재 작업 디렉토리에 있는 {result_dir}에 nobel_literature_2024.txt로 저장해줘."
    },
    {
        "id": 3,
        "prompt": "전기차와 하이브리드차의 장단점을 검색해서 비교표로 정리하고, 현재 작업 디렉토리에 있는 {result_dir}에 ev_vs_hybrid.md 파일로 저장해줘."
    },
    {
        "id": 4,
        "prompt": "건강보험 임플란트 보장 기준을 검색하고, 공식 사이트에서 나이 제한, 보장 개수, 본인부담금 정보만 추출해서 현재 작업 디렉토리에 있는 {result_dir}에 implant_insurance.txt로 저장해줘."
    },
    {
        "id": 5,
        "prompt": """부산 여행 정보를 단계별로 수집해줘:
        
        1) 부산 주요 관광지 상위 5곳 검색
        2) 각 관광지의 운영시간과 입장료 확인
        3) 대중교통으로 접근하는 방법 정리
        4) 모든 정보를 현재 작업 디렉토리에 있는 {result_dir}에 busan_travel_guide.md로 저장
        
        각 단계에서 필요한 정보만 추출해서 최종 결과에 포함해줘."""
    }
]


def collect_results(
    directory: str
) -> List[Dict]:
    """
    Collect all responses.json files from the specified directory and its subdirectories.
    
    Args:
        directory: The root directory to search for responses.json files
    Returns:
        List: loaded JSON datas from each responses.json file
    """
    results = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"Warning: Directory {directory} does not exist")
        return results
    
    for response_file in dir_path.rglob("responses.json"):
        try:
            with open(response_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            print(f"Error reading {response_file}: {e}")
    
    return results


def calculate_averages(
    results: List[Dict]
) -> Dict:
    """
    Calculate average statistics from a list of result dictionaries.
    
    Args:
        results: A list of dictionaries containing individual run statistics1
    
    Returns:
        Dict: Average statistics
    """
    if not results:
        return {
            "count": 0,
            "avg_duration_seconds": 0,
            "avg_system_prompt_input_tokens": 0,
            "avg_input_tokens": 0,
            "avg_output_tokens": 0,
            "avg_total_tokens": 0,
            "avg_tool_calls": 0,
            "avg_api_call_count": 0
        }
    
    count = len(results)
    
    averages = {
        "count": count,
        "avg_duration_seconds": sum(r.get("duration_seconds", 0) for r in results) / count,
        "avg_system_prompt_input_tokens": sum(r.get("usage", {}).get("system_prompt_input_tokens", 0) for r in results) / count,
        "avg_input_tokens": sum(r.get("usage", {}).get("input_tokens", 0) for r in results) / count,
        "avg_output_tokens": sum(r.get("usage", {}).get("output_tokens", 0) for r in results) / count,
        "avg_total_tokens": sum(
            r.get("usage", {}).get("system_prompt_input_tokens", 0) + 
            r.get("usage", {}).get("input_tokens", 0) + 
            r.get("usage", {}).get("output_tokens", 0) 
            for r in results
        ) / count,
        "avg_tool_calls": sum(r.get("tool_calls", 0) for r in results) / count,
        "avg_api_call_count": sum(r.get("api_call_count", 0) for r in results) / count
    }
    
    return averages


if __name__ == "__main__":
    
    for eval_prompt in EVALUATION_PROMPTS:
        print(f"\n\n=== Executing Evaluation Prompt ID: {eval_prompt['id']} ===")
        
        # Run with code execution
        print(f"\n--- Running with Code Execution Enabled ---")
        code_exec_enabled_dir = "results/code_execution_tests/code_execution_enabled"
        asyncio.run(main(
            user_prompt=eval_prompt["prompt"],
            result_directory=code_exec_enabled_dir,
            code_execution_conf={
                "enabled": True,
                "host": "localhost",
                "port": 8082
            }
        ))

        # Run without code execution
        print(f"\n--- Running with Code Execution Disabled ---")
        code_exec_disabled_dir = "results/code_execution_tests/code_execution_disabled"
        # asyncio.run(main(
        #     user_prompt=eval_prompt["prompt"],
        #     result_directory=code_exec_disabled_dir,
        #     code_execution_conf={
        #         "enabled": False
        #     }
        # ))
    
    code_exec_results = collect_results(code_exec_enabled_dir)
    direct_mcp_results = collect_results(code_exec_disabled_dir)
    
    code_exec_avg = calculate_averages(code_exec_results)
    with open(f"{code_exec_enabled_dir}/average_statistics.json", "w", encoding="utf-8") as f:
        json.dump(code_exec_avg, f, indent=4, ensure_ascii=False, default=str)
    direct_mcp_avg = calculate_averages(direct_mcp_results)
    with open(f"{code_exec_disabled_dir}/average_statistics.json", "w", encoding="utf-8") as f:
        json.dump(direct_mcp_avg, f, indent=4, ensure_ascii=False, default=str)
        
    

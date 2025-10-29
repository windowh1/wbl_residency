import anthropic
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple


def count_tool_blocks(
    response: Any
) -> Tuple[int, int]:
    """
    Count the number of 'tool_use' and 'tool_result' blocks in the response.
    """
    n_use = n_res = 0
    for block in response.content:
        btype = getattr(block, "type", "")
        if "tool_use" in btype:
            n_use += 1
        if "tool_result" in btype:
            n_res += 1
    return n_use, n_res


def extract_file_ids(
    response: Any
) -> List[str]:
    """
    Extract generated file IDs from the response
    """
    file_ids = []
    for item in response.content:
        if item.type == "bash_code_execution_tool_result":
            content_item = item.content
            if content_item.type == "bash_code_execution_result":
                for file in content_item.content:
                    if hasattr(file, "file_id"):
                        file_ids.append(file.file_id)
    return file_ids


def load_config(
    config_path: str = "../config.json"
) -> Dict[str, Any]:
    """
    Load a JSON configuration file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    # Load the configuration file
    config = load_config()
    claude_conf = config["claude"] 
    skills_conf = config["skills"]       
    prefix = config["prefix"]
    retries = config.get("retries", 1)
    store_dir = f"{prefix}/{datetime.now().strftime("%Y%m%d_%H%M%S")}"
    os.makedirs(store_dir, exist_ok=True)

    print(f"\n=== Skills: PPT Creation Log ===\n")

    all_attempts = []

    # Try multiple times; it often fails due to the max token limit
    for i in range(retries):
        # Record attempt start time
        attempt_start_time = time.time()
        
        print(f"\n{'-'*30}")
        print(f"Attempt {i+1}")
        print(f"{'-'*30}\n")

        client = anthropic.Anthropic(api_key=claude_conf["api_key"])
        response = client.beta.messages.create(
            model=claude_conf.get("model", "claude-sonnet-4-5-20250929"),
            max_tokens=claude_conf.get("max_tokens", 4096),
            temperature=claude_conf.get("temperature", 1.0),
            messages=[{"role": "user", "content": claude_conf["user_prompt"]}],
            betas=skills_conf["betas"],
            container={"skills": skills_conf["container_skills"]},
            tools=skills_conf["tools"],
        )
        
        # Record attempt end time and calculate duration
        attempt_end_time = time.time()
        attempt_duration = attempt_end_time - attempt_start_time
        
        # Print text content 
        # for idx, block in enumerate(response.content):
        #     print(f"Content Block {idx+1} ({block.type}):\n")
        #     if hasattr(block, "text"):
        #         print(f"{block.text}\n")
        #     print("\n")
        
        # Print metrics
        tool_use, _ = count_tool_blocks(response)
        print(f"Attempt Duration: {attempt_duration:.2f} seconds\n")    
        print(f"Stop Reason: {response.stop_reason}\n")    
        print(f"Input Tokens: {response.usage.input_tokens}\n")
        print(f"Output Tokens: {response.usage.output_tokens}\n")
        print(f"Tool Calls: {tool_use}\n\n")

        # Download any generated files for this attempt
        file_ids = extract_file_ids(response)
        for j, file_id in enumerate(file_ids, start=1):
            file_metadata = client.beta.files.retrieve_metadata(
                file_id=file_id,
                betas=["files-api-2025-04-14"]
            )
            file_content = client.beta.files.download(
                file_id=file_id,
                betas=["files-api-2025-04-14"]
            )
            result_filename = f"{store_dir}/result_{i+1}_{j}_{file_metadata.filename}"
            file_content.write_to_file(result_filename)
            print(f"Downloaded: {result_filename}\n")
        
        # Save data for JSON
        all_attempts.append({
            "attempt": i + 1,
            "duration_seconds": round(attempt_duration, 2),
            "stop_reason": response.stop_reason,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            "tool_calls": tool_use,
            "response": response.model_dump()
        })

    # Calculate summary statistics
    successful_attempts = [a for a in all_attempts if a["stop_reason"] not in ("pause_turn", "max_tokens")]
    
    avg_duration = sum(a["duration_seconds"] for a in all_attempts) / len(all_attempts)
    avg_input_tokens = sum(a["usage"]["input_tokens"] for a in all_attempts) / len(all_attempts)
    avg_output_tokens = sum(a["usage"]["output_tokens"] for a in all_attempts) / len(all_attempts)
    avg_tool_calls = sum(a["tool_calls"] for a in all_attempts) / len(all_attempts)
    success_ratio = len(successful_attempts) / len(all_attempts)
    
    print(f"\n{'='*30}\n")
    print(f"Summary:\n")
    print(f"  Average Duration: {avg_duration:.2f} seconds")
    print(f"  Average Total Input Tokens: {avg_input_tokens:.2f}")
    print(f"  Average Total Output Tokens: {avg_output_tokens:.2f}")
    print(f"  Average Tool Calls: {avg_tool_calls:.2f}")
    print(f"  Success Ratio: {success_ratio:.2f}")

    avg_duration_succeed = 0.0
    avg_input_tokens_succeed = 0.0
    avg_output_tokens_succeed = 0.0
    avg_tool_calls_succeed = 0.0
    
    if len(successful_attempts) > 0:
        avg_duration_succeed = sum(a["duration_seconds"] for a in successful_attempts) / len(successful_attempts)
        avg_input_tokens_succeed = sum(a["usage"]["input_tokens"] for a in successful_attempts) / len(successful_attempts)
        avg_output_tokens_succeed = sum(a["usage"]["output_tokens"] for a in successful_attempts) / len(successful_attempts)
        avg_tool_calls_succeed = sum(a["tool_calls"] for a in successful_attempts) / len(successful_attempts)
    
        print(f"\n{'-'*30}\n")
        print(f"Summary for successful attempts:\n")
        print(f"  Average Duration: {avg_duration_succeed:.2f} seconds")
        print(f"  Average Total Input Tokens: {avg_input_tokens_succeed:.2f}")
        print(f"  Average Total Output Tokens: {avg_output_tokens_succeed:.2f}")
        print(f"  Average Tool Calls: {avg_tool_calls_succeed:.2f}\n")


    # Add summary to all_attempts for JSON
    all_attempts.insert(0, {
        "summary": {
            "average_duration_seconds": round(avg_duration, 2),
            "average_input_tokens": round(avg_input_tokens, 2),
            "average_output_tokens": round(avg_output_tokens, 2),
            "average_tool_calls": round(avg_tool_calls, 2),
            "success_ratio": round(success_ratio, 2),
            "average_duration_seconds_succeed": round(avg_duration_succeed, 2),
            "average_input_tokens_succeed": round(avg_input_tokens_succeed, 2),
            "average_output_tokens_succeed": round(avg_output_tokens_succeed, 2),
            "average_tool_calls_succeed": round(avg_tool_calls_succeed, 2)
            }
    })

    # Save responses to JSON
    json_filename = f"{store_dir}/responses.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(all_attempts, f, indent=4, ensure_ascii=False, default=str)
    print(f"Saved JSON to: {json_filename}")


if __name__ == "__main__":        
    main()
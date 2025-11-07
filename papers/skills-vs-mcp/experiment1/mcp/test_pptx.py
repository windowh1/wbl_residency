import asyncio
import json
import glob
import os
import time
from datetime import datetime
from typing import Dict, Any

from agent import ClaudeAgent


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


async def main():
    # Load the configuration file
    config = load_config()
    claude_conf = config["claude"]
    prefix = config["prefix"]
    retries = config.get("retries", 1)
    store_dir = f"{prefix}/{datetime.now().strftime("%Y%m%d_%H%M%S")}"
    os.makedirs(store_dir, exist_ok=True)
    
    print(f"\n=== MCP: PPT Creation Log ===\n")
    
    all_attempts = []
    successful_attempts = []

    # Try multiple times
    for i in range(retries):
        # Record attempt start time
        attempt_start_time = time.time()
        is_successful = False
            
        print(f"\n{'-'*30}")
        print(f"Attempt {i+1}")
        print(f"{'-'*30}\n")

        agent = ClaudeAgent(
            api_key=claude_conf["api_key"],
            model=claude_conf.get("model", "claude-sonnet-4-5-20250929"),
            max_tokens=claude_conf.get("max_tokens", 4096),
            temperature=claude_conf.get("temperature", 1.0)
        )

        # Register and connect to MCP servers
        for name, server_conf in config.get("mcp_servers", {}).items():
            await agent.add_mcp(
                name,
                server_conf["command"],
                server_conf.get("args"),
                server_conf.get("env")
            )
        
        # Execute the task
        result = await agent.chat_with_mcp(claude_conf["user_prompt"])
        
        # Record attempt end time and calculate duration
        attempt_end_time = time.time()
        attempt_duration = attempt_end_time - attempt_start_time
                    
        # Print final response
        # print(f"Final Response:\n{result['text']}\n\n")

        # Print metrics
        metrics = agent.get_metrics()
        print(f"Attempt Duration: {attempt_duration:.2f} seconds\n")
        print(f"Stop Reason: {metrics['stop_reason']}\n")
        print(f"Input Tokens: {metrics['input_tokens']}\n")
        print(f"Output Tokens: {metrics['output_tokens']}\n")
        print(f"Tool Calls: {metrics['total_tool_calls']}\n\n")

        # Rename the generated .pptx files
        pptx_files = glob.glob("*.pptx")
        if len(pptx_files) > 0:
            is_successful = True
        for j, pptx_file in enumerate(pptx_files):           
            new_name = f"{store_dir}/result_{i+1}_{j}_{pptx_file}"
            os.rename(pptx_file, new_name)
            print(f"Renamed: {pptx_file} -> {new_name}\n")
        
        # Save data for JSON
        attempt_result = {
            "attempt": i + 1,
            "duration_seconds": round(attempt_duration, 2),
            "stop_reason": metrics['stop_reason'],
            "usage": {
                "input_tokens": metrics['input_tokens'],
                "output_tokens": metrics['output_tokens']
            },
            "tool_calls": metrics['total_tool_calls'],
            "response": agent.conversation_history
        }
        all_attempts.append(attempt_result)
        if is_successful:
            successful_attempts.append(attempt_result)

        # Disconnect from all MCP servers
        await agent.disconnect_all_mcp()
    
    # Calculate summary statistics
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
    asyncio.run(main())
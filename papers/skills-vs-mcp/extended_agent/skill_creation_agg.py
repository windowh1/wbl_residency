from anthropic import Anthropic
import argparse
import asyncio
import json
import os
import time
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

from claude_agent.agent import ClaudeAgent
from claude_agent.custom_skills import set_custom_skills
from claude_agent.file_download import download_all_files


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load a JSON configuration file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.json", help="Path to configuration file")
    parser.add_argument("--session-ids", type=json.loads, default="[]", help="Session id list to aggregate")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    claude_conf = config["claude"]
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_dir = f"{config['result_directory']}/{session_id}"
    os.makedirs(result_dir, exist_ok=True)

    conversation_list = []
    for past_session_id in args.session_ids:
        json_path = os.path.join(config['result_directory'], past_session_id, "responses.json")
        if not os.path.exists(json_path):
            print(f"Error: {json_path} is not available.")
            raise
        with open(json_path) as f:
            responses = json.load(f)
        conversation_list.append(responses["messages"])

    start_time = time.time()

    # Setup skill-creator skill
    sync_client = Anthropic(api_key=claude_conf["api_key"])
    print("Setting up skill-creator skill...\n")
    skills = set_custom_skills(
        sync_client,
        ["extensions/skills/skill-creator"],
        force_update=True
    )

    # Initialize Claude Agent
    agent = ClaudeAgent(
        api_key=claude_conf["api_key"],
        model=claude_conf.get("model", "claude-sonnet-4-5-20250929"),
        max_tokens=claude_conf.get("max_tokens", 4096),
        temperature=claude_conf.get("temperature", 1.0),
        betas=["code-execution-2025-08-25", "skills-2025-10-02"],
        skills=skills,
        configured_tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
        session_id=session_id
    )

    try:
        skill_creation_result = await agent.create_skill_from_conversation_list(conversation_list)
        
        end_time = time.time()
        duration = end_time - start_time
        usage_stats = agent.get_usage_stats()
        summary = {
            "aggregated_session_ids": args.session_ids,
            "skill_creation_result": skill_creation_result,
            "duration_seconds": round(duration, 2),
            "stop_reason": usage_stats["stop_reason"],
            "usage": {
                "input_tokens": usage_stats["input_tokens"],
                "output_tokens": usage_stats["output_tokens"]
            },
            "tool_calls": usage_stats["total_tool_calls"],
            "api_call_count": usage_stats["api_call_count"],
            "messages": agent.messages
        }

        json_filename = f"{result_dir}/responses_skill_creation_agg.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4, ensure_ascii=False, default=str)

        # Download generated files
        download_results = []
        for response in agent.api_responses:
            download_results += download_all_files(sync_client, response, result_dir)

        if len(download_results) > 0:
            print(f"\n{'-'*30}")
            print("File downloads:")
            success_count = 0
            for result in download_results:
                if result["success"]:
                    size_kb = result["size"] / 1024
                    overwrite_notice = " [overwritten]" if result.get("overwritten", False) else ""
                    print(f"    {result['output_path']} ({size_kb:.1f} KB){overwrite_notice}")
                    success_count += 1
                else:
                    print(f"    {result['output_path']} - Error: {result['error']}")
            print(f"\n{success_count}/{len(download_results)} files downloaded successfully")

    except Exception as e:
        print(f"\nError during execution: {e}")
        raise

    finally:
        # Cleanup all MCP resources
        print(f"\n{'='*30}")
        await agent.disconnect_mcp_servers()


if __name__ == "__main__":
    asyncio.run(main())
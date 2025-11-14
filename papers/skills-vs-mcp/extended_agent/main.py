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


async def main(
    user_prompt: str = None,
    result_directory: str = None,
    code_execution_conf: Dict[str, Any] = None
):
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str,  default="config.json", help="Path to configuration file")
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    claude_conf = config["claude"]
    if code_execution_conf is None:
        code_execution_conf = config.get("code_execution", {})
    use_code_execution = code_execution_conf.get("enabled", False)    
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    if result_directory is None:
        result_directory = config.get("result_directory", "results")
    result_dir = f"{result_directory}/{session_id}"
    
    create_new_skill = config.get("create_new_skill", False)
    mcp_conf = config.get("mcp_servers", {})
    skills_conf = config.get("skills", {})
    os.makedirs(result_dir, exist_ok=True)

    start_time = time.time()

    # Setup custom skills
    sync_client = Anthropic(api_key=claude_conf["api_key"])
    skills, custom_skill_names = [], []
    if skills_conf.get("custom_skill_folders"):
        print("Setting up custom skills...\n")
        skills = set_custom_skills(
            sync_client,
            skills_conf["custom_skill_folders"],
            force_update=True
        )
        custom_skill_names = [custom_skill.split("/")[-1] for custom_skill in skills_conf["custom_skill_folders"]]

    if create_new_skill and "skill-creator" not in custom_skill_names:
        print("Error: Include skill-creator custom skill in config.json.")
        raise

    if skills_conf.get("anthropic_skills"):
        skills.extend(skills_conf.get("anthropic_skills", []))

    # Initialize Claude Agent
    agent = ClaudeAgent(
        api_key=claude_conf["api_key"],
        model=claude_conf.get("model", "claude-sonnet-4-5-20250929"),
        max_tokens=claude_conf.get("max_tokens", 4096),
        temperature=claude_conf.get("temperature", 1.0),
        code_execution_conf=code_execution_conf,
        betas=skills_conf.get("betas", []),
        skills=skills,
        configured_tools=skills_conf.get("tools", []),
        session_id=session_id
    )

    try:
        # Setup MCP servers (agent handles proxy vs direct connection)
        await agent.setup_mcp_servers(mcp_conf)

        # Print available resources
        print(f"\n{'-'*30}")
        print("Available resources:")
        
        # Skills
        print(f"  Skills: {len(skills)}")
        for skill in custom_skill_names:
            print(f"    - Custom skill: {skill}")
        for skill in skills_conf.get("anthropic_skills", []):
            print(f"    - Anthropic skill: {skill['skill_id']}")
        
        # MCP resources
        if use_code_execution:
            print(f"  MCP wrappers: Available in extensions/wrapped_mcp/")
        else:
            print(f"  MCP tools: {len(agent.tools) - len(skills_conf.get("tools", []))}")
            for tool in agent.tools:
                if "__" in tool["name"]:
                    print(f"    - {tool['name']}")

        # Initial test prompt to get information about system prompt 
        simple_prompt = "Hi"
        agent.set_max_tokens(1)
        await agent.answer(simple_prompt)
        
        initial_usage_stats = agent.get_usage_stats()
        system_prompt_input_tokens = initial_usage_stats["input_tokens"] - 1  # Exclude simple prompt token

        # Reset messages and max tokens for actual execution
        agent.reset_messages()
        agent.set_max_tokens(claude_conf.get("max_tokens", 4096))

        # Execute user prompt
        print(f"\n{'='*30}")
        if user_prompt is None:
            user_prompt = claude_conf["user_prompt"]
        abs_result_dir = str(Path(result_dir).resolve())
        user_prompt = user_prompt.replace("{result_dir}", abs_result_dir)
        
        print(f"User:\n{user_prompt}")

        await agent.answer(user_prompt)

        # Record statistics
        end_time = time.time()
        duration = end_time - start_time
        usage_stats = agent.get_usage_stats()

        # Print statistics
        print(f"\n{'='*30}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Stop reason: {usage_stats['stop_reason']}")
        print(f"System prompt input tokens: {system_prompt_input_tokens}")
        print(f"Input tokens: {usage_stats['input_tokens']}")
        print(f"Output tokens: {usage_stats['output_tokens']}")
        print(f"Server tool uses: {usage_stats['total_server_tool_uses']}")
        print(f"Tool calls: {usage_stats['total_tool_calls']}")
        print(f"Claude API calls: {usage_stats['api_call_count']}")

        # Save summary
        summary = {
            "duration_seconds": round(duration, 2),
            "stop_reason": usage_stats["stop_reason"],
            "usage": {
                "system_prompt_input_tokens": system_prompt_input_tokens,
                "input_tokens": usage_stats["input_tokens"],
                "output_tokens": usage_stats["output_tokens"]
            },
            "tool_calls": usage_stats["total_tool_calls"],
            "api_call_count": usage_stats["api_call_count"],
            "messages": agent.messages,
        }

        json_filename = f"{result_dir}/responses.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4, ensure_ascii=False, default=str)

        print(f"\n{'-'*30}")
        print(f"Statistics and response data:")
        print(f"    {json_filename}")

        if create_new_skill:
            skill_creation_result = await agent.create_skill_from_conversation()
            end_time = time.time()
            duration = end_time - start_time
            usage_stats = agent.get_usage_stats()
            summary = {
                "skill_creation_result": skill_creation_result,
                "duration_seconds": round(duration, 2),
                "stop_reason": usage_stats["stop_reason"],
                "usage": {
                    "system_prompt_input_tokens": system_prompt_input_tokens,
                    "input_tokens": usage_stats["input_tokens"],
                    "output_tokens": usage_stats["output_tokens"]
                },
                "tool_calls": usage_stats["total_tool_calls"],
                "api_call_count": usage_stats["api_call_count"],
                "messages": agent.messages
            }

            json_filename = f"{result_dir}/responses_skill_creation.json"
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
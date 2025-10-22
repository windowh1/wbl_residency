import asyncio
import json
import os
from typing import Dict, Any

from agent import ClaudeAgent

def load_config(
    config_path: str = "config.json"
) -> Dict[str, Any]:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


async def main():
    # Load the configuration file
    config = load_config()

    # Initialize the Claude Agent
    claude_conf = config["claude"]
    agent = ClaudeAgent(
        api_key=claude_conf["api_key"],
        model=claude_conf.get("model", "claude-sonnet-4-5-20250929"),
        max_tokens=claude_conf.get("max_tokens", 4096),
        temperature=claude_conf.get("temperature", 1.0)
    )

    try:
        # Register and connect to MCP servers
        for name, server_conf in config.get("mcp_servers", {}).items():
            await agent.add_mcp(
                name,
                server_conf["command"],
                server_conf.get("args"),
                server_conf.get("env")
            )

        # Start the interactive conversation
        print("\n대화를 시작하세요!\n종료하려면 'quit'을 입력하세요.")
        while True:
            user_input = (await asyncio.to_thread(input, "> ")).strip()
            if user_input.lower() == "quit":
                print("\n대화를 종료합니다.")
                break

            result = await agent.chat_with_mcp(user_input)
            print("\nAgent:\n" + result["text"] + "\n")

    finally:
        # Disconnect from all MCP servers
        await agent.disconnect_all_mcp()


if __name__ == "__main__":
    asyncio.run(main())

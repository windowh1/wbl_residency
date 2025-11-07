import argparse
import json
import os

from browsecomp import browsecomp_eval, common
from agent_sampler import AgentSampler
from claude_sampler import ClaudeCompletionSampler, CLAUDE_SYSTEM_MESSAGE_LMSYS
from utils import load_config

BrowseCompEval = browsecomp_eval.BrowseCompEval


def main():
    # Set debug mode to avoid ThreadPool issues with async MCP connections
    os.environ["debug"] = "1"
    parser = argparse.ArgumentParser(
        description="Run BrowseComp evaluation using Claude Agent with MCP"
    )
    parser.add_argument(
        "--num_examples",
        type=int,
        default=10,
        help="Number of examples to evaluate (None for all)"
    )
    parser.add_argument(
        "--random_seed",
        type=int,
        default=42,
        help="Random seed for reproducible sample selection"
    )
    parser.add_argument(
        "--use_skills",
        action="store_true",
        help="Whether to use skills (if not set, uses MCP only)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to config file"
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Skip first N samples (useful for resuming interrupted runs)"
    )

    args = parser.parse_args()

    # Determine output directory based on use_skills
    output_dir = "results/skills" if args.use_skills else "results/mcp"

    # Print configuration
    print("Configuration:")
    print(f"  Config file: {args.config}")
    print(f"  Number of examples: {args.num_examples}")
    print(f"  Random seed: {args.random_seed}")
    print(f"  Use skills: {args.use_skills}")
    print(f"  Offset: {args.offset}")
    print(f"  Output directory: {output_dir}")

    # Config file path
    config_path = args.config
    CLAUDE_API_KEY = load_config(config_path)["claude"]["api_key"]

    # Create Agent Sampler (model to be evaluated)
    print(f"\n{'='*30}")
    print("Initializing Agent Sampler...")
    agent_sampler = AgentSampler(
        config_path=config_path,
        max_iterations=35,  # Maximum number of iterations for MCP tool usage
        use_skills=args.use_skills
    )

    # Create Grader Sampler (model for grading answers)
    # Use Claude as grader
    print("Initializing Grader Sampler...")
    grader_sampler = ClaudeCompletionSampler(
        api_key=CLAUDE_API_KEY,
        model="claude-haiku-4-5-20251001",
        system_message=CLAUDE_SYSTEM_MESSAGE_LMSYS,
        max_tokens=2048,
    )

    # Create BrowseComp evaluation
    print("Creating BrowseComp evaluation...")
    eval_obj = BrowseCompEval(
        grader_model=grader_sampler,
        num_examples=args.num_examples if args.num_examples > 0 else None,
        output_dir=output_dir,
        random_seed=args.random_seed,
        offset=args.offset
    )

    # Run evaluation
    print("Running evaluation...")
    result = eval_obj(agent_sampler)

    # Print results
    print(f"\n{'='*30}")
    print("Evaluation Results")
    print(f"Accuracy: {result.score:.3f}")
    if result.metrics:
        print("\nMetrics:")
        for key, value in result.metrics.items():
            print(f"  {key}: {value:.3f}")


if __name__ == "__main__":
    main()


import argparse
import json
import os
import sys
from typing import Any, Dict, Tuple
from pathlib import Path

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


def load_config(
    config_path: str = "config.json"
) -> Dict[str, Any]:
    """
    Load a JSON configuration file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_average_metadata(
    metadata_list: list[dict]
) -> dict:
    """
    Calculate average values from all sample metadata.

    Args:
        metadata_list: List of metadata dictionaries from all samples

    Returns:
        dict: Averaged metadata values
    """
    if not metadata_list:
        return {}

    num_samples = len(metadata_list)

    # Calculate averages
    avg_duration = sum(m.get("duration_seconds", 0) for m in metadata_list) / num_samples
    avg_input_tokens = sum(m.get("usage", {}).get("input_tokens", 0) for m in metadata_list) / num_samples
    avg_output_tokens = sum(m.get("usage", {}).get("output_tokens", 0) for m in metadata_list) / num_samples
    avg_tool_calls = sum(m.get("tool_calls", 0) for m in metadata_list) / num_samples
    avg_api_calls = sum(m.get("api_call_count", 0) for m in metadata_list) / num_samples

    # Calculate totals as well
    total_duration = sum(m.get("duration_seconds", 0) for m in metadata_list)
    total_input_tokens = sum(m.get("usage", {}).get("input_tokens", 0) for m in metadata_list)
    total_output_tokens = sum(m.get("usage", {}).get("output_tokens", 0) for m in metadata_list)
    total_tool_calls = sum(m.get("tool_calls", 0) for m in metadata_list)
    total_api_calls = sum(m.get("api_call_count", 0) for m in metadata_list)

    # Collect stop reasons
    stop_reasons = [m.get("stop_reason", "unknown") for m in metadata_list]
    unique_stop_reasons = list(set(stop_reasons))

    return {
        "averages": {
            "duration_seconds": round(avg_duration, 2),
            "input_tokens": round(avg_input_tokens, 2),
            "output_tokens": round(avg_output_tokens, 2),
            "total_tokens": round(avg_input_tokens + avg_output_tokens, 2),
            "tool_calls": round(avg_tool_calls, 2),
            "api_call_count": round(avg_api_calls, 2),
        },
        "totals": {
            "duration_seconds": round(total_duration, 2),
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "tool_calls": total_tool_calls,
            "api_call_count": total_api_calls,
        },
        "stop_reasons": unique_stop_reasons,
    }


def generate_summary(
    results_dir: str, 
    random_seed: int = 42
):
    """
    Generate summary.json from sample_*.json files in the given directory.

    Args:
        results_dir: Path to directory containing sample_*.json files
        random_seed: Random seed used for the evaluation (default: 42)
    """
    results_path = Path(results_dir)

    if not results_path.exists():
        print(f"Error: Directory {results_dir} does not exist")
        return

    # Find all sample_*.json files
    sample_files = sorted(results_path.glob("sample_*.json"))

    if not sample_files:
        print(f"Error: No sample_*.json files found in {results_dir}")
        return

    print(f"Found {len(sample_files)} sample files")

    # Load all samples
    samples = []
    metadata_list = []

    for sample_file in sample_files:
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                sample_data = json.load(f)
                samples.append(sample_data)
                metadata_list.append(sample_data.get("metadata", {}))
                print(f"  Loaded: {sample_file.name}")
        except Exception as e:
            print(f"  Error loading {sample_file.name}: {e}")
            continue

    if not samples:
        print("Error: No valid samples loaded")
        return

    # Calculate aggregate metrics
    num_correct = sum(1 for s in samples if s.get("is_correct", False))
    num_incorrect = sum(1 for s in samples if not s.get("is_correct", False))
    num_samples = len(samples)

    accuracy = num_correct / num_samples if num_samples > 0 else 0

    aggregate_metrics = {
        "is_correct": accuracy,
        "is_incorrect": num_incorrect / num_samples if num_samples > 0 else 0,
    }

    # Calculate average metadata
    avg_metadata = calculate_average_metadata(metadata_list)

    # Create summary
    summary = {
        "num_samples": num_samples,
        "aggregate_metrics": aggregate_metrics,
        "accuracy": accuracy,
        "average_metadata": avg_metadata,
        "random_seed": random_seed
    }

    # Save summary
    summary_file = results_path / "summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary saved to: {summary_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate summary.json file"
    )
    parser.add_argument(
        "--results_dir",
        type=str,
        help="Path to directory containing sample_*.json files"
    )
    parser.add_argument(
        "--random_seed",
        type=int,
        default=42,
        help="Random seed for reproducible sample selection"
    )

    args = parser.parse_args()
    generate_summary(args.results_dir, args.random_seed)


if __name__ == "__main__":
    main()

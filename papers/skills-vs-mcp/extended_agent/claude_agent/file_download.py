from anthropic import Anthropic
import json
import os
from pathlib import Path
from typing import List, Dict, Any


def extract_file_ids(
    response: Any
) -> List[str]:
    """
    Extract all file IDs from a Claude API response.

    Skills create files during code execution and return file_id attributes
    in the tool results. This function parses the response to find all file IDs.

    Args:
        response: The response object from client.beta.messages.create()

    Returns:
        List of file IDs found in the response
    """
    file_ids = []

    for block in response.content:
        # Check for bash_code_execution_tool_result (beta API format)
        if block.type == "bash_code_execution_tool_result":
            try:
                if hasattr(block, "content") and hasattr(block.content, "content"):
                    # Iterate through content array
                    for item in block.content.content:
                        if hasattr(item, "file_id"):
                            file_ids.append(item.file_id)
            except Exception as e:
                print(f"Error parsing bash_code_execution_tool_result: {e}")
                continue

        # Check for legacy tool_result blocks (for backward compatibility)
        elif block.type == "tool_result":
            try:
                if hasattr(block, "output"):
                    output_str = str(block.output)

                    # Look for file_id patterns in the output
                    if "file_id" in output_str.lower():
                        # Try to parse as JSON first
                        try:
                            output_json = json.loads(output_str)
                            if isinstance(output_json, dict) and "file_id" in output_json:
                                file_ids.append(output_json["file_id"])
                            elif isinstance(output_json, list):
                                for item in output_json:
                                    if isinstance(item, dict) and "file_id" in item:
                                        file_ids.append(item["file_id"])
                        except json.JSONDecodeError:
                            # If not JSON, use regex to find file_id patterns
                            import re

                            pattern = r"file_id['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_-]+)"
                            matches = re.findall(pattern, output_str)
                            file_ids.extend(matches)
            except Exception as e:
                print(f"Error parsing tool_result block: {e}")
                continue

    # Remove duplicates while preserving order
    seen = set()
    unique_file_ids = []
    for fid in file_ids:
        if fid not in seen:
            seen.add(fid)
            unique_file_ids.append(fid)

    return unique_file_ids


def download_file(
    client: Anthropic, 
    file_id: str, 
    output_path: str, 
    overwrite: bool = True
) -> Dict[str, Any]:
    """
    Download a file from Claude's Files API and save it locally.

    Args:
        client: Anthropic client instance
        file_id: The file ID returned by Skills
        output_path: Local path where the file should be saved
        overwrite: Whether to overwrite existing files (default: True)

    Returns:
        Dictionary with download metadata:
        {
            'file_id': str,
            'output_path': str,
            'size': int,
            'success': bool,
            'error': Optional[str]
        }
    """
    result = {
        "file_id": file_id,
        "output_path": output_path,
        "size": 0,
        "success": False,
        "error": None,
    }

    try:
        # Check if file exists
        file_exists = os.path.exists(output_path)
        if file_exists and not overwrite:
            result["error"] = f"File already exists: {output_path} (set overwrite=True to replace)"
            return result

        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Download file content from Files API (beta namespace)
        file_content = client.beta.files.download(file_id=file_id)

        # Save to disk
        with open(output_path, "wb") as f:
            f.write(file_content.read())

        # Get file size
        result["size"] = os.path.getsize(output_path)
        result["success"] = True
        result["overwritten"] = file_exists  # Track if we overwrote an existing file

    except Exception as e:
        print(f"Error downloading file: {e}")
        result["error"] = str(e)

    return result


def download_all_files(
    client: Anthropic,
    response: Any,
    output_dir: str,
    prefix: str = "",
    overwrite: bool = True,
) -> List[Dict[str, Any]]:
    """
    Extract and download all files from a Claude API response.

    This is a convenience function that combines extract_file_ids()
    and download_file() to download all files in a single call.

    Args:
        client: Anthropic client instance
        response: The response object from client.messages.create()
        output_dir: Directory where files should be saved
        prefix: Optional prefix for filenames (e.g., "financial_report_")
        overwrite: Whether to overwrite existing files (default: True)

    Returns:
        List of download results (one per file)
    """
    file_ids = extract_file_ids(response)
    results = []

    for i, file_id in enumerate(file_ids, 1):
        # Try to get file metadata for proper filename
        try:
            file_info = client.beta.files.retrieve_metadata(file_id=file_id)
            filename = file_info.filename
        except Exception:
            # If we can't get metadata, use a generic filename
            filename = f"file_{i}.bin"

        # Add prefix if provided
        if prefix:
            filename = f"{prefix}_{filename}"

        # Construct full output path
        output_path = os.path.join(output_dir, filename)

        # Download the file
        result = download_file(client, file_id, output_path, overwrite=overwrite)
        results.append(result)

    return results

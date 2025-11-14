
CODE_EXECUTION_SYSTEM_PROMPT = """
You are an autonomous reasoning agent that generates Python code for external execution.

1. Write a Python code block using markdown: ```python ... ```
2. The code will be executed externally in a sandbox
3. The results will be returned to you in the next message

**DO NOT attempt to execute code using the `bash_code_execution` tool. Only output a code block.**

# Environment Information

- The root directory contains a folder named `extensions/wrapped_mcp/`
- Each subfolder inside `extensions/wrapped_mcp/` corresponds to a connected MCP server (e.g., `extensions/wrapped_mcp/mcp_server_fetch`)
- Each of these subfolders contains one or more Python wrapper files, each representing a tool (e.g., `fetch.py`)

# CRITICAL RULES

**YOU MUST NEVER call the `bash_code_execution` tool EXCEPT when using Skills.**

**Why this matters**
- Code blocks execute LOCALLY → can access `extensions/wrapped_mcp/`
- `bash_code_execution` executes REMOTELY in Skills environment → CANNOT access `extensions/wrapped_mcp/`
- Using the wrong method will result in import errors and failures

# Progressive Discovery Workflow

**Follow this workflow step-by-step, generating ONE code block at a time**

## Step 1: List available servers
   List subdirectories under `extensions/wrapped_mcp/` to identify which MCP servers are available.
   
   Response (DO NOT execute it yourself):
   ```python
   import os
   print(os.listdir("extensions/wrapped_mcp"))
   ```

## Step 2: List tools in a server (after seeing Step 1 results)
   For a selected server (e.g. `mcp_server_fetch`), list all `.py` files inside that subfolder.
   
   Response:
   ```python
   import os
   print(os.listdir("extensions/wrapped_mcp/mcp_server_fetch"))
   ```

## Step 3: Read tool documentation (after seeing Step 2 results)
   Open the relevant Python file and inspect its contents to see how the function is defined.
   
   Response:
   ```python
   with open("extensions/wrapped_mcp/mcp_server_fetch/fetch.py") as f:
       print(f.read())
   ```

## Step 4: Use the tool (after understanding from Step 3)
   Once you confirm the function name and parameters, import and call it properly.
   
   Response:
   ```python
   import asyncio
   from extensions.wrapped_mcp.mcp_server_fetch import fetch
   
   async def main():
       result = await fetch({"url": "https://example.com"})
       print(result)
   
   asyncio.run(main())
   ```

# Output Format

When responding:
- Output EXACTLY ONE ```python code block
- Always include `print()` statements for results
- For async functions, wrap in `asyncio.run(main())`
- Do NOT use any tool calls related to code execution

**REMEMBER: You generate a code block. You do NOT execute them.**
"""


CODE_EXECUTION_FEEDBACK_PROMPT = """
Execution result:
{combined}

Next step:
- If more code or reasoning is needed: 
    Output ONLY a new ```python code block with no explanation
- If an ERROR occurred: 
    Analyze it and provide corrected code in a ```python block 
    You may read and edit your last script ({script_path}) instead of rewriting everything
- If the task is COMPLETE and successful: 
    Provide a brief summary WITHOUT any ```python code blocks
"""


SKILL_CREATION_PROMPT = """
Analyze the conversation history and determine if it contains a workflow pattern worth formalizing into a skill. If appropriate, create a new skill using the skill-creator Skill.

## Evaluation Criteria

### When TO CREATE a skill:
- Workflow has multiple steps (3+) with a clear structure
- Process involves multiple tool integrations
- Pattern is repeatable across different inputs/contexts
- Approach can be templated for similar problems

### When NOT TO create a skill:
- Workflow is too simple (1-2 steps only)
- No clear repeatable pattern exists
- Task is too particular to this single use case
- Process is too variable or context-dependent to formalize
- A similar skill already exists without significant improvements

## Process

1. **Analyze the conversation**
   - Identify the core workflow pattern
   - Assess reusability and generalizability
   - If not worth creating → **Skip and go to step 4**

2. **Review available skills to avoid duplication**
   - Check if similar skill already exists
   - If similar skill exists:
     * Create new version only if significant improvements can be made
     * If no significant improvement → **Skip and go to step 4**
 
3. **Create the skill (if appropriate)**
   - Follow skill-creator Skill guidelines
   - Make it generic enough for reuse, specific enough for utility

4. **Explain your decision**
   - If creating: Describe the workflow pattern identified and why it's valuable as a reusable skill
   - If skipping: Explain clearly why no skill was created

Proceed with the analysis and decision following the skill-creator Skill guidelines.
"""


AGGREGATE_SKILL_CREATION_PROMPT = """
Analyze the conversation histories provided below and determine if they contain workflow patterns worth formalizing into a skill. If appropriate, create a new skill using the skill-creator Skill.

## Evaluation Criteria

### When TO CREATE a skill:
- Workflow has multiple steps (3+) with a clear structure
- Process involves multiple tool integrations
- Pattern is repeatable across different inputs/contexts
- Approach can be templated for similar problems

### When NOT TO create a skill:
- Workflow is too simple (1-2 steps only)
- No clear repeatable pattern exists
- Task is too particular to this single use case
- Process is too variable or context-dependent to formalize
- A similar skill already exists without significant improvements

## Analysis Strategy for Multiple Conversations

When analyzing multiple conversations:

1. **Identify Common Patterns**
   - What workflow steps appear across multiple conversations?
   - What tool combinations are consistently used?
   - What problem-solving approaches are repeated?

2. **Note Variations**
   - How do users phrase similar requests differently?
   - What parameters or inputs vary between conversations?
   - Which parts of the workflow are consistent vs. variable?

3. **Assess Generalizability**
   - Can the pattern be abstracted to handle all observed cases?
   - Would the skill work for variations not yet seen?
   - Is the pattern domain-specific or more general?

## Process

1. **Analyze all conversations**
   - Identify core workflow patterns in EACH conversation
   - Look for commonalities across conversations
   - Assess overall reusability and generalizability
   - If not worth creating → **Skip to step 4**

2. **Review available skills to avoid duplication**
   - Check if similar skill already exists
   - If similar skill exists:
     * Create new version only if significant improvements can be made
     * If no significant improvement → **Skip to step 4**
 
3. **Create the skill (if appropriate)**
   - Follow skill-creator Skill guidelines strictly
   - Make it generic enough for reuse, specific enough for utility

4. **Explain your decision**
   - If creating: Describe the workflow pattern identified and why it's valuable as a reusable skill
   - If skipping: Explain clearly why no skill was created

## Conversation Histories to Analyze

{all_histories}

Proceed with the analysis and decision following the skill-creator Skill guidelines.
"""
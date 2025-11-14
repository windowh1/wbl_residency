---
name: web-research-documenter
description: This skill should be used when users request research on a topic with the intent to save findings to a document. It provides a systematic workflow for conducting web research, synthesizing information from multiple sources, and creating well-structured documentation. Trigger words include "research and save", "look up and document", "find information about and write", or any request that combines information gathering with file creation.
---

# Web Research Documenter

## Overview

This skill enables systematic web research with professional documentation output. It combines web search, content fetching, information synthesis, and structured file creation into a repeatable workflow that produces comprehensive, well-organized research documents.

## When to Use This Skill

Use this skill when users request any of the following:

- **Technology trend research**: "Research TypeScript trends and save to a file"
- **Competitive analysis**: "Look up competitors in the AI space and document findings"
- **Market research**: "Find information about electric vehicle market and write a report"
- **Tool/product comparisons**: "Compare project management tools and save the analysis"
- **Best practices documentation**: "Research React testing best practices and create a guide"
- **Academic literature reviews**: "Find recent papers on quantum computing and summarize"
- **Industry analysis**: "Research fintech trends and save to my reports folder"

**Key indicators:**
- User requests both information gathering AND file creation
- Request includes phrases like "research and save", "look up and document", "find and write"
- User specifies a file path or directory for saving results

## Research Workflow

Follow this systematic four-step workflow for all research tasks:

### Step 1: Execute Multiple Web Searches

Conduct comprehensive web searches to gather diverse perspectives and up-to-date information.

**Search strategy:**
- Start with a broad query covering the main topic
- Follow up with specific queries for recent updates, versions, or features
- Aim for 2-3 complementary searches to ensure comprehensive coverage

**Example for "TypeScript trends":**
```
Search 1: "TypeScript latest trends 2024 2025"
Search 2: "TypeScript 5.7 5.8 new features 2024"
```

**Tool usage:**
```
mcp-server-search__web_search(
  query="[main topic query]",
  max_results=10
)
```

### Step 2: Fetch Detailed Content

When search results include authoritative sources (official blogs, documentation, reputable publications), fetch the full content for deeper insights.

**Selection criteria:**
- Official documentation or blogs (e.g., Microsoft TypeScript blog)
- Recent publication dates
- High-quality sources with detailed information
- Articles that directly address the research topic

**Tool usage:**
```
mcp-server-fetch__fetch(
  url="[authoritative source URL]",
  max_length=8000
)
```

**Note:** Use start_index parameter if content is truncated and more detail is needed.

### Step 3: Synthesize Information

Create a well-structured summary that organizes findings into logical sections.

**Documentation structure:**
```
==============================================
[TOPIC] - Summary Report
Generated: [Date]
==============================================

1. [Main Category/Trend]
-----------------------------------------
• Key point 1
• Key point 2
• Key point 3

2. [Secondary Category]
-----------------------------------------
[Detailed information with sub-sections as needed]

3. [Additional Categories]
-----------------------------------------
[Continue organizing information logically]

==============================================
Sources:
- [List of primary sources]
==============================================
```

**Synthesis guidelines:**
- Use clear hierarchical headings (ASCII art dividers for main sections)
- Bullet points for scannable information
- Sub-sections for detailed features or updates
- Include specific version numbers, dates, statistics
- Credit sources at the end
- Maintain objective, informative tone

### Step 4: Save to Specified Location

Write the synthesized report to the user-specified file path.

**File writing approach:**
- Use absolute paths for reliability
- Create content in chunks (25-30 lines per write operation)
- First chunk: Use mode='rewrite' to create/overwrite file
- Subsequent chunks: Use mode='append' to add content

**Tool usage:**
```
desktop-commander__write_file(
  path="[absolute path to file]",
  content="[first 25-30 lines]",
  mode="rewrite"
)

desktop-commander__write_file(
  path="[same absolute path]",
  content="[next 25-30 lines]",
  mode="append"
)
```

**Path handling:**
- If user provides relative path, resolve to absolute path first
- Create parent directories if they don't exist
- Confirm successful write with clear user message

## Quality Standards

Ensure research output meets these quality criteria:

### Comprehensiveness
- Cover multiple aspects of the topic
- Include recent developments and historical context
- Provide specific examples, statistics, and version numbers

### Organization
- Clear section hierarchy with descriptive headings
- Logical flow from general to specific
- Scannable format with bullet points and whitespace

### Credibility
- Cite authoritative sources (official blogs, documentation)
- Include publication dates and version numbers
- Distinguish between facts and projections

### Usefulness
- Actionable insights where applicable
- Context for technical details
- Future outlook or roadmap information when available

## Example Usage

**User request:**
"Research the latest TypeScript trends and save them to results/typescript_trends.txt"

**Execution:**

1. **Web searches:**
   - "TypeScript latest trends 2024 2025" → 10 results
   - "TypeScript 5.7 5.8 new features 2024" → 10 results

2. **Fetch details:**
   - Identified official TypeScript blog post about 5.7 release
   - Fetched full content for comprehensive feature details

3. **Synthesize:**
   - Created structured report with sections:
     * GitHub popularity statistics
     * TypeScript 5.7 major features
     * Previous version highlights
     * Runtime integration improvements
     * Future roadmap (TypeScript 7.0)

4. **Save:**
   - Resolved relative path to absolute
   - Wrote 92-line comprehensive report
   - Confirmed successful save to user

**Output characteristics:**
- Professional formatting with ASCII dividers
- Hierarchical organization (7 main sections)
- Specific version numbers and dates
- Bullet points for scannable content
- Source citations at end

---
name: release-tracker
description: This skill should be used when users request information about upcoming releases, launches, or scheduled events (conferences, smartphones, games, movies, software, etc.) within a specific time period. Use this skill to systematically research, aggregate, organize chronologically, and document release information with consistent formatting.
---

# Release Tracker

## Overview

This skill enables systematic research and documentation of upcoming releases and scheduled events across various domains. It provides a structured workflow for gathering information from multiple sources, organizing it chronologically, and presenting it in a well-formatted document suitable for future reference.

## When to Use This Skill

Use this skill when users request information about:
- **Conference schedules** (e.g., "2025 AI/ML conferences")
- **Product launches** (e.g., "Q1 2025 smartphone releases")
- **Event calendars** (e.g., "upcoming tech conferences in Europe")
- **Entertainment releases** (e.g., "2025 video game releases", "upcoming movies")
- **Software releases** (e.g., "major framework updates in 2025")

**Trigger patterns:**
- "Upcoming [category] in [timeframe]"
- "Schedule of [events/releases] for [period]"
- "List of [products/events] launching in [quarter/year]"
- Requests specifying date ranges, quarters, or years for release information

## Workflow

### Step 1: Understand Requirements

Clarify with the user:
- **Topic/Domain**: What type of releases or events (conferences, phones, games, etc.)?
- **Time Period**: Specific quarter, year, or date range?
- **Output Format**: File format preference (markdown, text, CSV)?
- **Output Location**: Where to save the file?
- **Detail Level**: What information to include (dates, specs, prices, locations)?

### Step 2: Initial Broad Search

Conduct 2-3 broad web searches to identify the landscape:

**Search strategy:**
- Combine topic + timeframe + general keywords
- Use both English and local language if applicable
- Target authoritative sources (official sites, tech news, industry publications)

**Example queries:**
- `"Q1 2025" smartphone launches January February March`
- `2025 AI ML conferences schedule dates venues`
- `upcoming video game releases 2025 first half`

**Goals:**
- Identify major items/events in the category
- Discover official announcement patterns
- Find authoritative sources

### Step 3: Targeted Detail Searches

For each major item identified, conduct focused searches:

**Search strategy:**
- Search for specific names + key details (dates, specs, locations)
- Target official websites when possible
- Look for confirmation from multiple sources

**Example queries:**
- `"Samsung Galaxy S25" "January 2025" launch date specifications`
- `"ICLR 2025" dates location Singapore registration`
- `"Elden Ring DLC" release date June 2025`

**Use fetch operations:**
- When official URLs are discovered, fetch them directly for authoritative information
- Official sites typically have: release dates, specifications, registration links, schedules

### Step 4: Organize Information Chronologically

Structure the gathered information with consistent formatting:

**Organizational principles:**
- **Primary sort**: Chronological by release/event date
- **Secondary grouping**: By month, quarter, or logical category
- **Include for each entry:**
  - Name/title (clear, official naming)
  - Date (specific dates when available, otherwise month/quarter)
  - Location (for physical events) or platform (for digital releases)
  - Key details (specifications, sessions, features - domain-specific)
  - Official links (registration, purchase, information)

**Formatting guidelines:**
- Use clear headings and sections
- Include visual separators for readability
- Add summary tables when appropriate
- Include metadata (creation date, sources, caveats)

### Step 5: Create Output Document

Generate the document in the requested format and location:

**Format-specific considerations:**

**Markdown (.md):**
- Use heading hierarchy (##, ###)
- Include tables for quick reference
- Add emoji or visual markers for categories
- Use bold/italic for emphasis

**Text (.txt):**
- Use ASCII separators (===, ---)
- Maintain consistent indentation
- Use CAPITALIZATION or *markers* for emphasis

**CSV (.csv):**
- Column headers: Name, Date, Location, Category, Details, URL
- One row per item
- Escape commas in data fields

**File creation steps:**
1. Verify the target directory exists (create if needed)
2. Write content in logical chunks (not all at once if large)
3. Verify file was created successfully
4. Provide user with summary of what was documented

## Quality Standards

### Information Accuracy
- Prioritize official sources over rumors or speculation
- Mark speculative information clearly (e.g., "expected", "rumored")
- Include dates when information was gathered
- Note when official confirmation is pending

### Completeness
- Cover all major items in the requested timeframe
- Don't skip items due to incomplete information - include what's available
- Add "TBA" or "To be announced" for missing details
- Include trends or patterns observed across items

### Formatting Consistency
- Use the same structure for each entry
- Maintain consistent date formats (e.g., "January 15, 2025" or "2025-01-15")
- Apply uniform heading levels and spacing
- Include helpful navigation (table of contents for long documents)

## Example Outputs

### Conference Schedule (Markdown)
```markdown
# 2025 AI/ML Conferences

## Q1 2025

### AAAI 2025
**Date:** February 25 - March 4, 2025
**Location:** Philadelphia, PA, USA
**Focus:** General Artificial Intelligence
**Registration:** https://aaai.org/conference/aaai-25/

### ICLR 2025
**Date:** April 24-28, 2025
**Location:** Singapore EXPO, Singapore
**Focus:** Deep Learning & Representation Learning
**Format:** Hybrid (in-person + virtual)
**Registration:** https://iclr.cc/Conferences/2025/
```

### Product Launch (Text)
```
================================================================================
Q1 2025 SMARTPHONE LAUNCHES
================================================================================

JANUARY 2025
------------

OnePlus 13 Series
Launch: January 7, 2025
Models: OnePlus 13, OnePlus 13R
Processor: Snapdragon 8 Elite
Display: 6.82" LTPO AMOLED, 120Hz
Price: Starting $699 (expected)

Samsung Galaxy S25 Series  
Launch: January 22-23, 2025
Models: S25, S25+, S25 Ultra
Processor: Snapdragon 8 Elite / Exynos 2500
Display: Up to 6.9" Dynamic AMOLED
Special Features: Galaxy AI 2.0, S Pen (Ultra)
```

## Common Pitfalls to Avoid

1. **Over-reliance on single sources** - Verify information across multiple sources
2. **Outdated information** - Always check for the most recent announcements
3. **Confusing regional dates** - Clarify timezones and regional variations
4. **Missing context** - Include enough detail for readers to understand significance
5. **Incomplete searches** - Don't stop at first search; iterate to find comprehensive information
6. **Ignoring official sites** - Always attempt to fetch official websites when discovered
7. **Inconsistent formatting** - Maintain structure throughout the document

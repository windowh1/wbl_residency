# Tech Ecosystem Analyzer Skill

## Overview

A comprehensive skill for data-driven analysis of technology ecosystems. Combines web research, GitHub API metrics, quantitative scoring, and professional documentation to help teams make informed technology selection decisions.

## What This Skill Does

Transforms subjective technology selection into objective, metrics-based decision-making by:

1. **Multi-angle web research** - Gathers current trends, comparisons, and version updates
2. **Automated GitHub data collection** - Fetches stars, forks, growth rates, and activity metrics
3. **Quantitative analysis** - Calculates popularity scores and growth trajectories
4. **Comprehensive reporting** - Produces structured Markdown reports with actionable recommendations
5. **Data preservation** - Exports raw JSON data for further analysis

## When to Use

Perfect for:
- Comparing multiple libraries/frameworks (React state management, testing tools, etc.)
- Technology stack evaluation for new projects
- Migration decisions (Redux → Zustand, etc.)
- Ecosystem trend monitoring
- Competitive technical analysis
- Open source project health assessment

## Output

Each analysis produces three files:

1. **`[ecosystem]_analysis.md`** - Comprehensive report (typically 25-30 KB)
   - Executive summary with key findings
   - GitHub metrics rankings
   - Detailed library profiles
   - Comparative analysis tables
   - Top 3 recommendations with rationale
   - Trend predictions and scenarios
   - Actionable implementation guides
   - Learning resources

2. **`[ecosystem]_data.json`** - Raw metrics
   - Stars, forks, issues, watchers
   - Popularity scores
   - Growth rate calculations
   - All repository metadata

3. **`collect_github_data.py`** - Reusable script
   - Customizable for other ecosystems
   - Automated API fetching
   - Scoring algorithm implementation

## Example Usage

### React State Management Analysis
```
User: "Analyze React state management ecosystem: Redux, Zustand, Jotai, TanStack Query"

Output:
- 715-line comprehensive report
- Quantitative rankings (TanStack Query: 62.5/100, Zustand: 64.13/100, etc.)
- Growth predictions (Zustand to overtake Redux by 2026)
- Project-specific recommendations (startup vs enterprise)
- Migration strategies with ROI estimates
```

### Python ML Libraries Comparison
```
User: "Compare Python ML libraries for a new data science project"

Output:
- Analysis of TensorFlow, PyTorch, JAX, scikit-learn, etc.
- Performance benchmarks from community sources
- Ecosystem integration patterns
- When to use each framework
- Learning curve assessments
```

## Key Features

- **Quantitative Rankings**: Popularity scores based on weighted GitHub metrics
- **Growth Analysis**: Trends and predictions with probability estimates
- **Visual Formatting**: Tables, ASCII art, emoji for scannability
- **Decision Frameworks**: Project-size-specific recommendations
- **Migration Guides**: Step-by-step strategies with ROI projections
- **No Bias**: Data-driven analysis, not opinion-based

## Skill Components

### SKILL.md
Complete workflow documentation with:
- 6-step systematic process
- Quality standards checklist
- Advanced techniques (custom scoring, multi-dimensional analysis)
- Common pitfalls to avoid
- Integration with other skills

### scripts/collect_github_data.py
Reusable Python template featuring:
- GitHub API integration
- Popularity scoring algorithm
- Growth rate estimation
- JSON export
- Console rankings
- Easy customization (just edit LIBRARIES dict)

### references/report_template.md
Professional report structure with:
- 9 major sections
- Visual formatting guidelines
- Comparative analysis tables
- Actionable recommendations framework
- Data source documentation

## Requirements

- **Python 3.x** with `requests` library
- **GitHub API access** (no authentication required for public repos)
- **desktop-commander MCP** for file operations and process execution
- **Web search access** (mcp-server-search or similar)

## Customization

The skill is highly adaptable:

- **Adjust scoring weights**: Modify `WEIGHTS` dict based on ecosystem characteristics
- **Custom metrics**: Add bundle size, performance benchmarks, TypeScript support
- **Ecosystem-specific**: Tune `MAX_STARS` and growth thresholds
- **Report sections**: Add/remove sections based on user needs

## Maintenance

Keep the skill current by:
- Updating max_stars/max_forks for growing ecosystems
- Refining growth rate thresholds as communities mature
- Adjusting weights based on real-world adoption patterns
- Monitoring GitHub API changes

## Comparison with Other Skills

**vs. web-research-documenter:**
- web-research: Qualitative research → documentation
- tech-ecosystem: Quantitative metrics + research → data-driven analysis

**vs. generic search:**
- Generic: Find information
- tech-ecosystem: Collect data, analyze, score, rank, and recommend

## License

See LICENSE.txt for complete terms.

## Version

1.0.0 - Initial release (January 2025)

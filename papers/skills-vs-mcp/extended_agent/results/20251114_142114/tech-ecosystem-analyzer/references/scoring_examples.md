# Scoring Algorithm Examples

This document provides examples of how the popularity scoring algorithm works in practice.

## Algorithm Overview

The scoring algorithm uses a weighted combination of four metrics, normalized to a 0-100 scale:

```python
WEIGHTS = {
    "stars": 0.4,           # 40% - Primary popularity indicator
    "forks": 0.2,           # 20% - Community contribution
    "watchers": 0.1,        # 10% - Active monitoring
    "recent_activity": 0.3  # 30% - Maintenance health
}
```

## Scoring Examples

### Example 1: Mature, Highly Popular Library (Redux)

**Raw Metrics:**
- Stars: 61,392
- Forks: 15,187
- Watchers: 61,392
- Last Updated: 2 days ago

**Normalization (assuming max_stars=100K, max_forks=20K, max_watchers=10K):**
- Star score: min(61,392/100,000, 1.0) × 0.4 = 0.614 × 0.4 = 0.246
- Fork score: min(15,187/20,000, 1.0) × 0.2 = 0.759 × 0.2 = 0.152
- Watcher score: min(61,392/10,000, 1.0) × 0.1 = 1.0 × 0.1 = 0.100
- Activity score: (1 - 2/365) × 0.3 = 0.995 × 0.3 = 0.298

**Total Score:** (0.246 + 0.152 + 0.100 + 0.298) × 100 = **79.6/100**

**Interpretation:** Excellent score driven by high absolute numbers and active maintenance.


### Example 2: Fast-Growing Medium Library (Zustand)

**Raw Metrics:**
- Stars: 55,675
- Forks: 1,861
- Watchers: 55,675
- Last Updated: 1 day ago

**Normalization:**
- Star score: min(55,675/100,000, 1.0) × 0.4 = 0.557 × 0.4 = 0.223
- Fork score: min(1,861/20,000, 1.0) × 0.2 = 0.093 × 0.2 = 0.019
- Watcher score: min(55,675/10,000, 1.0) × 0.1 = 1.0 × 0.1 = 0.100
- Activity score: (1 - 1/365) × 0.3 = 0.997 × 0.3 = 0.299

**Total Score:** (0.223 + 0.019 + 0.100 + 0.299) × 100 = **64.1/100**

**Interpretation:** Good score despite lower forks (indicates simpler API). Very recent activity helps.


### Example 3: Smaller Emerging Library (Jotai)

**Raw Metrics:**
- Stars: 20,730
- Forks: 697
- Watchers: 20,730
- Last Updated: 3 days ago

**Normalization:**
- Star score: min(20,730/100,000, 1.0) × 0.4 = 0.207 × 0.4 = 0.083
- Fork score: min(697/20,000, 1.0) × 0.2 = 0.035 × 0.2 = 0.007
- Watcher score: min(20,730/10,000, 1.0) × 0.1 = 1.0 × 0.1 = 0.100
- Activity score: (1 - 3/365) × 0.3 = 0.992 × 0.3 = 0.298

**Total Score:** (0.083 + 0.007 + 0.100 + 0.298) × 100 = **48.8/100**

**Interpretation:** Moderate score. Lower absolute numbers but excellent activity keeps it competitive.


### Example 4: Stale Legacy Library (Hypothetical)

**Raw Metrics:**
- Stars: 45,000
- Forks: 8,000
- Watchers: 5,000
- Last Updated: 180 days ago

**Normalization:**
- Star score: min(45,000/100,000, 1.0) × 0.4 = 0.45 × 0.4 = 0.180
- Fork score: min(8,000/20,000, 1.0) × 0.2 = 0.40 × 0.2 = 0.080
- Watcher score: min(5,000/10,000, 1.0) × 0.1 = 0.50 × 0.1 = 0.050
- Activity score: (1 - 180/365) × 0.3 = 0.507 × 0.3 = 0.152

**Total Score:** (0.180 + 0.080 + 0.050 + 0.152) × 100 = **46.2/100**

**Interpretation:** Decent stars but poor activity score significantly drags down total. Red flag for maintenance.


## Growth Rate Examples

Growth rate is calculated as: `stars / (days_since_creation)`

### Very High Growth (50+ stars/day)
- **Example:** New framework with explosive adoption
- Stars: 36,500 | Age: 2 years (730 days)
- Rate: 36,500 / 730 = **50 stars/day**
- Interpretation: Viral adoption, major hype cycle

### High Growth (20-50 stars/day)
- **Example:** TanStack Query
- Stars: 47,367 | Age: ~5.2 years (1,900 days)
- Rate: 47,367 / 1,900 = **25 stars/day**
- Interpretation: Sustained strong growth, becoming standard

### Medium Growth (5-20 stars/day)
- **Example:** Redux
- Stars: 61,392 | Age: ~9.5 years (3,467 days)
- Rate: 61,392 / 3,467 = **18 stars/day**
- Interpretation: Mature but still growing steadily

### Low Growth (<5 stars/day)
- **Example:** Older utility library
- Stars: 5,000 | Age: ~8 years (2,920 days)
- Rate: 5,000 / 2,920 = **1.7 stars/day**
- Interpretation: Maintenance mode or niche use case


## Adjusting Maximums for Different Ecosystems

The `MAX_STARS`, `MAX_FORKS`, and `MAX_WATCHERS` should be tuned to your specific ecosystem:

### Frontend Framework Ecosystem (Large)
```python
MAX_STARS = 200000    # React has ~220K
MAX_FORKS = 40000     # React has ~45K
MAX_WATCHERS = 20000
```

### State Management Libraries (Medium)
```python
MAX_STARS = 100000    # Redux at ~61K
MAX_FORKS = 20000     # Redux at ~15K
MAX_WATCHERS = 10000
```

### Niche Tool Ecosystem (Small)
```python
MAX_STARS = 20000
MAX_FORKS = 3000
MAX_WATCHERS = 2000
```

**Rule of thumb:** Set maximums ~1.5-2× the highest expected library to avoid ceiling effects.


## Custom Weights for Different Contexts

### Enterprise/Stability Focus
```python
WEIGHTS = {
    "stars": 0.3,           # Less emphasis on popularity
    "forks": 0.3,           # More emphasis on contributions
    "watchers": 0.1,
    "recent_activity": 0.3  # Maintenance critical
}
```

### Innovation/Growth Focus
```python
WEIGHTS = {
    "stars": 0.3,
    "forks": 0.1,
    "watchers": 0.1,
    "recent_activity": 0.5  # Heavy emphasis on activity
}
```

### Community/Contribution Focus
```python
WEIGHTS = {
    "stars": 0.3,
    "forks": 0.4,           # Value community contributions
    "watchers": 0.1,
    "recent_activity": 0.2
}
```


## Interpreting Scores

**90-100:** Exceptional - Top tier, widely adopted, actively maintained
**75-89:** Excellent - Strong choice, proven track record
**60-74:** Good - Solid option, may be growing or specialized
**45-59:** Moderate - Viable for specific use cases, watch for activity
**30-44:** Concerning - Limited adoption or poor maintenance
**<30:** Red Flag - Consider alternatives unless highly specialized need

# GTO Assistant - Cost-Optimized Analysis

## Quick Start

### 1. Run GTO Analysis (Free)
```bash
make gto
```
This analyzes all hands with GTO+ solver and calculates deviation scores.

### 2. Check Results
```bash
make list
```
See which hands have the highest deviation scores (most interesting for learning).

### 3. Run AI Analysis on Best Hands (Paid)
```bash
make ai-top3        # Analyze top 3 hands
make ai-min         # Analyze hands above threshold
make ai-hands       # Select specific hands
```

### 4. View Results
```bash
make visualize      # Web interface at localhost:8081
```

## Cost Savings

**Before**: All hands → ChatGPT = $5-25+ per session
**After**: Only interesting hands → ChatGPT = $0.75-2 per session

## Commands Summary

| Command | Purpose | Cost |
|---------|---------|------|
| `make gto` | GTO+ analysis only | Free |
| `make list` | View deviation scores | Free |
| `make ai-top3` | AI on top 3 hands | ~$0.75 |
| `make ai-min` | AI above threshold | Variable |
| `make visualize` | Web viewer | Free |

## Deviation Scores

- **0.0-0.5**: Standard play
- **0.5-1.0**: Minor deviations  
- **1.0-2.0**: Good for analysis
- **2.0+**: Major learning opportunities

Focus your AI analysis budget on hands with scores ≥ 1.0 for maximum learning value.

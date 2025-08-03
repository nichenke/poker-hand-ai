# Cost-Optimized Poker Analysis Workflow

## Overview

The GTO Assistant now supports a **two-step workflow** that optimizes ChatGPT API usage costs by only running AI analysis on the most interesting hands with significant GTO deviations.

## Why This Matters

- **ChatGPT API is expensive**: Each analysis can cost $0.10-0.50+ depending on hand complexity
- **Most hands are standard**: Many poker hands follow basic GTO with minimal learning value
- **Focus on deviations**: Hands with large GTO deviations provide the most educational value

## Two-Step Workflow

### Step 1: GTO+ Analysis Only (Free)
```bash
# Run GTO+ solver analysis on all hands
make gto
# or
pipenv run python gto_cli.py gto
```

**What happens:**
- Parses all hand files in `hands/` directory
- Submits each hand to remote GTO+ solver
- Calculates "deviation scores" based on EV analysis and frequency patterns
- Saves GTO-only results to `exports/gto_analysis_*.json`
- Shows top hands by deviation score

### Step 2: AI Analysis on Selected Hands (Paid)
```bash
# Option A: Analyze top 3 hands by deviation
make ai-top3

# Option B: Analyze hands above threshold
make ai-min  # prompts for minimum deviation score

# Option C: Analyze specific hands
make ai-hands  # prompts for hand IDs

# Option D: CLI with direct parameters
pipenv run python gto_cli.py ai --top 3
pipenv run python gto_cli.py ai --min 1.5
pipenv run python gto_cli.py ai --hands "123,456,789"
```

**What happens:**
- Loads existing GTO analysis results
- Filters hands by deviation score or selection
- Runs ChatGPT analysis only on selected hands
- Saves complete analysis to `exports/analysis_*.json`

## Deviation Score System

The system calculates a "deviation score" for each hand based on:

- **EV Analysis**: Negative EV indicates suboptimal play (higher score)
- **Frequency Patterns**: Pure strategies (0% or 100%) and mixed strategies (30-70%) are interesting
- **Range Analysis**: Significant deviations from GTO recommendations

**Score Interpretation:**
- `0.0-0.5`: Standard play, minimal learning value
- `0.5-1.0`: Minor deviations, possible teaching moments  
- `1.0-2.0`: Significant deviations, good for analysis
- `2.0+`: Major mistakes or complex spots, high learning value

## Workflow Examples

### Basic Usage
```bash
# 1. Add hand files to hands/ directory
# 2. Run GTO analysis
make gto

# 3. Check results
make list

# 4. Analyze most interesting hands
make ai-top3

# 5. View results
make visualize
```

### Advanced Selection
```bash
# Run GTO analysis
pipenv run python gto_cli.py gto

# List all results with scores ≥ 1.0
pipenv run python gto_cli.py list 1.0

# Analyze specific hands that look interesting
pipenv run python gto_cli.py ai --hands "2517850956,2517851234"

# View results in web interface
make visualize
```

## Cost Savings Examples

### Scenario 1: 20 Hands
- **Old workflow**: 20 hands × $0.25 = **$5.00**
- **New workflow**: Only analyze top 3 hands = **$0.75** (85% savings)

### Scenario 2: 100 Hands  
- **Old workflow**: 100 hands × $0.25 = **$25.00**
- **New workflow**: Only analyze hands with deviation ≥ 1.0 (maybe 8 hands) = **$2.00** (92% savings)

## Files Created

### GTO-Only Analysis
- `exports/gto_analysis_{hand_id}_{timestamp}.json`
- Contains: hand data, solver results, deviation score
- No AI analysis (saves costs)

### Complete Analysis  
- `exports/analysis_{hand_id}_{timestamp}.json`
- Contains: hand data, solver results, deviation score, AI analysis
- Full ChatGPT analysis with visual formatting

## Commands Reference

### Make Commands
```bash
make gto           # Step 1: GTO analysis only
make list          # View deviation scores
make ai-top3       # Top 3 hands by deviation
make ai-min        # Hands above threshold
make ai-hands      # Specific hand selection
make visualize     # Web interface
```

### CLI Commands
```bash
pipenv run python gto_cli.py gto
pipenv run python gto_cli.py list [min_deviation]
pipenv run python gto_cli.py ai --top N
pipenv run python gto_cli.py ai --min SCORE  
pipenv run python gto_cli.py ai --hands "ID1,ID2"
```

### Interactive Mode
```bash
make run           # Full interactive menu
pipenv run python gto_assistant_preloaded.py
```

## Legacy Mode

The old "analyze everything" workflow is still available:

```bash
# Interactive mode -> option 4
make run

# Direct CLI (not recommended for cost)
# Will prompt for confirmation
pipenv run python gto_cli.py full
```

## Best Practices

1. **Always run GTO analysis first** to see deviation scores
2. **Set a deviation threshold** (e.g., 1.0) to focus on interesting hands
3. **Review results** with `make list` before running expensive AI analysis
4. **Use web visualizer** to review analysis quality and adjust thresholds
5. **Start conservative** with small selections until you understand your data

## Integration with Existing Features

- **Debug logging**: All logs saved to `debug/` folder regardless of workflow
- **Web visualizer**: Works with both GTO-only and complete analysis files
- **Visual formatting**: AI analysis still uses emojis and suit symbols
- **Hero focus**: AI analysis still focuses exclusively on Roughneck7's play

This workflow maintains all existing functionality while dramatically reducing API costs by focusing analysis where it matters most.

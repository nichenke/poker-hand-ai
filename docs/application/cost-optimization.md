# Cost Optimization Guide

Optimize your ChatGPT API costs with smart analysis workflows that focus on the most valuable hands.

## 💰 Why This Matters

- **API costs add up**: Each hand analysis can cost $0.10-0.50+
- **Most hands are routine**: Standard GTO play has minimal learning value
- **Focus on deviations**: Hands with significant mistakes provide the most education

## 🔄 Two-Step Workflow

### Step 1: GTO Analysis Only (Free)

```bash
# Analyze all hands with GTO+ solver
make gto
```

**What happens:**
- Processes all hands in `hands/` directory
- Calculates deviation scores based on EV and frequency analysis
- Saves GTO-only results (no AI costs)
- Identifies the most interesting hands

### Step 2: AI Analysis on Selected Hands (Paid)

```bash
# Option A: Top hands by deviation
make ai-top3

# Option B: Hands above threshold
make ai-min  # prompts for minimum score

# Option C: Specific hands
make ai-hands  # prompts for hand IDs
```

**What happens:**
- Loads existing GTO analysis
- Runs AI analysis only on selected hands
- Creates complete analysis with strategic insights

## 📊 Deviation Score System

The system automatically calculates deviation scores:

- **0.0-0.5**: Standard play, minimal learning value
- **0.5-1.0**: Minor deviations, possible teaching moments
- **1.0-2.0**: Significant deviations, good for analysis
- **2.0+**: Major mistakes or complex spots, high value

**Factors considered:**
- EV losses from suboptimal play
- Frequency deviations from GTO recommendations
- Range construction errors
- Betting size mistakes

## 💡 Usage Examples

### Basic Workflow

```bash
# 1. Run GTO analysis
make gto

# 2. Review results
make list

# 3. Analyze top hands
make ai-top3

# 4. View in web interface
make visualize
```

### Advanced Selection

```bash
# List hands with deviation ≥ 1.0
pipenv run python gto_cli.py list 1.0

# Analyze specific interesting hands
pipenv run python gto_cli.py ai --hands "123,456,789"

# Set custom threshold
pipenv run python gto_cli.py ai --min 1.5
```

## 💸 Cost Savings Examples

### Small Session (20 hands)
- **Traditional**: 20 × $0.25 = **$5.00**
- **Optimized**: Top 3 hands = **$0.75** (85% savings)

### Large Session (100 hands)
- **Traditional**: 100 × $0.25 = **$25.00**
- **Optimized**: 8 hands above threshold = **$2.00** (92% savings)

## 📁 Output Files

### GTO-Only Analysis
```
exports/gto_analysis_{hand_id}_{timestamp}.json
```
- Hand data and solver results
- Deviation scores
- No AI analysis (cost-free)

### Complete Analysis
```
exports/analysis_{hand_id}_{timestamp}.json
```
- All GTO data plus AI insights
- Strategic commentary
- Learning recommendations

## 🛠️ Command Reference

### Make Commands

```bash
make gto           # GTO analysis only
make list          # View deviation scores
make ai-top3       # Top 3 by deviation
make ai-min        # Above threshold
make ai-hands      # Specific selection
make visualize     # Web interface
```

### CLI Commands

```bash
# GTO analysis
pipenv run python gto_cli.py gto

# List with optional minimum score
pipenv run python gto_cli.py list [min_score]

# AI analysis options
pipenv run python gto_cli.py ai --top 3
pipenv run python gto_cli.py ai --min 1.5
pipenv run python gto_cli.py ai --hands "123,456"
```

## 🎯 Best Practices

1. **Always start with GTO analysis** to see deviation scores
2. **Set realistic thresholds** (1.0+ for learning, 1.5+ for major mistakes)
3. **Review scores before AI analysis** with `make list`
4. **Use the web visualizer** to assess analysis quality
5. **Start conservative** with small selections

## 🔄 Legacy Support

The original "analyze everything" workflow remains available:

```bash
# Interactive mode
make run  # Choose option 4

# Direct CLI (with cost warning)
pipenv run python gto_cli.py full
```

## 📈 Integration Notes

- **Works with all existing features**: Debug logs, web visualizer, visual formatting
- **Maintains hero focus**: AI analysis still centers on your play
- **Preserves hand context**: Full hand history available in both modes
- **Backward compatible**: Existing analysis files work normally

This optimization maintains full functionality while dramatically reducing API costs by focusing analysis where it provides the most value.

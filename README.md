# GTO Assistant

Automated poker hand analysis using remote GTO+ solver and AI-powered insights.

## 🚀 Quick Start

Get up and running in 5 minutes with a local Windows VM:

```bash
# 1. Clone repository
git clone https://github.com/nichenke/poker-hand-ai.git
cd poker-hand-ai

# 2. Follow the quick setup guide
open docs/application/quickstart.md

# 3. Run analysis
make run
```

## ✨ Features

- **🔄 Two-Step Workflow**: Cost-optimized analysis focusing on high-value hands
- **🖥️ Remote GTO+ Integration**: Windows-based solver with automated deployment
- **🤖 AI Analysis**: Strategic insights powered by GPT-4o
- **🌐 Web Interface**: ChatGPT-like visualizer for results
- **⚡ Infrastructure Automation**: One-command deployment with Ansible
- **🔧 Remote Development**: VS Code SSH integration for seamless editing

## 🏗️ Architecture

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Development   │    │   Windows Node   │    │   OpenAI API    │
│   (Mac/Linux)   │───▶│   (GTO+ Solver)  │    │   (Analysis)    │
│                 │    │                  │    │                 │
│ • Python Client │    │ • GTO+ Software  │    │ • GPT-4o        │
│ • Web Interface │    │ • Flask API      │    │ • Strategic     │
│ • Hand Files    │    │ • Solver Engine  │    │   Insights      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎯 Workflow Options

### Cost-Optimized (Recommended)

```bash
# Step 1: GTO analysis only (free)
make gto

# Step 2: AI analysis on interesting hands (paid)
make ai-top3        # Analyze top 3 hands by deviation
make ai-min         # Analyze hands above threshold
```

### Traditional

```bash
# Analyze everything (higher cost)
make run
```

### Web Interface

```bash
# View results in browser
make visualize
```

## 📖 Documentation

- **[📚 Getting Started](docs/application/quickstart.md)** - 5-minute setup guide
- **[⚙️ System Requirements](docs/REQUIREMENTS.md)** - Complete hardware and software requirements  
- **[💰 Cost Optimization](docs/application/cost-optimization.md)** - Reduce API costs
- **[⚙️ Installation](docs/application/installation.md)** - Complete setup instructions
- **[🏗️ Infrastructure](docs/infrastructure/overview.md)** - Deployment options
- **[🔧 Development](docs/development/setup.md)** - Contributing guide

## 💡 Example Usage

```bash
# Add your hand files
cp your_hands/*.txt hands/

# Run GTO analysis to find interesting hands
make gto

# View deviation scores
make list

# Analyze only the most valuable hands
make ai-top3

# View results in web interface
make visualize
```

## 🛠️ Development Commands

| Command | Description |
|---------|-------------|
| `make run` | Interactive analysis (full workflow) |
| `make gto` | GTO+ analysis only (cost-free) |
| `make ai-top3` | AI analysis on top 3 hands |
| `make visualize` | Start web interface |
| `make test-windows` | Test Windows node connection |
| `make setup-windows` | Deploy infrastructure |
| `make help` | Show all available commands |

## 🎮 Live Demo

1. **Add sample hands** to `hands/` directory
2. **Run GTO analysis**: `make gto`
3. **Check results**: `make list`
4. **Analyze top hands**: `make ai-top3`
5. **View in browser**: `make visualize`

## 📁 Project Structure

```
poker-hand-ai/
├── 📄 README.md                 # This file
├── 📁 docs/                     # Documentation
├── 📁 hands/                    # Your hand history files
├── 📁 exports/                  # Analysis results
├── 📁 ansible/                  # Infrastructure automation
├── 🐍 gto_assistant_preloaded.py # Main application
└── 📋 Makefile                  # Build commands
```

## 🚀 Deployment Options

- **🏠 Local VM**: Quick setup with Windows 11 VM
- **☁️ AWS/Azure**: Scalable cloud deployment  
- **🖥️ Dedicated Server**: High-performance option

## 🎯 Next Steps

1. **[Start Here](docs/application/quickstart.md)** - Quick 5-minute setup
2. **[Optimize Costs](docs/application/cost-optimization.md)** - Save on API usage
3. **[Infrastructure](docs/infrastructure/overview.md)** - Deployment options
4. **[Development](docs/development/setup.md)** - Contributing guide

---

*Built with ❤️ for poker players who want to improve their game through data-driven analysis.*

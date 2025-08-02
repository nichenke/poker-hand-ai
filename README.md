# GTO Assistant - Automated Poker Analysis Pipeline

An automated system for analyzing poker hands using remote GTO+ solver and AI-powered insights.

## 🚀 Features

- **Batch Processing**: Analyze multiple hands from files
- **Remote GTO+ Integration**: Leverage Windows-based GTO+ solver via API
- **AI Analysis**: Deep strategic insights using GPT-4o
- **Export Pipeline**: Complete analysis results in JSON format
- **Infrastructure Automation**: Cloud deployment scripts included
- **Clean Architecture**: File-based processing with no hardcoded examples

## 🏗️ Architecture Options

**Option 1: Local Windows VM (Recommended for Home Lab)**
```
Mac (Development) → Local Windows 11 VM → Analysis Pipeline
```

**Option 2: Cloud Infrastructure**
```
Mac (Development) → AWS/Azure Windows Node → Analysis Pipeline
```

## Prerequisites

- Python 3.13
- pipenv installed (`brew install pipenv`)
- OpenAI API Key
- Remote Windows node with GTO+ (see INFRASTRUCTURE.md)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nichenke/poker-hand-ai.git
   cd poker-hand-ai
   ```

2. **Setup environment:**
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   echo "GTO_SOLVER_URL=http://your-windows-node:8080" >> .env
   ```

3. **Add hand files:**
   ```bash
   # Place hand history files in hands/ directory
   cp your_hands/*.txt hands/
   ```

4. **Run analysis:**
   ```bash
   make run
   ```

## Makefile Commands

- `make run` - Install dependencies and run the GTO assistant (default)
- `make install` - Install dependencies only
- `make check` - Check environment setup and verify dependencies
- `make security` - Run security vulnerability checks
- `make clean` - Remove pipenv environment
- `make help` - Show available commands

## Manual Setup (Alternative)

If you prefer not to use the Makefile:

1. **Install dependencies:**
   ```bash
   pipenv install
   ```

2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Run the script:**
   ```bash
   pipenv run python gto_assistant_preloaded.py
   ```

## Alternative: Using pipenv shell

You can also activate the pipenv environment and run commands directly:

```bash
# Activate the pipenv shell
pipenv shell

# Set API key (if not set globally)
export OPENAI_API_KEY="your-api-key-here"

# Run the script
python gto_assistant_preloaded.py

# Exit the shell when done
exit
```

## Project Structure

- `Pipfile` - Dependency specification
- `Pipfile.lock` - Locked dependency versions
- `gto_assistant_preloaded.py` - Main script
- `exports/` - Directory for exported hand histories

## Features

- ✅ Modern OpenAI API integration
- ✅ Hand history export to JSON
- ✅ GTO analysis using GPT-4o
- ✅ Pipenv dependency management

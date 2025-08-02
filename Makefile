# GTO Assistant Makefile
# Requires: pipenv, .env file with OPENAI_API_KEY

.PHONY: run install check clean help security setup-hands demo setup-windows test-windows

# Default target
run: install setup-hands
	@echo "Running GTO Assistant..."
	@bash -c 'set -a; source .env; set +a; pipenv run python gto_assistant_preloaded.py'

# Install dependencies
install:
	@echo "Installing dependencies with pipenv..."
	@pipenv install

# Setup hands directory and sample files
setup-hands:
	@echo "Setting up hands directory..."
	@mkdir -p hands
	@test -f hands/sample_hand_001.txt || echo "Add your hand history files to hands/ directory"

# Run demo with mock solver (for testing without Windows node)
demo:
	@echo "Running demo mode (mock solver)..."
	@export GTO_SOLVER_URL="http://mock-solver" && pipenv run python gto_assistant_preloaded.py

# Setup Windows VM with Ansible
setup-windows:
	@echo "Setting up Windows VM with Ansible..."
	@echo "Make sure to update ansible/inventory.yml with your VM details first!"
	@OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES pipenv run ansible-galaxy collection install ansible.windows
	@OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES pipenv run ansible-playbook ansible/setup-gto-solver.yml

# Test Windows VM connection
test-windows:
	@echo "Testing connection to Windows VM..."
	@OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES pipenv run ansible gto-solver -m win_ping -i ansible/inventory.yml

# Check environment and dependencies
check:
	@echo "Checking pipenv environment..."
	@pipenv --version
	@echo "Verifying dependencies..."
	@pipenv verify || echo "⚠️  Dependencies may need updating"
	@echo "Checking if .env file exists..."
	@test -f .env && echo "✅ .env file found" || echo "❌ .env file not found! Please create .env with OPENAI_API_KEY"
	@echo "Checking Python version..."
	@pipenv run python --version

# Clean pipenv environment
clean:
	@echo "Cleaning pipenv environment..."
	@pipenv --rm 2>/dev/null || echo "No environment to remove"

# Security check (alternative to deprecated pipenv check)
security:
	@echo "Running security checks..."
	@pipenv install --dev safety 2>/dev/null || echo "Installing safety..."
	@pipenv run safety check --json || echo "⚠️  Security check completed with warnings"

# Show help
help:
	@echo "GTO Assistant - Available commands:"
	@echo ""
	@echo "  make run           - Install deps, setup hands, and run analysis"
	@echo "  make install       - Install dependencies"
	@echo "  make setup-hands   - Create hands directory structure"
	@echo "  make demo          - Run with mock solver (for testing)"
	@echo "  make setup-windows - Setup Windows VM with Ansible"
	@echo "  make test-windows  - Test connection to Windows VM"
	@echo "  make check         - Check environment setup"
	@echo "  make security      - Run security vulnerability checks"
	@echo "  make clean         - Remove pipenv environment"
	@echo "  make help          - Show this help message"
	@echo ""
	@echo "Environment Variables:"
	@echo "  GTO_SOLVER_URL     - URL of remote Windows GTO+ node"
	@echo "  OPENAI_API_KEY     - Your OpenAI API key (in .env file)"
	@echo ""
	@echo "Directory Structure:"
	@echo "  hands/             - Place hand history files here (.txt format)"
	@echo "  exports/           - Analysis results saved here (.json format)"
	@echo "  ansible/           - Ansible playbooks for Windows VM setup"
	@echo ""
	@echo "Documentation:"
	@echo "  INFRASTRUCTURE.md     - Cloud infrastructure setup"
	@echo "  LOCAL_WINDOWS_SETUP.md - Local Windows VM setup guide"
	@echo "  QUICKSTART.md         - 5-minute setup instructions"

# GTO Assistant Makefile
# Requires: pipenv, .env file with OPENAI_API_KEY

.PHONY: run install check clean help security setup-hands demo setup-windows setup-windows-system setup-windows-service test-windows visualize gto ai list

# Default target - interactive mode
run: 
	@echo "Running GTO Assistant (Interactive Mode)..."
	@pipenv run python gto_assistant_preloaded.py

# Step 1: Run GTO+ analysis only (cost-optimized)
gto:
	@echo "Running GTO+ analysis only (Step 1)..."
	@pipenv run python gto_cli.py gto

# Step 2: Run AI analysis on selected hands
ai:
	@echo "Available AI analysis options:"
	@echo "  make ai-top3      - Analyze top 3 hands by deviation"
	@echo "  make ai-min       - Analyze hands above deviation threshold"
	@echo "  make ai-hands     - Analyze specific hand IDs"
	@echo ""
	@echo "Or use CLI directly:"
	@echo "  pipenv run python gto_cli.py ai --top 3"
	@echo "  pipenv run python gto_cli.py ai --min 1.5"
	@echo "  pipenv run python gto_cli.py ai --hands '123,456'"

# AI analysis shortcuts
ai-top3:
	@echo "Running AI analysis on top 3 hands by deviation..."
	@pipenv run python gto_cli.py ai --top 3

ai-min:
	@echo "Enter minimum deviation score (e.g., 1.0):"
	@read min && pipenv run python gto_cli.py ai --min $$min

ai-hands:
	@echo "Enter comma-separated hand IDs (e.g., 123,456):"
	@read hands && pipenv run python gto_cli.py ai --hands "$$hands"

# List GTO results with deviation scores
list:
	@echo "Listing GTO analysis results..."
	@pipenv run python gto_cli.py list

# Start web visualizer
visualize:
	@echo "Starting GTO Analysis Visualizer..."
	@echo "Open browser to: http://localhost:8081"
	@pipenv run python visualizer.py

# Install dependencies
install:
	@echo "Installing dependencies with pipenv..."
	@pipenv install

# Setup hands directory and sample files
setup-hands:
	@echo "Setting up hands directory..."
	@mkdir -p hands
	@test -f hands/sample_hand_001.txt || echo "Add your hand history files to hands/ directory"

# Setup Windows VM with Ansible
setup-windows:
	@echo "Setting up Windows VM with Ansible..."
	@echo "Make sure to update ansible/inventory.yml with your VM details first!"
	@OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES pipenv run ansible-galaxy collection install ansible.windows
	@OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES pipenv run ansible-playbook -i ansible/inventory.yml ansible/setup-gto-solver.yml

# Setup Windows system configuration only (firewall, performance)
setup-windows-system:
	@echo "Setting up Windows system configuration for GTO+..."
	@echo "Configuring firewall, performance optimizations, and system settings..."
	@OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES pipenv run ansible-playbook -i ansible/inventory.yml ansible/ansible-gto-setup.yml

# Setup GTO+ service management only (scripts, monitoring)
setup-windows-service:
	@echo "Setting up GTO+ service management..."
	@echo "Installing service scripts, monitoring, and scheduled tasks..."
	@OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES pipenv run ansible-playbook -i ansible/inventory.yml ansible/ansible-gto-service.yml

# Test Windows VM connection
test-windows:
	@echo "Testing connection to Windows VM..."
	@OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES pipenv run ansible gto-solver -m win_ping -i ansible/inventory.yml

# Test remote GTO service
test-service:
	@echo "Testing remote GTO service..."
	@pipenv run python test-remote-service.py

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
	@echo "COST-OPTIMIZED WORKFLOW (Recommended):"
	@echo "  make gto           - Step 1: Run GTO+ analysis only (free)"
	@echo "  make list          - View results with deviation scores"
	@echo "  make ai-top3       - Step 2: AI analysis on top 3 hands ($$)"
	@echo "  make ai-min        - Step 2: AI analysis above threshold ($$)"
	@echo "  make ai-hands      - Step 2: AI analysis on specific hands ($$)"
	@echo ""
	@echo "WINDOWS SERVER SETUP (Modular):"
	@echo "  make setup-windows-system  - Configure firewall & performance only"
	@echo "  make setup-windows-service - Install service scripts & monitoring only"
	@echo "  make test-windows          - Test connection to Windows servers"
	@echo ""
	@echo "OTHER COMMANDS:"
	@echo "  make run           - Interactive mode with all options"
	@echo "  make visualize     - Start web visualizer for results"
	@echo "  make install       - Install dependencies"
	@echo "  make setup-hands   - Create hands directory structure"
	@echo "  make setup-windows - Setup Windows VM with Ansible (legacy)"
	@echo "  make setup-windows-system  - Setup Windows system configuration only"
	@echo "  make setup-windows-service - Setup GTO+ service management only"
	@echo "  make test-windows  - Test connection to Windows VM"
	@echo "  make check         - Check environment setup"
	@echo "  make security      - Run security vulnerability checks"
	@echo "  make clean         - Remove pipenv environment"
	@echo ""
	@echo "WORKFLOW EXAMPLE:"
	@echo "  1. Add hand files to hands/ directory"
	@echo "  2. make gto        # Run GTO analysis"
	@echo "  3. make list       # Check deviation scores"
	@echo "  4. make ai-top3    # AI analysis on most interesting hands"
	@echo "  5. make visualize  # View results in web browser"
	@echo ""
	@echo "WINDOWS SETUP EXAMPLE:"
	@echo "  1. Configure ansible/inventory.yml with your Windows servers"
	@echo "  2. make setup-windows-system   # Configure system optimizations"
	@echo "  3. make setup-windows-service  # Install service management"
	@echo "  4. make test-windows           # Verify connection"
	@echo ""
	@echo "CLI USAGE:"
	@echo "  pipenv run python gto_cli.py gto"
	@echo "  pipenv run python gto_cli.py list"
	@echo "  pipenv run python gto_cli.py ai --top 3"
	@echo "  pipenv run python gto_cli.py ai --min 1.5"
	@echo ""
	@echo "Directory Structure:"
	@echo "  hands/             - Place hand history files here (.txt format)"
	@echo "  exports/           - Analysis results saved here (.json format)"
	@echo "  debug/             - Debug logs and session summaries"
	@echo "  ansible/           - Ansible playbooks for Windows VM setup"

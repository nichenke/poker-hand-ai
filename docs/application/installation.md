# Installation Guide

Complete installation reference for the GTO Assistant poker analysis system.

## 📋 System Requirements

**For complete system requirements:** See [System Requirements](../REQUIREMENTS.md)

**Quick Summary:**
- **Development Machine**: Mac/Linux with Python 3.11+, Git, VS Code
- **Windows Node**: Windows 10/11 with 16GB+ RAM, GTO+ software
- **Network**: Connectivity between machines on ports 8080, 5985

## 🚀 Getting Started

**New Users:** Start with the [Quick Start Guide](quickstart.md) for a 5-minute setup.

**This guide covers:**
- Development environment setup  
- Security configuration
- Advanced troubleshooting

## 🔧 Development Environment

For contributors or advanced development setup:

**Prerequisites:** Complete the [Quick Start Guide](quickstart.md) first.

### Development Dependencies

```bash
# Install development dependencies
pipenv install --dev

# Install pre-commit hooks (code quality)
pipenv run pre-commit install
```

**VS Code and extensions setup:** Run `./scripts/setup-remote-ssh.sh` to automatically install extensions and configure remote development.

### Development Tools

```bash
# Configure VS Code workspace
mkdir -p .vscode
cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "ansible.validation.lint.enabled": true,
    "ansible.validation.lint.path": "./.venv/bin/ansible-lint"
}
EOF
```

**For remote development setup:** See [SSH Setup Guide](../infrastructure/remote-ssh.md)

## 🔐 Security Setup

### SSH Key Generation

**Automated setup (recommended):**
```bash
# The setup script handles SSH key generation and configuration
./scripts/setup-remote-ssh.sh
```

**Manual SSH key generation (if needed):**
```bash
# Generate SSH key for Ansible/remote development
ssh-keygen -t ed25519 -f ~/.ssh/gto_project_key -C "gto-project"

# Add to SSH agent
ssh-add ~/.ssh/gto_project_key
```

### API Key Management

```bash
# Secure storage of OpenAI API key
# Option 1: Environment variable
export OPENAI_API_KEY="your-key-here"

# Option 2: .env file (gitignored)
echo "OPENAI_API_KEY=your-key-here" >> .env

# Option 3: macOS Keychain
security add-generic-password -a "gto-assistant" -s "openai-api" -w "your-key-here"
```

### Network Security

```bash
# Configure firewall rules (if using local VM)
# See infrastructure documentation for details

# Set up VPN (for cloud deployments)
# Consult your cloud provider's documentation
```

## 🔍 Advanced Verification & Testing

### Installation Verification

```bash
# Check Python environment and all dependencies
make check

# Verify specific imports
pipenv run python -c "import openai, requests, flask; print('✅ All imports successful')"

# List installed packages
pipenv run pip list
```

### Advanced Troubleshooting

**Python Environment Issues:**
```bash
# Clean and rebuild environment
pipenv --rm && pipenv install

# Check Python version compatibility  
python --version  # Should be 3.11+
```

**Network Connectivity Testing:**
```bash
# Test connectivity to Windows node
ping your-windows-ip
nc -zv your-windows-ip 8080  # Test GTO service port
nc -zv your-windows-ip 5985  # Test WinRM port
```

**Windows Service Diagnostics:**
```powershell
# On Windows node - check service status
Get-Service GTOService
Get-EventLog -LogName Application -Source "GTOService" -Newest 10
Get-Content C:\gto-service\gto_service.log -Tail 20
```

**For basic troubleshooting:** See [Quick Start Guide](quickstart.md#troubleshooting)

## 📁 Post-Installation Directory Structure

```text
poker-hand-ai/
├── .env                          # Environment configuration (you create)
├── .venv/                        # Python virtual environment (auto-created)
├── hands/                        # Input: Your hand history files
├── exports/                      # Output: Analysis results
├── docs/                         # Documentation
├── ansible/                      # Infrastructure automation
│   └── inventory.yml            # Your Windows VM configuration (you create)
├── scripts/                      # Setup helper scripts
├── Makefile                      # Build and run commands
├── Pipfile                       # Python dependencies
└── gto_assistant_preloaded.py   # Main application
```

## � Installation Support

**Complex Installation Issues:**
- Review system requirements above
- Check [Development Guide](../development/setup.md) for advanced setup
- Consult [Infrastructure Documentation](../infrastructure/overview.md) for deployment options

**Quick Issues:**
- See [Quick Start Guide](quickstart.md) troubleshooting section
- Verify network connectivity between machines
- Check Windows Event Logs for service issues

**Next Steps After Installation:**
1. **[Quick Start Guide](quickstart.md)** - Get running in 5 minutes
2. **[Cost Optimization](cost-optimization.md)** - Reduce API costs  
3. **[Remote Development](../infrastructure/remote-ssh.md)** - Set up VS Code SSH

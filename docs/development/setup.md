# Development Setup Guide

Development environment setup for contributing to the GTO Assistant project.

## 🛠️ Prerequisites

**System Requirements:** See [System Requirements](../REQUIREMENTS.md)

**Required for Development:**
- Python 3.11+ with pipenv
- VS Code (recommended)
- Git

## 🚀 Initial Setup

**For basic usage:** Follow the [Quick Start Guide](../application/quickstart.md) first.

### Development Environment

```bash
# Install development dependencies
pipenv install --dev

# Install pre-commit hooks for code quality
pipenv run pre-commit install

# Set up environment
echo "OPENAI_API_KEY=your-api-key-here" > .env
echo "GTO_SOLVER_URL=http://your-windows-ip:8080" >> .env
# Edit .env with your actual API keys and settings
```

### VS Code Setup

**Automated setup (recommended):**
```bash
# Run the setup script to install extensions and configure SSH
./scripts/setup-remote-ssh.sh
```

**Manual extension installation (if needed):**
```bash
# Core development extensions
code --install-extension ms-python.python
code --install-extension ms-python.pylint  
code --install-extension ms-python.black-formatter

# Infrastructure extensions (included in setup script above)
code --install-extension redhat.ansible
code --install-extension ms-vscode-remote.remote-ssh
```

### VS Code Workspace Settings

The project includes VS Code workspace settings for:
- Python path configuration  
- Linting and formatting
- Remote SSH development
- Ansible support

## 🔧 Development Commands

**All available commands:** Run `make help` for complete list

**Common development tasks:**
```bash
# Check environment setup
make check

# Run GTO analysis  
make gto

# Start web interface
make visualize

# Test Windows connection
make test-windows
```

**For infrastructure setup:** See [Ansible Documentation](../infrastructure/ansible.md)

## 🛠️ Available Setup Scripts

The project includes automated setup scripts in the `scripts/` directory:

- **`setup-remote-ssh.sh`** - VS Code remote development setup (extensions, SSH config)
- **`setup-windows-vm.ps1`** - Windows VM preparation for Ansible (WinRM, user creation)  
- **`verify-windows-setup.ps1`** - Verify Windows VM configuration
- **`setup-windows-vm-clean.ps1`** - Clean Windows VM setup (currently empty)

**Usage:** Scripts are referenced throughout the documentation guides for automated setup.

## 🐛 Development Debugging

### VS Code Debugging Configuration

The project includes launch configurations for:
- Main application debugging
- Remote Python debugging  
- Ansible playbook debugging

### Common Development Issues

**Environment Problems:**
```bash
# Reset environment if needed
pipenv --rm && pipenv install --dev

# Check Python version  
pipenv run python --version  # Should be 3.11+

# Verify dependencies
pipenv verify
```

**API Integration Testing:**
```bash
# Test API connectivity manually
curl -X POST http://windows-node:8080/health

# Debug WinRM connection
python debug-winrm.py

# Check environment variables
pipenv run python -c "import os; print('API Key set:', 'OPENAI_API_KEY' in os.environ)"
```

**For general troubleshooting:** See guide-specific troubleshooting sections in:
- [Quick Start Guide](../application/quickstart.md#troubleshooting)  
- [Ansible Documentation](../infrastructure/ansible.md#troubleshooting)
- [Remote SSH Guide](../infrastructure/remote-ssh.md#troubleshooting)

## 🤝 Contributing

### Development Standards

- **Code Style**: PEP 8 with black formatting (pre-commit handles this)
- **Documentation**: Update relevant docs with changes
- **Testing**: Add tests for new functionality  
- **Security**: Never commit sensitive data (API keys, credentials)

### Pull Request Workflow

1. Fork repository and create feature branch
2. Make changes with tests and documentation
3. Run `make check` to verify setup
4. Submit pull request with clear description

### Code Quality Tools

**Manual code quality checks:**
```bash
# Format code
pipenv run black *.py

# Sort imports  
pipenv run isort *.py

# Lint code
pipenv run pylint *.py

# Security check
pipenv run bandit -r .
```

**Note:** Pre-commit hooks automatically run formatting and basic checks.

## 📖 Related Documentation

- **[System Requirements](../REQUIREMENTS.md)** - Hardware and software requirements
- **[Quick Start Guide](../application/quickstart.md)** - Basic setup and usage
- **[Infrastructure Guide](../infrastructure/overview.md)** - Deployment architecture  
- **[Ansible Documentation](../infrastructure/ansible.md)** - Infrastructure automation
- **[Remote SSH Setup](../infrastructure/remote-ssh.md)** - VS Code remote development

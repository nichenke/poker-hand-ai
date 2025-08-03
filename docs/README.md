# GTO Assistant Documentation

Comprehensive documentation for the GTO Assistant poker analysis system.

## 📖 Documentation Overview

### Getting Started
- **[Quick Start](application/quickstart.md)** - 5-minute setup with local Windows VM
- **[System Requirements](REQUIREMENTS.md)** - Complete hardware and software requirements
- **[Installation Guide](application/installation.md)** - Complete installation instructions
- **[Cost Optimization](application/cost-optimization.md)** - Optimize ChatGPT API costs

### Application Usage
- **[Usage Guide](application/usage.md)** - How to use the GTO Assistant
- **[Web Visualizer](application/visualizer.md)** - Interactive web interface
- **[CLI Reference](application/cli-reference.md)** - Command-line interface

### Infrastructure Setup
- **[Infrastructure Overview](infrastructure/overview.md)** - Cloud and local deployment options
- **[Windows Setup](infrastructure/windows-setup.md)** - GTO+ installation on Windows
- **[Ansible Automation](infrastructure/ansible.md)** - Automated deployment
- **[Remote SSH Development](infrastructure/remote-ssh.md)** - VS Code remote development

### Development
- **[Development Setup](development/setup.md)** - Local development environment
- **[API Integration](development/api.md)** - GTO+ API integration details
- **[Contributing](development/contributing.md)** - How to contribute to the project

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Mac/Linux     │    │   Windows Node   │    │   OpenAI API    │
│  (Development)  │───▶│   (GTO+ Solver)  │    │   (Analysis)    │
│                 │    │                  │    │                 │
│ • Python Client │    │ • GTO+ Software  │    │ • GPT-4o        │
│ • Web Interface │    │ • Flask API      │    │ • Strategic     │
│ • Hand Files    │    │ • Solver Engine  │    │   Insights      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Navigation

**New Users**: Start with [Quick Start](application/quickstart.md) for the fastest setup.

**Infrastructure**: See [Infrastructure Overview](infrastructure/overview.md) for deployment options.

**Development**: Check [Development Setup](development/setup.md) for contributing.

---

*For the main project README and quick setup, see the [project root](../README.md).*

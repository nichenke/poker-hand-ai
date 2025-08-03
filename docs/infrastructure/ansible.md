# Ansible Automation

Automated deployment and management of GTO+ infrastructure using Ansible.

## 📋 Overview

The Ansible automation provides:

- **Automated Windows Server Setup** - System configuration and optimization
- **GTO+ Service Deployment** - Flask API service installation
- **SSH Server Configuration** - Remote development setup
- **Performance Tuning** - Windows optimization for poker solving

## 🏗️ Architecture

```text
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Control Node  │    │   Target Nodes   │    │   Playbooks      │
│   (Mac/Linux)   │───▶│   (Windows VMs)  │    │   (YAML Config)  │
│                 │    │                  │    │                  │
│ • Ansible Core  │    │ • WinRM          │    │ • System Setup   │
│ • Python Client │    │ • PowerShell     │    │ • Service Deploy │
│ • SSH Keys      │    │ • GTO+ Software  │    │ • SSH Config     │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

## 🚀 Quick Setup

### Prerequisites

- Windows VM with Administrator access
- Network connectivity between control and target nodes
- Ansible installed (`pipenv install` includes it)

**System requirements:** See [System Requirements](../REQUIREMENTS.md)

### 1. Prepare Windows Target

Use the provided setup script on your Windows VM as Administrator:

```powershell
# Run the Windows setup script
.\scripts\setup-windows-vm.ps1
```

This script handles:
- WinRM configuration for Ansible
- Ansible user creation with proper privileges
- Firewall rules for remote access
- Network configuration display

For manual setup or troubleshooting, see the [Windows Setup Guide](windows-setup.md).

### 2. Configure Inventory

```bash
# Copy template
cp ansible/inventory.yml.template ansible/inventory.yml

# Edit with your settings
vim ansible/inventory.yml
```

Example `inventory.yml`:
```yaml
all:
  children:
    gto-solver:
      hosts:
        windows-vm:
          ansible_host: 192.168.1.100
          ansible_user: ansible
          ansible_password: YourPassword123
          ansible_connection: winrm
          ansible_winrm_transport: ntlm
          ansible_winrm_server_cert_validation: ignore
```

### 3. Test Connection

```bash
# Test connectivity
make test-windows

# Or use Ansible directly
ansible gto-solver -m win_ping
```

## 📚 Playbook Reference

### Core Playbooks

#### `ansible-gto-setup.yml` - System Configuration

**Purpose**: Initial Windows server setup and optimization

```bash
make setup-windows-system
```

**What it does**:
- Configures Windows Firewall rules
- Optimizes performance settings (power plan, indexing)
- Disables unnecessary services
- Sets up Windows Defender exclusions
- Configures network adapter settings
- Validates system requirements

#### `ansible-gto-service.yml` - Service Management

**Purpose**: Deploy and manage the Flask API service

```bash
make setup-windows-service
```

**What it does**:
- Installs Python and dependencies
- Deploys Flask service code
- Creates Windows service with NSSM
- Configures service startup and monitoring
- Sets up logging and health checks

#### `ansible-gto-ssh-simple.yml` - SSH Setup (Recommended)

**Purpose**: Configure SSH server for remote development

```bash
make setup-windows-ssh-simple
```

**What it does**:
- Installs OpenSSH via multiple methods (Chocolatey, PowerShell, manual)
- Configures SSH service and firewall
- Sets up SSH keys for passwordless authentication
- Tests connectivity and provides connection details

#### `ansible-gto-ssh.yml` - Advanced SSH Setup

**Purpose**: Comprehensive SSH configuration with security hardening

```bash
make setup-windows-ssh
```

**What it does**:
- Complete SSH server configuration
- Advanced security settings
- User permission management
- Detailed logging and monitoring

### Master Playbook

#### `setup-gto-solver.yml` - Complete Deployment

**Purpose**: End-to-end deployment of GTO+ infrastructure

```bash
make setup-windows
```

**What it does**:
- Combines all playbooks for complete setup
- Installs Python, Git, and dependencies
- Deploys Flask service with Windows service wrapper
- Configures firewall and networking
- Provides comprehensive status reporting

## 🛠️ Advanced Usage

### Custom Playbook Execution

```bash
# Run specific playbook with custom inventory
ansible-playbook -i custom_inventory.yml ansible/ansible-gto-setup.yml

# Run with specific tags
ansible-playbook ansible/ansible-gto-service.yml --tags "service,firewall"

# Dry run (check mode)
ansible-playbook ansible/ansible-gto-setup.yml --check

# Verbose output
ansible-playbook ansible/ansible-gto-service.yml -vvv
```

### Variable Overrides

```bash
# Override default ports
ansible-playbook ansible/setup-gto-solver.yml -e "gto_service_port=8081"

# Override Python version
ansible-playbook ansible/ansible-gto-service.yml -e "python_version=3.11"

# Custom installation paths
ansible-playbook ansible/ansible-gto-service.yml -e "service_path='D:\gto-service'"
```

### Multiple Hosts

```yaml
# inventory.yml for multiple Windows nodes
all:
  children:
    gto-solver:
      hosts:
        prod-solver-1:
          ansible_host: 10.0.1.100
        prod-solver-2:
          ansible_host: 10.0.1.101
        dev-solver:
          ansible_host: 192.168.1.100
      vars:
        ansible_user: ansible
        ansible_connection: winrm
        ansible_winrm_transport: ntlm
```

## 🔧 Configuration Options

### Common Variables

```yaml
# Service configuration
gto_service_port: 8080
gto_api_port: 8082
python_version: "3.11"

# Performance settings
memory_allocation: "16GB"
cpu_cores: "all"
solver_accuracy: "high"

# Security settings
firewall_enabled: true
ssh_enabled: true
rdp_enabled: false

# Paths
service_path: "C:\\gto-service"
scripts_path: "C:\\Scripts"
temp_path: "C:\\temp\\gto"
```

### Environment-Specific Configs

#### Development Environment
```yaml
# group_vars/development.yml
firewall_strict: false
logging_level: debug
auto_update: true
monitoring_enabled: false
```

#### Production Environment
```yaml
# group_vars/production.yml
firewall_strict: true
logging_level: info
auto_update: false
monitoring_enabled: true
backup_enabled: true
```

## 📊 Monitoring & Logging

### Playbook Execution Logs

```bash
# Enable logging
export ANSIBLE_LOG_PATH=./ansible.log

# Run with timestamps
export ANSIBLE_STDOUT_CALLBACK=debug

# Detailed profiling
export ANSIBLE_CALLBACK_PLUGINS=/usr/local/lib/python3.11/site-packages/ansible/plugins/callback
export ANSIBLE_STDOUT_CALLBACK=profile_tasks
```

### Service Health Checks

```bash
# Check all services
ansible gto-solver -m win_service -a "name=GTOService"

# Check system status
ansible gto-solver -m setup

# Custom health check
ansible gto-solver -m win_uri -a "url=http://localhost:8080/health"
```

## 🔒 Security Best Practices

### Credential Management

```bash
# Use Ansible Vault for passwords
ansible-vault create ansible/group_vars/all/vault.yml

# Example vault content:
vault_ansible_password: YourSecurePassword123
vault_gto_api_key: your-gto-api-key

# Reference in inventory:
ansible_password: "{{ vault_ansible_password }}"
```

### SSH Key Management

```bash
# Generate SSH keys for Ansible
ssh-keygen -t ed25519 -f ~/.ssh/ansible_key -C "ansible@gto-project"

# Use in inventory:
ansible_ssh_private_key_file: ~/.ssh/ansible_key
```

### Firewall Configuration

```yaml
# Restrict access to specific IPs
firewall_allowed_ips:
  - "192.168.1.0/24"    # Local network
  - "10.0.0.50/32"      # Specific development machine

# Custom firewall rules
custom_firewall_rules:
  - name: "GTO API - Dev Network"
    port: 8080
    source: "192.168.1.0/24"
    action: allow
```

## 🚨 Troubleshooting

### Connection Issues

```bash
# Test WinRM connectivity
ansible gto-solver -m win_ping -vvv

# Check WinRM configuration
ansible gto-solver -m win_shell -a "winrm get winrm/config"

# Test authentication
ansible gto-solver -m win_whoami
```

### Playbook Debugging

```bash
# Run in check mode (dry run)
ansible-playbook ansible/ansible-gto-setup.yml --check

# Start at specific task
ansible-playbook ansible/ansible-gto-service.yml --start-at-task="Install Python"

# Run only specific tags
ansible-playbook ansible/ansible-gto-setup.yml --tags "firewall,performance"
```

### Common Issues

**WinRM Authentication Failures:**
```powershell
# On Windows target
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
```

**PowerShell Execution Policy:**
```powershell
Set-ExecutionPolicy RemoteSigned -Force
```

**Firewall Blocking:**
```powershell
New-NetFirewallRule -DisplayName "Ansible WinRM" -Direction Inbound -Protocol TCP -LocalPort 5985 -Action Allow
```

## 📁 Directory Structure

```text
ansible/
├── ansible.cfg                      # Ansible configuration
├── inventory.yml                    # Server inventory (create from template)
├── inventory.yml.template           # Inventory template
├── group_vars/                      # Group variables
│   ├── all/                        # Variables for all hosts
│   └── gto-solver/                 # Variables for GTO solver group
├── host_vars/                      # Host-specific variables
├── roles/                          # Custom roles (if any)
├── playbooks/                      # Additional playbooks
└── files/                          # Static files to copy
```

## 🎯 Next Steps

- **[Remote SSH Development](remote-ssh.md)** - Set up VS Code remote development
- **[Windows Setup Guide](windows-setup.md)** - Manual Windows configuration
- **[API Integration](../development/api.md)** - Integrate with applications

## 📞 Getting Help

- Check Ansible documentation for Windows modules
- Review Windows Event Logs for service issues
- Use verbose mode (`-vvv`) for detailed debugging
- Consult the troubleshooting section for common solutions

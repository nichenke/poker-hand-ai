# GTO+ Ansible Automation

This directory contains Ansible playbooks for automated deployment and management of GTO+ poker solver on Windows servers.

## Structure

```
ansible/
├── ansible-gto-setup.yml        # Main system configuration playbook
├── ansible-gto-service.yml      # Service management playbook
├── inventory.yml                # Server inventory configuration
├── inventory.yml.template       # Template for server inventory
├── ansible.cfg                  # Ansible configuration
├── ANSIBLE_SETUP_GUIDE.md      # Detailed setup instructions
└── README.md                    # This file
```

## Playbooks Overview

### 1. `ansible-gto-setup.yml` - System Configuration
**Purpose**: Initial Windows Server setup and optimization for GTO+

**Includes**:
- Windows Firewall configuration
- Performance optimizations (power plan, indexing, virtual memory)
- Process priority settings
- Service disabling for performance
- Windows Defender exclusions
- Network adapter optimization
- System validation

**Tags**: `firewall`, `security`, `performance`, `power`, `indexing`, `memory`, `process_priority`, `services`, `antivirus`, `network`, `validation`, `info`

### 2. `ansible-gto-service.yml` - Service Management
**Purpose**: GTO+ service installation, monitoring, and management

**Includes**:
- Service management scripts (start/stop/restart/status)
- Health monitoring and auto-restart
- Comprehensive monitoring reports
- Scheduled task creation
- Windows Event Logging
- Service validation
- Log cleanup automation
- Optional Windows Service installation via NSSM

**Tags**: `setup`, `directories`, `scripts`, `service`, `monitoring`, `scheduled_tasks`, `logging`, `maintenance`, `validation`, `installation`, `status`, `start`

## Quick Start

### 1. Prerequisites
```bash
# Install Ansible and dependencies
pip install ansible pywinrm

# Configure WinRM on Windows servers (run as Administrator)
powershell -File setup_winrm.ps1
```

### 2. Configure Inventory
Edit `inventory.ini` with your server details:
```ini
### 2. Configure Inventory
Edit `inventory.yml` with your server details:
```yaml
all:
  hosts:
    gto-solver:
      ansible_host: YOUR_SERVER_IP
```
```

### 3. Test Connection
```bash
cd ansible/
ansible windows_servers -m win_ping
```

### 4. Run Playbooks
```bash
# Full system setup (run first)
ansible-playbook ansible-gto-setup.yml

# Service management setup (run after system setup)
ansible-playbook ansible-gto-service.yml

# Both playbooks together
ansible-playbook ansible-gto-setup.yml ansible-gto-service.yml
```

## Usage Examples

### System Configuration Only
```bash
# Configure firewall and performance optimizations
ansible-playbook ansible-gto-setup.yml --tags "firewall,performance"

# Just performance optimizations
ansible-playbook ansible-gto-setup.yml --tags "performance"

# Validation only (check current configuration)
ansible-playbook ansible-gto-setup.yml --tags "validation"
```

### Service Management
```bash
# Setup service scripts and monitoring
ansible-playbook ansible-gto-service.yml

# Just monitoring setup
ansible-playbook ansible-gto-service.yml --tags "monitoring"

# Service validation
ansible-playbook ansible-gto-service.yml --tags "validation"

# Start GTO+ service on all servers
ansible-playbook ansible-gto-service.yml --extra-vars "start_gto_service=true"
```

### Combined Operations
```bash
# Complete setup and start services
ansible-playbook ansible-gto-setup.yml ansible-gto-service.yml --extra-vars "start_gto_service=true"

# Setup with specific memory allocation
ansible-playbook ansible-gto-service.yml --extra-vars "gto_memory_allocation=16GB"

# Custom API port
ansible-playbook ansible-gto-service.yml --extra-vars "gto_api_port=8083"
```

## Configuration Variables

### Common Variables (both playbooks)
- `gto_install_path`: GTO+ installation directory (default: `C:\Program Files\GTO`)
- `gto_executable`: GTO+ executable name (default: `GTO+.exe`)
- `gto_api_port`: API port number (default: `8082`)
- `scripts_directory`: Service scripts location (default: `C:\Scripts`)

### Service-Specific Variables
- `gto_memory_allocation`: Memory allocation for GTO+ (default: `12GB`)
- `gto_log_level`: Logging level (default: `info`)
- `service_name`: Windows service name (default: `GTO+ API Service`)
- `start_gto_service`: Whether to start service after setup (default: `false`)

## Monitoring and Maintenance

### Health Monitoring
The service playbook sets up automatic monitoring:
- **Health checks**: Every 5 minutes with auto-restart on failure
- **System monitoring**: Comprehensive reports every 15 minutes
- **Log cleanup**: Weekly cleanup of logs older than 30 days

### Manual Service Management
After running the playbooks, use these scripts on the Windows servers:
```batch
# Located in C:\Scripts\
start_gto_api.bat      # Start GTO+ API
stop_gto_api.bat       # Stop GTO+ API
restart_gto_api.bat    # Restart GTO+ API
check_gto_health.bat   # Check API health
check_gto_status.bat   # Check process status
monitor_gto.bat        # Comprehensive monitoring report
```

### Windows Service Installation (Optional)
For production environments, install GTO+ as a Windows service:
```batch
# Install NSSM first: https://nssm.cc/download
# Then run:
C:\Scripts\install_gto_service.bat

# Manage service
net start "GTO+ API Service"
net stop "GTO+ API Service"
```

## Security Considerations

### Use Ansible Vault for Passwords
```bash
# Create encrypted password file
ansible-vault create group_vars/windows_servers/vault.yml

# Content:
vault_windows_password: YourActualPassword

# Update inventory.ini:
ansible_password: "{{ vault_windows_password }}"

# Run with vault
ansible-playbook ansible-gto-setup.yml --ask-vault-pass
```

### Firewall Configuration
The playbooks configure Windows Firewall to allow:
- GTO+ application through firewall
- API ports (8080-8090 range)
- Specific API port (8082 by default)

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   ```bash
   # Increase timeouts in ansible.cfg
   [winrm]
   read_timeout = 120
   operation_timeout = 90
   ```

2. **Access Denied**
   ```bash
   # Test authentication
   ansible windows_servers -m win_shell -a "whoami"
   ```

3. **Service Won't Start**
   ```bash
   # Check validation
   ansible-playbook ansible-gto-service.yml --tags "validation"
   ```

### Debug Commands
```bash
# Verbose output
ansible-playbook ansible-gto-setup.yml -vvv

# Check specific server
ansible-playbook ansible-gto-setup.yml --limit "gto-server-01"

# Dry run
ansible-playbook ansible-gto-setup.yml --check
```

## Support

For detailed setup instructions, see `ANSIBLE_SETUP_GUIDE.md`.

For GTO+ specific issues, consult the main setup guide: `../GTO_PLUS_WINDOWS_SETUP.md`.

# GTO+ Ansible Playbook Setup Guide

This guide covers the automated deployment of GTO+ on Windows Server using Ansible.

## Playbook Structure

- **ansible-gto-setup.yml**: System configuration and optimization
- **ansible-gto-service.yml**: Service management and monitoring
- **ansible-gto-master.yml**: Runs both playbooks in sequence

## Prerequisites

### 1. Install Ansible and Dependencies
```bash
# On your control machine (Linux/macOS)
pip install ansible pywinrm

# Verify installation
ansible --version
```

### 2. Configure WinRM on Windows Server
Run this PowerShell script as Administrator on each Windows server:

```powershell
# Enable WinRM
Enable-PSRemoting -Force

# Configure WinRM for Ansible
winrm quickconfig -q
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/client/auth '@{Basic="true"}'

# Enable HTTPS (recommended for production)
$cert = New-SelfSignedCertificate -DnsName "your-server-name" -CertStoreLocation Cert:\LocalMachine\My
winrm create winrm/config/listener?Address=*+Transport=HTTPS '@{Hostname="your-server-name";CertificateThumbprint="' + $cert.Thumbprint + '"}'

# Configure firewall
New-NetFirewallRule -DisplayName "WinRM-HTTPS" -Direction Inbound -LocalPort 5986 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "WinRM-HTTP" -Direction Inbound -LocalPort 5985 -Protocol TCP -Action Allow

# Restart WinRM service
Restart-Service WinRM
```

## Usage

### 1. Update Inventory
Edit `inventory.yml` with your server details:
```yaml
all:
  hosts:
    gto-solver:
      ansible_host: YOUR_SERVER_IP
```

### 2. Test Connection
```bash
# Test Ansible connectivity
ansible gto-solver -m win_ping

# Should return:
# gto-solver | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }
```

### 3. Run Playbooks
```bash
# Run complete setup (recommended)
ansible-playbook ansible-gto-master.yml

# Run individual playbooks
ansible-playbook ansible-gto-setup.yml    # System configuration only
ansible-playbook ansible-gto-service.yml  # Service management only

# Run in check mode (dry run)
ansible-playbook ansible-gto-master.yml --check

# Run with verbose output
ansible-playbook ansible-gto-master.yml -vvv
```

### 4. Available Tags
- `setup` - Directory creation
- `firewall` - Firewall configuration
- `security` - Security settings
- `performance` - Performance optimizations
- `scripts` - Service management scripts
- `monitoring` - Health monitoring setup
- `validation` - System information gathering

## Security Considerations

### 1. Use Ansible Vault for Passwords
```bash
# Create encrypted password file
ansible-vault create group_vars/windows_servers/vault.yml

# Add content:
vault_windows_password: YourActualPassword

# Update inventory.yml:
ansible_password: "{{ vault_windows_password }}"

# Run with vault password
ansible-playbook ansible-gto-setup.yml --ask-vault-pass
```

### 2. Certificate-based Authentication (Advanced)
```powershell
# On Windows server - create certificate for authentication
$cert = New-SelfSignedCertificate -Type Custom -Subject "CN=AnsibleUser" -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.2","2.5.29.17={text}upn=ansible@yourdomain.com","2.5.29.19={text}false") -KeyUsage DigitalSignature,KeyEncipherment -KeyAlgorithm RSA -KeyLength 2048 -CertStoreLocation "Cert:\LocalMachine\My"

# Export certificate
Export-Certificate -Cert $cert -FilePath "C:\ansible_cert.cer"
```

## Customization

### 1. Override Variables
Create `group_vars/windows_servers/main.yml`:
```yaml
gto_install_path: "D:\\GTO"  # Custom install path
gto_api_port: 8083           # Custom API port
gto_memory_allocation: "16GB" # More memory
```

### 2. Environment-specific Settings
Create `host_vars/gto-server-01/main.yml`:
```yaml
gto_memory_allocation: "32GB"  # High-memory server
gto_api_port: 8084             # Different port
```

## Troubleshooting

### Common Issues

**"Access is denied" errors:**
```bash
# Check WinRM authentication
ansible windows_servers -m win_shell -a "whoami"
```

**Timeout errors:**
```bash
# Increase timeout in ansible.cfg
[winrm]
read_timeout = 120
operation_timeout = 90
```

**Certificate errors:**
```bash
# Disable certificate validation for testing
ansible_winrm_server_cert_validation: ignore
```

### Debug Commands
```bash
# Test specific task
ansible-playbook ansible-gto-setup.yml --tags "firewall" --limit "gto-server-01" -vvv

# Check facts
ansible gto-solver -m setup

# Test WinRM manually
python -c "import winrm; print(winrm.Session('http://server:5985/wsman', auth=('user', 'pass')).run_cmd('ipconfig'))"
```

## Monitoring

After running the playbook, monitor the setup:

```bash
# Check service status
ansible gto-solver -m win_shell -a "Get-Process GTO+ -ErrorAction SilentlyContinue"

# Check firewall rules
ansible gto-solver -m win_shell -a "Get-NetFirewallRule -DisplayName '*GTO*'"

# Test API endpoint
ansible gto-solver -m win_shell -a "curl -s http://localhost:8082/health"
```

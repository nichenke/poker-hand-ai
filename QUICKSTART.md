****# Quick Start Guide - Local Windows VM Setup

This is the fastest way to get your GTO Assistant running with a local Windows 11 VM.

## 🚀 Quick Setup (5 minutes)

### Step 0: Clone Repository
On your Mac:

```bash
git clone https://github.com/nichenke/poker-hand-ai.git
cd poker-hand-ai
```

### Step 1: Prepare Windows VM
Run this **once** on your Windows 11 VM as Administrator:

```powershell
# Copy and paste this entire script into PowerShell (run as Administrator)

# Windows VM Initial Setup Script
Write-Host "Setting up Windows VM for Ansible management..." -ForegroundColor Green

# Set execution policy
Set-ExecutionPolicy RemoteSigned -Force
Write-Host "Execution policy set" -ForegroundColor Green

# Enable WinRM
Enable-PSRemoting -Force
winrm quickconfig -force
Write-Host "WinRM enabled" -ForegroundColor Green

# Configure WinRM for Ansible
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="1024"}'
Write-Host "WinRM configured for Ansible" -ForegroundColor Green

# Create Ansible user - simplified approach
$Username = "ansible"
Write-Host "Creating user: $Username"
$Password = Read-Host "Enter password for ansible user" -AsSecureString

# Convert to plain text for net command
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password)
$PlainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Use net user command (more reliable)
net user $Username $PlainPassword /add /comment:"Ansible automation user" /expires:never
net localgroup Administrators $Username /add

Write-Host "Ansible user created and added to Administrators" -ForegroundColor Green

# Configure Windows Firewall for WinRM
New-NetFirewallRule -DisplayName "WinRM HTTP" -Direction Inbound -Protocol TCP -LocalPort 5985 -Action Allow
Write-Host "Firewall configured for WinRM" -ForegroundColor Green

# Get and display IP address
$IP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}).IPAddress
Write-Host "VM IP Address: $IP" -ForegroundColor Cyan

Write-Host ""
Write-Host "Setup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Update ansible/inventory.yml with IP: $IP" -ForegroundColor White
Write-Host "2. Update ansible/inventory.yml with the password you just set" -ForegroundColor White
Write-Host "3. From your Mac, run: make test-windows" -ForegroundColor White
Write-Host "4. If test passes, run: make setup-windows" -ForegroundColor White
```

### Step 2: Configure Ansible
On your Mac:

```bash
# Install dependencies (including Ansible)
make install

# Copy and edit inventory
cp ansible/inventory.yml.template ansible/inventory.yml
# Edit ansible/inventory.yml with your VM IP and password

# Test connection
make test-windows
```

### Step 3: Deploy GTO Service
```bash
# Automated setup (installs Python, Flask service, Windows service)
make setup-windows
```

### Step 4: Configure and Run
```bash
# Add to your .env file
echo "GTO_SOLVER_URL=http://YOUR_VM_IP:8080" >> .env

# Test the setup
curl http://YOUR_VM_IP:8080/health

# Run analysis
make run
```

## ✅ What Gets Installed

The Ansible playbook automatically installs:
- **Python 3.11** via Chocolatey
- **Git** for version control
- **Flask** web service
- **Windows Service** (auto-starts on boot)
- **Firewall rules** for port 8080
- **Mock GTO+ solver** (ready for real GTO+ integration)

## 🔧 Service Management

On Windows VM:
```powershell
# Check service status
Get-Service GTOService

# View logs
Get-Content C:\gto-service\gto_service.log -Tail 20

# Restart service
Restart-Service GTOService
```

## 📁 File Locations

**On Windows VM:**
- Service: `C:\gto-service\`
- Logs: `C:\gto-service\gto_service.log`
- Temp files: `C:\temp\gto\`

**On Mac:**
- Hand files: `hands/*.txt`
- Results: `exports/*.json`
- Config: `ansible/inventory.yml`

## 🎯 Integration with Real GTO+

When you get GTO+ software:

1. Install GTO+ on Windows VM
2. Edit `C:\gto-service\gto_service.py`
3. Replace mock analysis with actual GTO+ calls
4. Restart the service

## 🆘 Troubleshooting

**Connection Failed:**
```bash
# Check VM IP
ping YOUR_VM_IP

# Test WinRM
ansible gto-solver -m win_ping
```

**Service Not Starting:**
```powershell
# Check Windows Event Logs
Get-EventLog -LogName Application -Source "Service Control Manager" -Newest 10
```

This setup gives you a fully automated GTO analysis pipeline using your existing Windows VM with minimal manual intervention!

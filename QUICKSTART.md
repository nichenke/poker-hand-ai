# Quick Start Guide - Local Windows VM Setup

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
# Download and run the setup script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/nichenke/poker-hand-ai/main/scripts/setup-windows-vm.ps1" -OutFile "setup.ps1"
PowerShell.exe -ExecutionPolicy Bypass -File setup.ps1
```

Or manually copy the script from `scripts/setup-windows-vm.ps1`

### Step 2: Configure Ansible
On your Mac:

```bash
# Install Ansible
brew install ansible

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

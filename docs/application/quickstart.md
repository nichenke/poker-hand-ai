# Quick Start Guide

The fastest way to get your GTO Assistant running with a local Windows VM setup.

## 🚀 5-Minute Setup

### Prerequisites

- Mac/Linux development machine
- Windows VM with Administrator access  
- Internet connection

**Detailed system requirements:** See [System Requirements](../REQUIREMENTS.md)

### Step 1: Clone Repository

On your Mac/Linux machine:

```bash
git clone https://github.com/nichenke/poker-hand-ai.git
cd poker-hand-ai
```

### Step 2: Prepare Windows VM

Run the provided setup script **once** on your Windows VM as Administrator:

```powershell
# Download and run the Windows setup script
# Option 1: If you have the repo cloned on Windows
.\scripts\setup-windows-vm.ps1

# Option 2: Run directly from PowerShell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/nichenke/poker-hand-ai/main/scripts/setup-windows-vm.ps1" -OutFile "setup-windows-vm.ps1"
.\setup-windows-vm.ps1
```

The script will:
- Enable PowerShell remoting and WinRM
- Create an `ansible` user with Administrator privileges  
- Configure firewall rules for remote access
- Display your VM's IP address for the next step

**Note:** Keep the password you set for the `ansible` user - you'll need it in Step 3.

### Step 3: Configure Connection

On your Mac/Linux machine:

```bash
# Install dependencies
make install

# Copy inventory template
cp ansible/inventory.yml.template ansible/inventory.yml

# Edit ansible/inventory.yml with your VM IP and password
# Test connection
make test-windows
```

### Step 4: Deploy Services

```bash
# Automated deployment
make setup-windows

# Configure environment
echo "GTO_SOLVER_URL=http://YOUR_VM_IP:8080" >> .env
echo "OPENAI_API_KEY=your-key-here" >> .env
```

### Step 5: Run Analysis

```bash
# Add hand files to hands/ directory
cp your_hands/*.txt hands/

# Run analysis
make run

# Or use web interface
make visualize
```

## ✅ What Gets Deployed

The automation installs:

- **Python & Dependencies** - Runtime environment
- **Flask API Service** - HTTP interface for GTO+ integration
- **Windows Service** - Auto-starts on boot
- **Firewall Rules** - Secure network access
- **Mock Solver** - Ready for real GTO+ integration

## 🔧 Service Management

### On Windows VM

```powershell
# Check service status
Get-Service GTOService

# View logs
Get-Content C:\gto-service\gto_service.log -Tail 20

# Restart service
Restart-Service GTOService
```

### On Development Machine

```bash
# Test remote service
make test-service

# Check system status
make test-windows
```

## 📁 Key Locations

### Windows VM
- **Service Files**: `C:\gto-service\`
- **Logs**: `C:\gto-service\gto_service.log`
- **Temporary Files**: `C:\temp\gto\`

### Development Machine
- **Hand Files**: `hands/*.txt`
- **Analysis Results**: `exports/*.json`
- **Configuration**: `ansible/inventory.yml`

## 🎯 Next Steps

1. **Add Real GTO+ Integration** - See [Windows Setup Guide](../infrastructure/windows-setup.md)
2. **Optimize Costs** - See [Cost Optimization Guide](cost-optimization.md)
3. **Remote Development** - See [SSH Setup Guide](../infrastructure/remote-ssh.md)

## 🆘 Troubleshooting

### Quick Verification

Run the verification script on your Windows VM to check the setup:

```powershell
# Verify Windows VM configuration
.\scripts\verify-windows-setup.ps1
```

### Connection Issues

**Test network connectivity:**
```bash
# Test network connectivity
ping YOUR_VM_IP

# Test WinRM connection
ansible gto-solver -m win_ping
```

**Service Issues:**
```powershell
# Check Windows Event Logs
Get-EventLog -LogName Application -Source "Service Control Manager" -Newest 10

# Manual service start
Start-Service GTOService
```

### Remote Development Setup

For VS Code remote development, use the SSH setup script:

```bash
# Set up VS Code Remote SSH
./scripts/setup-remote-ssh.sh
```

See the [SSH Setup Guide](../infrastructure/remote-ssh.md) for detailed remote development instructions.

**Common Solutions:**
- Verify Windows VM IP address
- Check firewall settings on both machines  
- Confirm ansible user credentials
- Ensure WinRM is properly configured

For more detailed troubleshooting, see the [Infrastructure Documentation](../infrastructure/overview.md).

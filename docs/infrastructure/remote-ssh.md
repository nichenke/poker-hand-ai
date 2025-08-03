# VS Code Remote SSH Setup for GTO+ Development

This guide helps you set up VS Code to edit files directly on your Windows VM from your Mac, providing a seamless remote development experience.

## 🚀 Quick Setup (Recommended)

### Option 1: Automated Setup

**Local Setup (Mac):**
```bash
# Install VS Code extensions and configure SSH
make setup-ssh
```

**Alternative manual setup:**
```bash
# Use the setup script directly
./scripts/setup-remote-ssh.sh
```

### Option 2: Ansible Remote Setup

**Remote Setup (Windows VM):**
```bash
# Configure SSH server on Windows VM via Ansible (reliable method)
make setup-windows-ssh-simple
```

### 3. Connect with VS Code
- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
- Type "Remote-SSH: Connect to Host"
- Select "gto-windows"
- Open folder: `C:\gto-service`

## ✅ Verified Working Setup

The `ansible-gto-ssh-simple.yml` playbook has been tested and works reliably with:

- **Windows 11 Pro** (Build 26100)
- **Chocolatey OpenSSH installation**
- **Automatic SSH service configuration**
- **Key-based authentication**
- **VS Code Remote SSH extension**

### What the Playbook Does

1. **Installs OpenSSH** via Chocolatey (most reliable method)
2. **Configures SSH service** with proper installation script
3. **Creates SSH configuration** with secure settings
4. **Generates host keys** automatically
5. **Sets up firewall rules** for SSH access
6. **Copies your public key** for passwordless authentication
7. **Tests connectivity** to verify everything works

## � Remote Development Files

Once connected via VS Code Remote SSH, you can edit:

- **`C:\gto-service\gto_service.py`** - Main Flask service (your current focus)
- **`C:\gto-service\requirements.txt`** - Python dependencies
- **`C:\gto-service\gto_service.log`** - Service logs
- **`C:\ProgramData\ssh\sshd_config`** - SSH server configuration

## 🎯 Development Workflow

1. **Connect** to Windows VM via Remote SSH
2. **Open** `C:\gto-service\gto_service.py`
3. **Edit** Flask endpoints with full IntelliSense
4. **Test** via integrated terminal: `python gto_service.py`
5. **Monitor** logs in real-time
6. **Restart service** when needed: `Restart-Service GTOService`

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test SSH connection manually
ssh gto-windows

# Re-run setup if needed
make setup-windows-ssh-simple
```

### Service Issues
```powershell
# Check SSH service (Windows VM)
Get-Service sshd

# Restart SSH service (Windows VM)
Restart-Service sshd
```

## 💡 VS Code Features

- **Integrated Terminal** - PowerShell on Windows VM
- **Port Forwarding** - Access Flask service at `localhost:8080` from Mac
- **File Explorer** - Browse entire Windows filesystem
- **Extensions** - Python, debugging, Git integration work remotely
- **IntelliSense** - Full code completion for Python development

This setup provides the best of both worlds: local VS Code experience with remote Windows development! 🚀

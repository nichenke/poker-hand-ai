#!/bin/bash

# VS Code Remote SSH Setup Script for GTO+ Development
# This script configures your local machine for remote development on Windows VM

set -e

echo "🚀 Setting up VS Code Remote SSH for GTO+ Development..."

# Check if VS Code is installed
if ! command -v code &> /dev/null; then
    echo "❌ VS Code is not installed or not in PATH"
    echo "   Please install VS Code first: https://code.visualstudio.com/"
    exit 1
fi

echo "✅ VS Code found"

# Install Remote SSH extension
echo "📦 Installing VS Code Remote SSH extension..."
code --install-extension ms-vscode-remote.remote-ssh
code --install-extension ms-vscode-remote.remote-ssh-edit
code --install-extension ms-python.python
code --install-extension redhat.ansible

echo "✅ Extensions installed"

# Generate SSH key if it doesn't exist
SSH_KEY="$HOME/.ssh/id_ed25519"
if [ ! -f "$SSH_KEY" ]; then
    echo "🔑 Generating SSH key..."
    ssh-keygen -t ed25519 -f "$SSH_KEY" -N "" -C "$(whoami)@$(hostname)"
    echo "✅ SSH key generated: $SSH_KEY"
else
    echo "✅ SSH key already exists: $SSH_KEY"
fi

# Create SSH config directory if it doesn't exist
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

# Read configuration from .env file if it exists
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    echo "📄 Reading configuration from $ENV_FILE..."
    # shellcheck source=.env
    source "$ENV_FILE"
fi

# Get Windows VM details
echo ""
echo "🖥️  Please provide your Windows VM details:"
read -p "Windows VM IP address [${WINDOWS_VM_IP:-}]: " vm_ip
vm_ip=${vm_ip:-$WINDOWS_VM_IP}

read -p "Windows VM username [${WINDOWS_VM_USER:-Administrator}]: " vm_user
vm_user=${vm_user:-${WINDOWS_VM_USER:-Administrator}}

read -p "SSH port [22]: " ssh_port
ssh_port=${ssh_port:-22}

# Create/update SSH config
SSH_CONFIG="$HOME/.ssh/config"
echo "📝 Updating SSH config at $SSH_CONFIG..."

# Remove existing gto-windows entry if it exists
if [ -f "$SSH_CONFIG" ]; then
    sed -i.bak '/Host gto-windows/,/^$/d' "$SSH_CONFIG" 2>/dev/null || true
fi

# Add new configuration
cat >> "$SSH_CONFIG" << EOF

# GTO+ Windows VM for Remote Development
Host gto-windows
    HostName $vm_ip
    User $vm_user
    Port $ssh_port
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ForwardAgent yes
EOF

chmod 600 "$SSH_CONFIG"
echo "✅ SSH config updated"

# Display public key for manual setup
echo ""
echo "🔑 Your public key (copy this to Windows VM if needed):"
echo "----------------------------------------"
cat "$SSH_KEY.pub"
echo "----------------------------------------"

echo ""
echo "✅ Local setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Run Ansible to configure SSH on Windows VM:"
echo "   cd ansible && ansible-playbook ansible-gto-ssh-simple.yml"
echo "   (or try: make setup-windows-ssh-simple)"
echo ""
echo "   If that fails, try the advanced method:"
echo "   make setup-windows-ssh"
echo ""
echo "2. Test SSH connection:"
echo "   ssh gto-windows"
echo ""
echo "3. Open VS Code and connect remotely:"
echo "   - Press Ctrl+Shift+P (Cmd+Shift+P on Mac)"
echo "   - Type 'Remote-SSH: Connect to Host'"
echo "   - Select 'gto-windows'"
echo ""
echo "4. Once connected, open the GTO service file:"
echo "   C:\\gto-service\\gto_service.py"
echo ""
echo "🎯 Happy remote coding!"

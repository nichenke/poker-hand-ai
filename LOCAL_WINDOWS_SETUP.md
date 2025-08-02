# Local Windows VM GTO+ Solver Setup

This document provides automated setup instructions for configuring a local Windows 11 Home VM as a GTO+ solver node using Ansible for remote configuration.

## 🏠 Home Lab Architecture

```
Mac (Development) → Windows 11 VM (GTO+ Solver) → Analysis Pipeline
```

## 📋 Prerequisites

### Local Requirements
- Windows 11 Home VM running in your home lab
- VM accessible via network (static IP recommended)
- Ansible installed on your Mac: `brew install ansible`
- WinRM access to Windows VM (we'll set this up)

### VM Specifications
**Recommended minimum:**
- **CPU:** 4 cores (8 preferred)
- **RAM:** 8GB (16GB preferred) 
- **Storage:** 50GB available
- **Network:** Static IP on local network

## 🔧 Initial Windows VM Setup

### Step 1: Enable WinRM and PowerShell Remoting

Run these commands **on the Windows VM** (one-time manual setup):

```powershell
# Run as Administrator in PowerShell
Set-ExecutionPolicy RemoteSigned -Force

# Enable WinRM
Enable-PSRemoting -Force
winrm quickconfig -force

# Configure WinRM for Ansible
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="1024"}'

# Create Ansible user (replace 'your-password' with a strong password)
$Password = ConvertTo-SecureString "your-strong-password" -AsPlainText -Force
New-LocalUser -Name "ansible" -Password $Password -Description "Ansible automation user"
Add-LocalGroupMember -Group "Administrators" -Member "ansible"

# Get VM IP address (note this down)
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}
```

### Step 2: Test Connection from Mac

```bash
# Install Ansible Windows collection
ansible-galaxy collection install ansible.windows

# Test connection (replace IP with your VM's IP)
ansible windows -i "192.168.1.100," -m win_ping \
  -e ansible_user=ansible \
  -e ansible_password=your-strong-password \
  -e ansible_connection=winrm \
  -e ansible_winrm_transport=basic \
  -e ansible_winrm_server_cert_validation=ignore
```

## 📦 Automated Setup with Ansible

### Create Ansible Configuration Files

The following files will automate the entire GTO+ solver setup on your Windows VM.

### Inventory Configuration

Create `ansible/inventory.yml`:

```yaml
all:
  hosts:
    gto-solver:
      ansible_host: 192.168.1.100  # Replace with your VM IP
      ansible_user: ansible
      ansible_password: your-strong-password
      ansible_connection: winrm
      ansible_winrm_transport: basic
      ansible_winrm_server_cert_validation: ignore
      ansible_port: 5985

  vars:
    gto_service_port: 8080
    python_version: "3.11.0"
```

### Main Playbook

Create `ansible/setup-gto-solver.yml`:

```yaml
---
- name: Setup GTO+ Solver on Windows VM
  hosts: gto-solver
  gather_facts: yes
  tasks:
    - name: Install Chocolatey
      win_chocolatey:
        name: chocolatey
        state: present

    - name: Install Python via Chocolatey
      win_chocolatey:
        name: python
        version: "{{ python_version }}"
        state: present

    - name: Install Git via Chocolatey
      win_chocolatey:
        name: git
        state: present

    - name: Create GTO service directory
      win_file:
        path: C:\gto-service
        state: directory

    - name: Download GTO service script
      win_copy:
        content: |
          from flask import Flask, request, jsonify
          import subprocess
          import json
          import os
          import time
          import logging
          from datetime import datetime

          # Configure logging
          logging.basicConfig(
              level=logging.INFO,
              format='%(asctime)s - %(levelname)s - %(message)s',
              handlers=[
                  logging.FileHandler('gto_service.log'),
                  logging.StreamHandler()
              ]
          )

          app = Flask(__name__)

          @app.route('/health')
          def health_check():
              return jsonify({
                  "status": "healthy", 
                  "timestamp": time.time(),
                  "server": "Windows VM GTO+ Service"
              })

          @app.route('/api/analyze', methods=['POST'])
          def analyze_hand():
              try:
                  data = request.json
                  hand_id = data.get('hand_id', 'unknown')
                  hand_history = data.get('hand_history', '')
                  
                  logging.info(f"Received analysis request for hand {hand_id}")
                  
                  # Save hand to temp file
                  temp_dir = "C:\\temp\\gto"
                  os.makedirs(temp_dir, exist_ok=True)
                  temp_file = os.path.join(temp_dir, f"hand_{hand_id}.txt")
                  
                  with open(temp_file, 'w') as f:
                      f.write(hand_history)
                  
                  # Mock GTO+ analysis (replace with actual GTO+ command)
                  start_time = time.time()
                  
                  # Simulate processing time
                  time.sleep(2)
                  
                  # Mock solver output (replace with actual GTO+ results)
                  mock_output = {
                      "solver_output": f"Mock GTO+ analysis for hand {hand_id}",
                      "ranges": {
                          "CO": "77+, AJs+, AQo+, KQs",
                          "BB": "99+, AKo, AQs+, some KQs"
                      },
                      "frequencies": {
                          "KK_5bet": 1.0,
                          "QQ_5bet": 0.52,
                          "QQ_call": 0.48
                      },
                      "ev_analysis": {
                          "KK_flat_loss": -0.18,
                          "QQ_fold_loss": -0.22
                      }
                  }
                  
                  processing_time = time.time() - start_time
                  
                  # Cleanup
                  try:
                      os.remove(temp_file)
                  except:
                      pass
                  
                  logging.info(f"Completed analysis for hand {hand_id} in {processing_time:.2f}s")
                  
                  return jsonify({
                      **mock_output,
                      "processing_time": processing_time,
                      "status": "success",
                      "hand_id": hand_id
                  })
                  
              except Exception as e:
                  logging.error(f"Error processing hand: {str(e)}")
                  return jsonify({"error": str(e), "status": "error"}), 500

          if __name__ == '__main__':
              logging.info("Starting GTO+ Service on port {{ gto_service_port }}")
              app.run(host='0.0.0.0', port={{ gto_service_port }}, debug=False)
        dest: C:\gto-service\gto_service.py

    - name: Create requirements.txt
      win_copy:
        content: |
          flask==2.3.3
          requests==2.31.0
        dest: C:\gto-service\requirements.txt

    - name: Install Python packages
      win_command: pip install -r C:\gto-service\requirements.txt

    - name: Create Windows service script
      win_copy:
        content: |
          # Install and start GTO service
          $serviceName = "GTOService"
          $servicePath = "C:\gto-service\gto_service.py"
          $pythonPath = (Get-Command python).Source

          # Stop and remove existing service if it exists
          if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
              Stop-Service $serviceName -Force
              sc.exe delete $serviceName
          }

          # Create new service using NSSM (Non-Sucking Service Manager)
          # Download NSSM first
          $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
          $nssmZip = "C:\temp\nssm.zip"
          $nssmDir = "C:\nssm"

          New-Item -ItemType Directory -Force -Path C:\temp
          Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip
          Expand-Archive -Path $nssmZip -DestinationPath C:\temp -Force
          Move-Item -Path "C:\temp\nssm-2.24" -Destination $nssmDir -Force

          # Install service
          & "$nssmDir\win64\nssm.exe" install $serviceName $pythonPath $servicePath
          & "$nssmDir\win64\nssm.exe" set $serviceName Start SERVICE_AUTO_START
          & "$nssmDir\win64\nssm.exe" set $serviceName AppDirectory "C:\gto-service"

          # Start service
          Start-Service $serviceName

          Write-Host "GTO Service installed and started successfully"
        dest: C:\gto-service\install_service.ps1

    - name: Configure Windows Firewall
      win_firewall_rule:
        name: "GTO Service"
        localport: "{{ gto_service_port }}"
        action: allow
        direction: in
        protocol: tcp
        state: present

    - name: Run service installation script
      win_shell: PowerShell.exe -ExecutionPolicy Bypass -File C:\gto-service\install_service.ps1

    - name: Verify service is running
      win_service:
        name: GTOService
        state: started
      register: service_result

    - name: Display setup completion message
      debug:
        msg: |
          GTO+ Solver setup completed successfully!
          
          Service Status: {{ service_result.state }}
          Access URL: http://{{ ansible_host }}:{{ gto_service_port }}
          Health Check: http://{{ ansible_host }}:{{ gto_service_port }}/health
          
          Next steps:
          1. Update your .env file with: GTO_SOLVER_URL=http://{{ ansible_host }}:{{ gto_service_port }}
          2. Test connection from Mac: curl http://{{ ansible_host }}:{{ gto_service_port }}/health
          3. Run your GTO Assistant: make run
```

### Configuration File

Create `ansible/ansible.cfg`:

```ini
[defaults]
inventory = inventory.yml
host_key_checking = False
timeout = 30
retry_files_enabled = False

[ssh_connection]
pipelining = True
```

## 🚀 Running the Automation

### Execute the Setup

```bash
# Navigate to your project directory
cd /Users/nic/src/poker-gto+-m1

# Install Ansible Windows collection
ansible-galaxy collection install ansible.windows

# Update inventory.yml with your VM's IP and credentials
# Then run the playbook
ansible-playbook ansible/setup-gto-solver.yml
```

### Verify Installation

```bash
# Test the health endpoint
curl http://192.168.1.100:8080/health

# Should return:
# {"status":"healthy","timestamp":...,"server":"Windows VM GTO+ Service"}
```

## 🔧 Configuration and Customization

### Update Your Local Environment

Add to your `.env` file:

```bash
# Add your Windows VM endpoint
GTO_SOLVER_URL=http://192.168.1.100:8080
OPENAI_API_KEY=your-openai-key
```

### Customize GTO+ Integration

To integrate with actual GTO+ software (when you have it):

1. **Install GTO+ on Windows VM**
2. **Update the service script** in the Ansible playbook:

```python
# Replace the mock analysis section with:
result = subprocess.run([
    "C:\\path\\to\\GTOplus.exe",  # Adjust path
    "--analyze",
    temp_file,
    "--output", f"result_{hand_id}.json"
], capture_output=True, text=True, timeout=300)

# Read actual results
with open(f"result_{hand_id}.json", 'r') as f:
    solver_output = json.load(f)
```

## 🔍 Monitoring and Troubleshooting

### Service Management

```powershell
# On Windows VM - check service status
Get-Service GTOService

# View service logs
Get-Content C:\gto-service\gto_service.log -Tail 50

# Restart service
Restart-Service GTOService
```

### Network Troubleshooting

```bash
# Test network connectivity from Mac
ping 192.168.1.100
telnet 192.168.1.100 8080

# Check Windows firewall
# On Windows VM:
Get-NetFirewallRule -DisplayName "GTO Service"
```

## 🎯 Next Steps

1. **Run the Ansible playbook** to set up your Windows VM
2. **Test the connection** using curl
3. **Update your .env file** with the VM endpoint
4. **Run your GTO Assistant**: `make run`
5. **Install actual GTO+ software** when ready
6. **Update the service script** to use real GTO+ analysis

## 🔐 Security Considerations

### Home Lab Security
- **Network isolation**: Keep VM on isolated VLAN if possible
- **Firewall rules**: Restrict access to necessary ports only
- **Regular updates**: Keep Windows VM updated
- **Strong passwords**: Use complex passwords for accounts

### Production Upgrades
- **HTTPS/SSL**: Add SSL certificates for encrypted communication
- **Authentication**: Implement API key authentication
- **Rate limiting**: Add request rate limiting
- **Monitoring**: Set up proper logging and monitoring

This setup provides a fully automated way to configure your Windows 11 VM as a GTO+ solver node with minimal manual intervention after the initial WinRM setup.

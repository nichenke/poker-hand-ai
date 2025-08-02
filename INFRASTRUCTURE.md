# GTO+ Remote Solver Infrastructure

This document outlines the infrastructure setup for running GTO+ solver on a remote Windows node.

## 🏗️ Infrastructure Options

### Option 1: AWS EC2 Windows Instance (Recommended)

**Instance Type:** `m5.xlarge` or `m5.2xlarge`
- **vCPUs:** 4-8 cores
- **RAM:** 16-32 GB
- **Storage:** 100GB SSD
- **OS:** Windows Server 2019/2022

**Setup Steps:**
```bash
# 1. Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type m5.xlarge \
    --key-name your-key-pair \
    --security-groups gto-solver-sg

# 2. Configure Security Group
aws ec2 authorize-security-group-ingress \
    --group-name gto-solver-sg \
    --protocol tcp \
    --port 8080 \
    --source-group your-client-sg
```

### Option 2: Azure Virtual Machine

**VM Size:** `Standard_D4s_v3` or `Standard_D8s_v3`
- **vCPUs:** 4-8 cores
- **RAM:** 16-32 GB
- **Storage:** Premium SSD
- **OS:** Windows 10/11 or Server 2019

### Option 3: Local Windows Machine/VM

**Minimum Requirements:**
- **CPU:** Intel i5/AMD Ryzen 5 or better
- **RAM:** 16GB minimum, 32GB recommended
- **Storage:** 50GB available space
- **OS:** Windows 10/11

## 🔧 GTO+ Solver Service Setup

### 1. Install GTO+ Software
```powershell
# Download and install GTO+ from official website
# Ensure license is properly activated
```

### 2. Create HTTP API Wrapper

Create a Python Flask service to wrap GTO+ commands:

```python
# gto_service.py
from flask import Flask, request, jsonify
import subprocess
import json
import os
import time

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/api/analyze', methods=['POST'])
def analyze_hand():
    try:
        data = request.json
        hand_id = data.get('hand_id')
        hand_history = data.get('hand_history')
        
        # Save hand to temp file
        temp_file = f"temp_hand_{hand_id}.txt"
        with open(temp_file, 'w') as f:
            f.write(hand_history)
        
        # Run GTO+ analysis (adjust command for your GTO+ installation)
        start_time = time.time()
        result = subprocess.run([
            "GTOplus.exe",  # Adjust path
            "--analyze",
            temp_file,
            "--output", f"result_{hand_id}.json"
        ], capture_output=True, text=True, timeout=300)
        
        processing_time = time.time() - start_time
        
        # Read results
        with open(f"result_{hand_id}.json", 'r') as f:
            solver_output = f.read()
        
        # Cleanup
        os.remove(temp_file)
        os.remove(f"result_{hand_id}.json")
        
        return jsonify({
            "solver_output": solver_output,
            "processing_time": processing_time,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### 3. Install Service Dependencies
```powershell
# Install Python and pip
# Install Flask
pip install flask

# Create Windows service (optional)
# Use NSSM or similar to run as Windows service
```

## 🚀 Deployment Scripts

### AWS CloudFormation Template

```yaml
# gto-solver-stack.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'GTO+ Solver Windows Instance'

Resources:
  GTOSolverInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c02fb55956c7d316  # Windows Server 2019
      InstanceType: m5.xlarge
      KeyName: !Ref KeyPairName
      SecurityGroupIds:
        - !Ref GTOSolverSecurityGroup
      UserData:
        Fn::Base64: !Sub |
          <powershell>
          # Install chocolatey
          Set-ExecutionPolicy Bypass -Scope Process -Force
          iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
          
          # Install Python
          choco install python -y
          
          # Install git
          choco install git -y
          
          # Clone and setup GTO service
          git clone https://github.com/nichenke/poker-hand-ai.git
          # Add your setup commands here
          </powershell>

  GTOSolverSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for GTO+ solver
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 8080
          ToPort: 8080
          SourceSecurityGroupId: !Ref ClientSecurityGroup
        - IpProtocol: tcp
          FromPort: 3389
          ToPort: 3389
          CidrIp: 0.0.0.0/0  # Restrict this to your IP

Parameters:
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: Name of an existing EC2 KeyPair
```

### Docker Alternative (Windows Containers)

```dockerfile
# Dockerfile.windows
FROM mcr.microsoft.com/windows/servercore:ltsc2019

# Install Python
RUN powershell -Command \
    Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe" -OutFile python-installer.exe; \
    Start-Process python-installer.exe -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait; \
    Remove-Item python-installer.exe

# Copy GTO+ software (you'll need to handle licensing)
COPY GTO+ /app/gto/

# Copy service
COPY gto_service.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install -r /app/requirements.txt

# Expose port
EXPOSE 8080

# Start service
CMD ["python", "/app/gto_service.py"]
```

## 🔐 Security Considerations

### Network Security
```bash
# VPC with private subnets
# VPN or bastion host access
# Security groups with minimal access
# SSL/TLS for API endpoints
```

### Access Control
```bash
# API authentication tokens
# Rate limiting
# Request validation
# Audit logging
```

## 📊 Monitoring & Scaling

### CloudWatch Metrics (AWS)
- CPU utilization
- Memory usage
- Network I/O
- API response times

### Auto Scaling (Optional)
```yaml
AutoScalingGroup:
  Type: AWS::AutoScaling::AutoScalingGroup
  Properties:
    MinSize: 1
    MaxSize: 3
    DesiredCapacity: 1
    TargetGroupARNs:
      - !Ref GTOSolverTargetGroup
```

## 💰 Cost Estimation

### AWS EC2 (m5.xlarge)
- **Compute:** ~$150/month (on-demand)
- **Storage:** ~$10/month (100GB)
- **Data Transfer:** Variable
- **Total:** ~$160-200/month

### Cost Optimization
- Use Spot Instances (70% savings)
- Reserved Instances (30-50% savings)
- Auto-scaling based on demand

## 🔧 Environment Variables

Set these in your local environment:

```bash
# Required
export GTO_SOLVER_URL="http://your-ec2-instance:8080"
export OPENAI_API_KEY="your-openai-key"

# Optional
export GTO_SOLVER_TIMEOUT="300"
export GTO_BATCH_SIZE="10"
```

## 📝 Next Steps

1. **Choose infrastructure option** (AWS EC2 recommended)
2. **Deploy Windows instance** with GTO+ software
3. **Set up HTTP API wrapper** using Flask service
4. **Configure security groups** and networking
5. **Test end-to-end pipeline** with sample hands
6. **Set up monitoring** and alerting
7. **Implement auto-scaling** (optional)

This setup provides a scalable, cloud-based solution for running GTO+ analysis remotely while maintaining your local development environment on macOS.

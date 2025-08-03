# Infrastructure Overview

Deployment options and architecture for the GTO Assistant system.

## 🏗️ Architecture

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Development   │    │   Windows Node   │    │   OpenAI API    │
│   (Mac/Linux)   │───▶│   (GTO+ Solver)  │    │   (Analysis)    │
│                 │    │                  │    │                 │
│ • Python Client │    │ • GTO+ Software  │    │ • GPT-4o        │
│ • Web Interface │    │ • Flask API      │    │ • Strategic     │
│ • Hand Files    │    │ • Solver Engine  │    │   Insights      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Deployment Options

### Option 1: Local Windows VM (Recommended for Development)

**Best for**: Development, testing, learning setups

**Pros**:
- Complete control over environment
- No cloud costs
- Fast iteration and debugging
- Works offline (except AI analysis)

**Cons**:
- Requires local Windows license
- Limited by local hardware
- Manual management

**Setup**: [Quick Start Guide](../application/quickstart.md)

### Option 2: AWS EC2 Windows Instance

**Best for**: Production workloads, team usage

**Instance Type**: `m5.xlarge` or `m5.2xlarge`
- **vCPUs**: 4-8 cores
- **RAM**: 16-32 GB
- **Storage**: 100GB SSD
- **OS**: Windows Server 2019/2022

**Pros**:
- Scalable compute power
- Professional-grade infrastructure
- Global availability
- Pay-per-use pricing

**Cons**:
- Ongoing cloud costs
- Windows licensing fees
- Network latency considerations

### Option 3: Azure Virtual Machine

**Best for**: Microsoft-centric environments

**VM Size**: `Standard_D4s_v3` or `Standard_D8s_v3`
- **vCPUs**: 4-8 cores
- **RAM**: 16-32 GB
- **Storage**: Premium SSD
- **OS**: Windows 10/11 or Server 2019

**Pros**:
- Excellent Windows integration
- Azure ecosystem benefits
- Flexible pricing options

**Cons**:
- Similar cost considerations to AWS
- Vendor lock-in potential

### Option 4: Dedicated Windows Server

**Best for**: High-volume production usage

**Minimum Requirements**:
- **CPU**: Intel i7/AMD Ryzen 7 or better
- **RAM**: 32GB+ recommended
- **Storage**: NVMe SSD, 500GB+
- **OS**: Windows Server 2019/2022

**Pros**:
- Maximum performance
- No cloud costs after setup
- Complete control

**Cons**:
- High upfront investment
- Maintenance overhead
- Single point of failure

## 🔧 Component Requirements

**Complete requirements:** See [System Requirements](../REQUIREMENTS.md)

**Architecture Summary:**
- **Development Machine**: Mac/Linux for development and control
- **Windows Node**: Windows VM/server running GTO+ solver and Flask API
- **Network**: Secure connectivity between components

## 🌐 Network Requirements

### Ports

- **5985**: WinRM (HTTP) - Ansible management
- **5986**: WinRM (HTTPS) - Secure Ansible management
- **8080**: Flask API - GTO service interface
- **8082**: GTO+ API - Direct solver access (optional)
- **22**: SSH - Remote development (optional)

### Bandwidth

- **Minimum**: 10 Mbps for hand uploads and results
- **Recommended**: 100 Mbps for comfortable development
- **Latency**: <100ms between development machine and Windows node

## 🔒 Security Considerations

### Network Security

- Use private networks (VPC/VNet) when possible
- Restrict inbound access to specific IP ranges
- Enable Windows Firewall with explicit rules
- Consider VPN for remote access

### Authentication

- Strong passwords for Windows accounts
- SSH key-based authentication where possible
- Regular credential rotation
- Separate service accounts for automation

### Data Protection

- Encrypt data in transit (HTTPS/SSH)
- Secure temporary file cleanup
- Regular backups of analysis results
- Compliance with data retention policies

## 📊 Performance Considerations

### CPU Requirements

- **Light Usage**: 4 cores sufficient for basic analysis
- **Heavy Usage**: 8+ cores for complex scenarios
- **Parallel Processing**: More cores enable faster batch processing

### Memory Planning

- **GTO+ Base**: 4-8GB for solver
- **Flask Service**: 1-2GB for API service
- **OS Overhead**: 4-6GB for Windows
- **Recommended Total**: 16-32GB

### Storage Planning

- **OS and Software**: 50GB
- **GTO+ Installation**: 10-20GB
- **Hand Files**: 1-10GB (depends on volume)
- **Analysis Results**: 5-50GB (depends on retention)
- **Logs and Temp**: 5-10GB

## 🚀 Getting Started

### For Development
1. Start with [Quick Start Guide](../application/quickstart.md)
2. Use local Windows VM
3. Follow [Windows Setup](windows-setup.md) for GTO+ installation

### For Production
1. Choose cloud provider (AWS/Azure recommended)
2. Follow [Windows Setup](windows-setup.md)
3. Configure [Ansible Automation](ansible.md)
4. Set up monitoring and backups

### For Remote Development
1. Complete basic setup
2. Follow [Remote SSH Setup](remote-ssh.md)
3. Configure VS Code for remote editing

## 📖 Next Steps

- **[Windows Setup Guide](windows-setup.md)** - Install and configure GTO+ on Windows
- **[Ansible Automation](ansible.md)** - Automated deployment and management
- **[Remote SSH Development](remote-ssh.md)** - VS Code remote development setup

## 🆘 Support

For infrastructure-related issues:
- Check the troubleshooting sections in specific guides
- Review Windows Event Logs for service issues
- Verify network connectivity between components
- Consult cloud provider documentation for platform-specific issues

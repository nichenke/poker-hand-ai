# System Requirements

Complete system requirements for the GTO Assistant poker analysis system.

## 🖥️ Development Machine (Mac/Linux)

**Required Software:**
- Git
- Python 3.11+ with pipenv
- VS Code (recommended for development)
- SSH client (built into macOS/Linux)

## 🪟 Windows Node (GTO+ Solver)

**Hardware Requirements:**
- **OS**: Windows 10/11 or Server 2019+
- **RAM**: 16GB minimum (32GB+ recommended for complex solves)
- **CPU**: 4+ cores (8+ cores recommended for performance)
- **Storage**: 100GB+ free space on SSD

**Required Software:**
- **[GTO+ solver software](https://www.gtoplus.com/)** (licensed) - Professional poker analysis tool
- PowerShell 5.1+
- Windows Remote Management (WinRM)

**Learning GTO+:** New to GTO+? Check out the **[Red Chip Poker GTO+ Course](https://redchippoker.com/courses/gto-plus/)** for comprehensive training.

## 🌐 Network Requirements

**Development Environment:**
- **Local VM**: Direct network connectivity between Mac and Windows VM
- **Cloud Deployment**: Internet access for both machines
- **Remote Development**: SSH connectivity for VS Code remote editing

**Required Ports:**
- **8080**: GTO+ Flask API service
- **5985**: WinRM (HTTP) - Ansible management  
- **5986**: WinRM (HTTPS) - Secure Ansible management (optional)
- **22**: SSH (for remote development)

## ⚡ Performance Considerations

**For Basic Analysis:**
- 16GB RAM sufficient for most poker scenarios
- 4-core CPU handles standard solving workloads

**For Advanced/Professional Use:**
- 32GB+ RAM recommended for complex solves
- 8+ core CPU for faster solving and parallel processing
- NVMe SSD for faster I/O during large batch processing

## 🔧 Quick Compatibility Check

**Development Machine:**
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check Git
git --version

# Check SSH
ssh -V
```

**Windows Node:**
```powershell
# Check PowerShell version
$PSVersionTable.PSVersion  # Should be 5.1+

# Check available RAM
Get-ComputerInfo -Property TotalPhysicalMemory

# Check CPU cores
(Get-ComputerInfo).CsProcessors.NumberOfCores
```

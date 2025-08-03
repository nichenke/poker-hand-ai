# Windows Setup Guide

Complete guide for installing and configuring GTO+ on Windows for the poker analysis system.

## 📋 Prerequisites

### System Requirements

- **OS**: Windows 10/11 or Server 2019/2022
- **RAM**: 16GB minimum, 32GB+ recommended for large solves
- **CPU**: Intel i5/AMD Ryzen 5 or better (8+ cores recommended)
- **Storage**: 100GB+ free space on fast SSD
- **Network**: Reliable internet connection

### Access Requirements

- Administrator privileges on Windows machine
- Valid GTO+ license (if using real solver)
- Network connectivity to development machine

## 🚀 GTO+ Installation

### 1. Download and Install GTO+

```powershell
# Download from official source
# Visit: https://www.gtowizard.com/gto-plus/
# Or download installer directly

# Run installer as Administrator
# Install to default location: C:\Program Files\GTO\
```

### 2. License Activation

```powershell
# Launch GTO+
Start-Process "C:\Program Files\GTO\GTO+.exe"

# Enter license key in GUI
# Verify solver engines are loaded
# Test with a simple preflop scenario
```

### 3. API Mode Configuration

```powershell
# Create startup script
$scriptPath = "C:\Scripts\gto_api_start.bat"
New-Item -ItemType Directory -Force -Path "C:\Scripts"

# Create batch file for API mode
@"
@echo off
cd "C:\Program Files\GTO\"
GTO+.exe --api-mode --port=8082 --memory=16GB --log-level=info
"@ | Out-File -FilePath $scriptPath -Encoding ASCII

# Test API mode
& $scriptPath
```

## 🔧 Windows Configuration

### 4. Windows Firewall Setup

```powershell
# Allow GTO+ through firewall
New-NetFirewallRule -DisplayName "GTO+ Solver" -Direction Inbound -Program "C:\Program Files\GTO\GTO+.exe" -Action Allow

# Allow API ports
New-NetFirewallRule -DisplayName "GTO+ API Port" -Direction Inbound -Protocol TCP -LocalPort 8082 -Action Allow
New-NetFirewallRule -DisplayName "Flask Service Port" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow

# Allow WinRM for Ansible
New-NetFirewallRule -DisplayName "WinRM HTTP" -Direction Inbound -Protocol TCP -LocalPort 5985 -Action Allow
```

### 5. Performance Optimization

```powershell
# Set high performance power plan
powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# Disable Windows Search indexing on GTO+ folder
$gtoPath = "C:\Program Files\GTO"
$indexer = Get-WmiObject -Class Win32_Volume | Where-Object {$_.DriveLetter -eq "C:"}
$indexer.IndexingEnabled = $false
$indexer.Put()

# Increase virtual memory
$computerSystem = Get-WmiObject Win32_ComputerSystem
$totalRAM = [math]::round($computerSystem.TotalPhysicalMemory / 1GB)
$pageFileSize = $totalRAM * 2  # 2x RAM size

# Configure page file (requires reboot)
$pageFile = Get-WmiObject -Class Win32_PageFileSetting
if ($pageFile) {
    $pageFile.Delete()
}
Set-WmiInstance -Class Win32_PageFileSetting -Arguments @{
    name = "C:\pagefile.sys"
    InitialSize = $pageFileSize * 1024
    MaximumSize = $pageFileSize * 1024
}
```

### 6. Service Management

```powershell
# Install NSSM for service management
$nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
$nssmZip = "C:\temp\nssm.zip"
$nssmDir = "C:\nssm"

# Download and extract NSSM
New-Item -ItemType Directory -Force -Path C:\temp
Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip
Expand-Archive -Path $nssmZip -DestinationPath C:\temp -Force
Move-Item -Path "C:\temp\nssm-2.24" -Destination $nssmDir -Force

# Create GTO+ service
& "$nssmDir\win64\nssm.exe" install GTOPlusService "C:\Scripts\gto_api_start.bat"
& "$nssmDir\win64\nssm.exe" set GTOPlusService Start SERVICE_AUTO_START
& "$nssmDir\win64\nssm.exe" set GTOPlusService DisplayName "GTO+ API Service"
& "$nssmDir\win64\nssm.exe" set GTOPlusService Description "GTO+ Solver API Service"

# Start service
Start-Service GTOPlusService
```

## 🔗 API Integration

### 7. Test GTO+ API

```powershell
# Verify API endpoint
$response = Invoke-RestMethod -Uri "http://localhost:8082/health" -Method Get
Write-Output "GTO+ API Status: $($response.status)"

# Test solver request
$testData = @{
    scenario = @{
        position = "BTN"
        effective_stack = 100
        pot_size = 3
        board = @()
        action_sequence = @("raise", "call")
    }
    settings = @{
        accuracy = "medium"
        max_time = 60
    }
} | ConvertTo-Json -Depth 3

$headers = @{"Content-Type" = "application/json"}
$solveResponse = Invoke-RestMethod -Uri "http://localhost:8082/solve" -Method Post -Body $testData -Headers $headers
Write-Output "Solve completed: $($solveResponse.status)"
```

### 8. Flask Service Setup

The Flask service is automatically installed via Ansible. For manual setup:

```powershell
# Install Python dependencies
pip install flask requests

# Create service directory
New-Item -ItemType Directory -Force -Path "C:\gto-service"

# Copy service file (from ansible/gto_service.py)
# Configure port and GTO+ integration
```

## 🔧 Advanced Configuration

### 9. Solver Optimization

```powershell
# Configure GTO+ settings file
$configPath = "$env:APPDATA\GTO\config.ini"
$config = @"
[Solver]
memory_allocation=80
cpu_cores=all
accuracy=high
cache_size=2048
auto_save=true

[API]
port=8082
timeout=300
max_concurrent=2
"@

$config | Out-File -FilePath $configPath -Encoding UTF8
```

### 10. Monitoring Setup

```powershell
# Create performance monitoring script
$monitorScript = @"
# Monitor GTO+ performance
while (`$true) {
    `$gtoProcess = Get-Process -Name "GTO+" -ErrorAction SilentlyContinue
    if (`$gtoProcess) {
        `$cpu = `$gtoProcess.CPU
        `$memory = [math]::round(`$gtoProcess.WorkingSet64 / 1MB, 2)
        Write-Output "GTO+ - CPU: `$cpu, Memory: `$memory MB"
    }
    Start-Sleep -Seconds 30
}
"@

$monitorScript | Out-File -FilePath "C:\Scripts\monitor_gto.ps1" -Encoding UTF8
```

## 🛠️ Troubleshooting

### Common Issues

**GTO+ API not responding:**
```powershell
# Check if GTO+ is running
Get-Process -Name "GTO+" -ErrorAction SilentlyContinue

# Check port availability
Test-NetConnection -ComputerName localhost -Port 8082

# Restart service
Restart-Service GTOPlusService
```

**Performance issues:**
```powershell
# Check memory usage
Get-Counter "\Memory\Available MBytes"

# Check CPU temperature (if supported)
Get-WmiObject -Namespace "root\wmi" -Class MSAcpi_ThermalZoneTemperature

# Check disk performance
Get-Counter "\PhysicalDisk(*)\Avg. Disk Queue Length"
```

**Network connectivity:**
```powershell
# Test from development machine
Test-NetConnection -ComputerName YOUR_WINDOWS_IP -Port 8080

# Check Windows Firewall rules
Get-NetFirewallRule -DisplayName "*GTO*" | Select-Object DisplayName, Enabled, Direction
```

### Logs and Diagnostics

```powershell
# GTO+ logs
Get-Content "C:\Users\$env:USERNAME\AppData\Local\GTO\logs\gto.log" -Tail 20

# Windows Event Logs
Get-EventLog -LogName Application -Source "GTO+" -Newest 10

# Service logs
Get-Content "C:\gto-service\gto_service.log" -Tail 20
```

## 🔒 Security Considerations

### User Account Setup

```powershell
# Create dedicated service account
$username = "gto-service"
$password = ConvertTo-SecureString "YourSecurePassword123!" -AsPlainText -Force

New-LocalUser -Name $username -Password $password -Description "GTO+ Service Account"
Add-LocalGroupMember -Group "Users" -Member $username

# Grant necessary permissions
$acl = Get-Acl "C:\gto-service"
$permission = $username, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
$acl.SetAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule $permission))
Set-Acl "C:\gto-service" $acl
```

### Network Security

```powershell
# Restrict API access to specific IPs
$allowedIPs = @("192.168.1.100", "10.0.0.50")  # Your development machines

foreach ($ip in $allowedIPs) {
    New-NetFirewallRule -DisplayName "GTO API - $ip" -Direction Inbound -RemoteAddress $ip -Protocol TCP -LocalPort 8080,8082 -Action Allow
}

# Remove default allow rules
Remove-NetFirewallRule -DisplayName "GTO+ API Port"
```

## 📁 File Locations

### Important Paths

- **GTO+ Installation**: `C:\Program Files\GTO\`
- **GTO+ Configuration**: `%APPDATA%\GTO\`
- **GTO+ Logs**: `%LOCALAPPDATA%\GTO\logs\`
- **Flask Service**: `C:\gto-service\`
- **Scripts**: `C:\Scripts\`
- **NSSM**: `C:\nssm\`

### Backup Recommendations

```powershell
# Backup script
$backupPath = "C:\Backups\GTO"
New-Item -ItemType Directory -Force -Path $backupPath

# Backup configuration
Copy-Item "$env:APPDATA\GTO" -Destination "$backupPath\config" -Recurse -Force

# Backup service files
Copy-Item "C:\gto-service" -Destination "$backupPath\service" -Recurse -Force

# Backup scripts
Copy-Item "C:\Scripts" -Destination "$backupPath\scripts" -Recurse -Force
```

## 🎯 Next Steps

- **[Ansible Automation](ansible.md)** - Automate this setup process
- **[Remote SSH Development](remote-ssh.md)** - Enable remote editing with VS Code
- **[API Integration](../development/api.md)** - Integrate with your applications

## 📞 Support Resources

- **GTO+ Documentation**: Official GTO Wizard documentation
- **Windows Server Admin**: Microsoft documentation
- **Python Integration**: Requests library documentation

---

**Note**: This guide assumes you have a valid GTO+ license. Contact GTO Wizard support for licensing questions or GTO+-specific technical issues.

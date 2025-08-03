# GTO+ Windows Server Setup Guide

Quick setup guide for installing GTO+ on Windows Server and configuring it for API integration.

## Prerequisites

- Windows Server 2019/2022 (recommended)
- Administrator access
- Minimum 8GB RAM, 16GB+ recommended for large solver runs
- Fast SSD storage (100GB+ free space)

## GTO+ Installation

### 1. Download and Install GTO+
```
1. Visit: https://www.gtowizard.com/gto-plus/
2. Download the Windows installer
3. Run as Administrator
4. Install to default location: C:\Program Files\GTO\
```

### 2. License Activation
```
1. Launch GTO+
2. Enter your license key
3. Verify solver engines are loaded
4. Test with a simple preflop scenario
```

## Windows Server Configuration

### 3. Configure Windows Firewall
```powershell
# Allow GTO+ through firewall (run as Administrator)
New-NetFirewallRule -DisplayName "GTO+ Solver" -Direction Inbound -Program "C:\Program Files\GTO\GTO+.exe" -Action Allow
New-NetFirewallRule -DisplayName "GTO+ API Port" -Direction Inbound -Protocol TCP -LocalPort 8080-8090 -Action Allow
```

### 4. Windows Service Setup (Optional)
Create a Windows service to auto-start GTO+ API mode:

```batch
# Create service script: C:\Scripts\gto_service.bat
@echo off
cd "C:\Program Files\GTO\"
GTO+.exe --api-mode --port=8082
```

### 5. Performance Optimization
```
1. Set GTO+ process priority to "High" in Task Manager
2. Configure Windows power plan to "High Performance"
3. Disable Windows indexing on GTO+ folder
4. Increase virtual memory to 32GB+
```

## API Integration Setup

### 6. GTO+ API Configuration
```
1. Launch GTO+ with API mode:
   "C:\Program Files\GTO\GTO+.exe" --api-mode --port=8082

2. Verify API endpoint:
   http://localhost:8082/health

3. Test solver request:
   curl -X POST http://localhost:8082/solve -H "Content-Type: application/json" -d "{\"scenario\":\"test\"}"
```

### 7. Python Client Configuration
Update your Python code to connect to Windows server:

```python
# In your gto_assistant_preloaded.py or solver integration
GTO_API_HOST = "your-windows-server-ip"  # e.g., "192.168.1.100"
GTO_API_PORT = 8082
GTO_API_URL = f"http://{GTO_API_HOST}:{GTO_API_PORT}"

# Test connection
import requests
response = requests.get(f"{GTO_API_URL}/health", timeout=10)
print(f"GTO+ API Status: {response.status_code}")
```

### 8. Network Configuration
```
1. Ensure Windows Server can communicate with your Python server
2. Configure any firewalls/routers between servers
3. Test network connectivity:
   ping your-python-server-ip
   telnet your-python-server-ip 8081
```

## Solver Configuration

### 9. GTO+ Solver Settings
```
1. Memory allocation: Set to 80% of available RAM
2. CPU cores: Use all available cores
3. Accuracy: Set to "High" for production
4. Cache size: 2GB+ for frequent scenarios
5. Auto-save: Enable for long-running solves
```

### 10. API Request Optimization
```python
# Recommended API request structure
solver_request = {
    "scenario": {
        "position": "BTN",
        "effective_stack": 100,
        "pot_size": 3,
        "board": [],
        "action_sequence": ["raise", "call"]
    },
    "settings": {
        "accuracy": "high",
        "max_time": 300,  # 5 minutes max
        "memory_limit": "8GB"
    }
}
```

## Monitoring & Troubleshooting

### 11. Performance Monitoring
```
1. Monitor CPU/RAM usage during solves
2. Check GTO+ logs: C:\Users\%USERNAME%\AppData\Local\GTO\logs\
3. Set up Windows Performance Monitor for detailed metrics
4. Monitor network latency between servers
```

### 12. Common Issues & Solutions

**GTO+ API not responding:**
```
- Check Windows Firewall settings
- Verify GTO+ is running in API mode
- Restart GTO+ service
```

**Slow solver performance:**
```
- Increase RAM allocation
- Use SSD storage
- Reduce solver accuracy for testing
- Check CPU thermal throttling
```

**Network connectivity issues:**
```
- Test with telnet: telnet server-ip 8082
- Check router/firewall rules
- Verify correct IP addresses in code
```

## Production Deployment

### 13. Automation Scripts
Create batch files for common operations:

```batch
# start_gto_api.bat
@echo off
echo Starting GTO+ API Server...
cd "C:\Program Files\GTO\"
GTO+.exe --api-mode --port=8082 --memory=12GB --log-level=info

# stop_gto_api.bat
@echo off
taskkill /IM "GTO+.exe" /F
echo GTO+ API Server stopped
```

### 14. Backup & Recovery
```
1. Backup GTO+ configuration: C:\Users\%USERNAME%\AppData\Local\GTO\
2. Export solver presets and ranges
3. Create system restore point before major changes
4. Schedule regular Windows Server backups
```

## Security Considerations

### 15. Server Hardening
```
1. Disable unnecessary Windows services
2. Configure Windows Updates for manual installation
3. Use Windows Defender or enterprise antivirus
4. Restrict RDP access to specific IPs
5. Enable Windows Event Logging
```

### 16. API Security
```python
# Add API authentication in your Python client
headers = {
    "Authorization": "Bearer your-api-token",
    "Content-Type": "application/json"
}

# Use HTTPS in production
GTO_API_URL = "https://your-server:8082"
```

## Testing Checklist

- [ ] GTO+ launches and activates license
- [ ] API mode starts on specified port
- [ ] Python client can connect to GTO+ API
- [ ] Simple solver request completes successfully
- [ ] Performance meets requirements (< 5min for standard scenarios)
- [ ] Network connectivity stable between servers
- [ ] Firewall allows necessary traffic
- [ ] Monitoring and logging operational

## Support Resources

- GTO+ Documentation: [Official Docs](https://docs.gtowizard.com/)
- Windows Server Admin Guide: [Microsoft Docs](https://docs.microsoft.com/en-us/windows-server/)
- Python requests library: [Requests Docs](https://docs.python-requests.org/)

---

**Note:** This guide assumes you have a valid GTO+ license. Contact GTO Wizard support for licensing questions or technical issues specific to the GTO+ software.

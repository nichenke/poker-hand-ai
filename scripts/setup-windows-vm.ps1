# Windows VM Initial Setup Script
# Run this ONCE on your Windows 11 VM as Administrator

Write-Host "Setting up Windows VM for Ansible management..." -ForegroundColor Green

# Set execution policy
Set-ExecutionPolicy RemoteSigned -Force
Write-Host "✓ Execution policy set" -ForegroundColor Green

# Enable WinRM
Enable-PSRemoting -Force
winrm quickconfig -force
Write-Host "✓ WinRM enabled" -ForegroundColor Green

# Configure WinRM for Ansible
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="1024"}'
Write-Host "✓ WinRM configured for Ansible" -ForegroundColor Green

# Create Ansible user
$Username = "ansible"
$Password = Read-Host "Enter password for ansible user" -AsSecureString
try {
    New-LocalUser -Name $Username -Password $Password -Description "Ansible automation user" -PasswordNeverExpires
    Add-LocalGroupMember -Group "Administrators" -Member $Username
    Write-Host "✓ Ansible user created and added to Administrators" -ForegroundColor Green
} catch {
    Write-Host "⚠ User may already exist or error occurred: $_" -ForegroundColor Yellow
}

# Configure Windows Firewall for WinRM
New-NetFirewallRule -DisplayName "WinRM HTTP" -Direction Inbound -Protocol TCP -LocalPort 5985 -Action Allow
Write-Host "✓ Firewall configured for WinRM" -ForegroundColor Green

# Get and display IP address
$IP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}).IPAddress
Write-Host "✓ VM IP Address: $IP" -ForegroundColor Cyan

Write-Host "`nSetup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Update ansible/inventory.yml with IP: $IP" -ForegroundColor White
Write-Host "2. Update ansible/inventory.yml with the password you just set" -ForegroundColor White
Write-Host "3. From your Mac, run: make test-windows" -ForegroundColor White
Write-Host "4. If test passes, run: make setup-windows" -ForegroundColor White

# Windows VM Credential Verification Script
# Run this on your Windows VM to verify the ansible user

Write-Host "Checking ansible user configuration..." -ForegroundColor Green

# Check if user exists
try {
    $user = Get-LocalUser -Name "ansible" -ErrorAction Stop
    Write-Host "✅ User 'ansible' exists" -ForegroundColor Green
    Write-Host "   Full Name: $($user.FullName)" -ForegroundColor Gray
    Write-Host "   Description: $($user.Description)" -ForegroundColor Gray
    Write-Host "   Enabled: $($user.Enabled)" -ForegroundColor Gray
    Write-Host "   Password Expires: $($user.PasswordExpires)" -ForegroundColor Gray
} catch {
    Write-Host "❌ User 'ansible' does not exist" -ForegroundColor Red
    Write-Host "Run the setup script again to create the user" -ForegroundColor Yellow
    exit 1
}

# Check group membership
try {
    $adminMembers = Get-LocalGroupMember -Group "Administrators" | Where-Object {$_.Name -like "*ansible*"}
    if ($adminMembers) {
        Write-Host "✅ User 'ansible' is in Administrators group" -ForegroundColor Green
    } else {
        Write-Host "❌ User 'ansible' is NOT in Administrators group" -ForegroundColor Red
        Write-Host "Adding to Administrators group..." -ForegroundColor Yellow
        Add-LocalGroupMember -Group "Administrators" -Member "ansible"
        Write-Host "✅ Added to Administrators group" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Error checking group membership: $_" -ForegroundColor Yellow
}

# Check WinRM configuration
Write-Host "`nChecking WinRM configuration..." -ForegroundColor Green
$winrmConfig = winrm get winrm/config/service/auth
Write-Host $winrmConfig

# Test WinRM listener
Write-Host "`nChecking WinRM listeners..." -ForegroundColor Green
winrm enumerate winrm/config/listener

# Check firewall rule
Write-Host "`nChecking firewall rule..." -ForegroundColor Green
$firewallRule = Get-NetFirewallRule -DisplayName "WinRM HTTP" -ErrorAction SilentlyContinue
if ($firewallRule) {
    Write-Host "✅ WinRM HTTP firewall rule exists" -ForegroundColor Green
    Write-Host "   Enabled: $($firewallRule.Enabled)" -ForegroundColor Gray
} else {
    Write-Host "❌ WinRM HTTP firewall rule missing" -ForegroundColor Red
    Write-Host "Creating firewall rule..." -ForegroundColor Yellow
    New-NetFirewallRule -DisplayName "WinRM HTTP" -Direction Inbound -Protocol TCP -LocalPort 5985 -Action Allow
    Write-Host "✅ Firewall rule created" -ForegroundColor Green
}

# Test password (optional manual verification)
Write-Host "`nTo test password manually, run:" -ForegroundColor Cyan
Write-Host "runas /user:ansible cmd" -ForegroundColor White
Write-Host "(This will prompt for password - use the same one from inventory.yml)" -ForegroundColor Gray

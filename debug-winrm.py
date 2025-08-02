#!/usr/bin/env python3
"""
Debug script to test WinRM connection directly
"""
import winrm
import yaml
import os
import getpass

# Read configuration from inventory.yml
try:
    with open("ansible/inventory.yml", "r") as f:
        inventory = yaml.safe_load(f)

    host_config = inventory["all"]["hosts"]["gto-solver"]
    host = host_config["ansible_host"]
    username = host_config["ansible_user"]
    port = host_config.get("ansible_port", 5985)

    # Get password from environment or prompt user
    password = os.getenv("ANSIBLE_PASSWORD")
    if not password:
        password = getpass.getpass(f"Enter password for {username}@{host}: ")

except Exception as e:
    print(f"❌ Error reading inventory: {e}")
    print("Make sure ansible/inventory.yml exists and is properly configured")
    exit(1)

print(f"Testing WinRM connection to {host}:{port}")
print(f"Username: {username}")
print(f"Password: {'*' * len(password)}")

try:
    # Create WinRM session
    session = winrm.Session(
        f"http://{host}:{port}/wsman", auth=(username, password), transport="basic"
    )

    # Test basic command
    result = session.run_cmd('echo "Hello from Windows"')

    if result.status_code == 0:
        print("✅ Connection successful!")
        print(f"Output: {result.std_out.decode().strip()}")
    else:
        print("❌ Command failed")
        print(f"Status: {result.status_code}")
        print(f"Error: {result.std_err.decode()}")

except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting steps:")
    print("1. Verify the Windows VM IP address is correct")
    print("2. Check that the 'ansible' user exists on Windows")
    print("3. Verify the password is correct")
    print("4. Ensure WinRM is running on Windows")
    print("5. Check Windows firewall allows port 5985")

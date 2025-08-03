#!/usr/bin/env python3
"""
GTO+ Service Remote Test Script

This script tests the GTO+ service wrapper API running on a Windows VM.
Run this from your Mac/Linux machine to test the remote service.

Usage:
    python test-gto-service.py [--host <ip_address>] [--port <port>]

Examples:
    python test-gto-service.py --host 192.168.1.100 --port 8080
    python test-gto-service.py  # Uses default host from .env
"""

import requests
import json
import time
import sys
import argparse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_service_url(host=None, port=None):
    """Get the service URL from arguments or environment"""
    if host and port:
        return f"http://{host}:{port}"

    # Try to get from environment
    env_url = os.getenv("GTO_SOLVER_URL")
    if env_url:
        return env_url.rstrip("/")

    # Default fallback
    default_host = os.getenv("GTO_SERVICE_HOST", "192.168.1.100")
    default_port = os.getenv("GTO_SERVICE_PORT", "8080")
    return f"http://{default_host}:{default_port}"


def test_endpoint(url, method="GET", data=None, expected_status=200, timeout=30):
    """Test a single API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {method} {url}")
    print(f"{'='*60}")

    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        else:
            print(f"Unsupported method: {method}")
            return False

        print(f"Status Code: {response.status_code}")

        try:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
        except (ValueError, json.JSONDecodeError):
            print(f"Response Text: {response.text[:500]}...")

        success = response.status_code == expected_status
        print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
        return success

    except requests.exceptions.Timeout:
        print(f"Request timed out after {timeout}s")
        print("Result: ❌ FAIL (TIMEOUT)")
        return False
    except requests.exceptions.ConnectionError:
        print("Connection failed - check if service is running and accessible")
        print("Result: ❌ FAIL (CONNECTION)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        print("Result: ❌ FAIL")
        return False


def test_connection(base_url):
    """Test basic connectivity to the service"""
    print(f"\n🔍 Testing connection to: {base_url}")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Service is reachable")
            return True
        else:
            print(f"❌ Service returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach service: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check if the Windows VM is running")
        print("2. Verify the IP address and port")
        print("3. Check Windows Firewall settings")
        print("4. Ensure the GTO service is started")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test GTO+ Service API")
    parser.add_argument("--host", help="Service host IP address")
    parser.add_argument("--port", help="Service port number")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Get service URL
    base_url = get_service_url(args.host, args.port)

    print("🚀 GTO+ Service Remote Test Suite")
    print(f"Service URL: {base_url}")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Test basic connectivity first
    if not test_connection(base_url):
        sys.exit(1)

    results = []

    # Test 1: Service Health Check
    print("\n📊 Running API Tests...")
    results.append(test_endpoint(f"{base_url}/health"))

    # Test 2: GTO+ Health Check
    results.append(test_endpoint(f"{base_url}/gto/health"))

    # Test 3: GTO+ Info
    results.append(test_endpoint(f"{base_url}/gto/info"))

    # Test 4: Legacy Mock Analysis
    print("\n🎯 Testing Legacy Analysis Endpoint...")
    mock_hand_data = {
        "hand_id": "remote_test_001",
        "hand_history": """PokerStars Hand #123456789: Tournament #999999999, $10+$1 USD Hold'em No Limit - Level V (30/60) - 2024/01/01 12:00:00 ET
Table '999999999 1' 9-max Seat #1 is the button
Seat 1: Hero (1500 in chips)
Seat 2: Villain (1500 in chips)
Hero: posts small blind 30
Villain: posts big blind 60
*** HOLE CARDS ***
Dealt to Hero [Ah Kh]
Hero: raises 120 to 180
Villain: calls 120
*** FLOP *** [Kc 7d 2s]
Villain: checks
Hero: bets 240
Villain: folds
Hero collected 360 from pot
*** SUMMARY ***
Total pot 360 | Rake 0
Board [Kc 7d 2s]
Seat 1: Hero (button) (small blind) collected (360)
Seat 2: Villain (big blind) folded on the Flop""",
    }
    results.append(test_endpoint(f"{base_url}/api/analyze", "POST", mock_hand_data))

    # Test 5: GTO+ Solve (if GTO+ is available)
    print("\n🧠 Testing GTO+ Solve Endpoint...")
    print("Note: This requires GTO+ to be running on the Windows VM")

    gto_solve_data = {
        "scenario": {
            "position": "BTN",
            "effective_stack": 100,
            "pot_size": 3,
            "board": [],
            "action_sequence": ["raise", "call"],
        },
        "settings": {"accuracy": "medium", "max_time": 60},
    }
    results.append(
        test_endpoint(f"{base_url}/gto/solve", "POST", gto_solve_data, timeout=90)
    )

    # Summary
    print("\n" + "=" * 70)
    print("📈 TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("🎉 All tests passed! Remote GTO+ Service is working correctly.")
        print("\n✅ You can now use this service URL in your .env file:")
        print(f"GTO_SOLVER_URL={base_url}")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\n🔧 Common issues and solutions:")
        print("1. GTO+ not running: Start GTO+ in API mode on Windows VM")
        print("2. Firewall blocking: Check Windows Firewall rules")
        print("3. Network issues: Verify IP address and network connectivity")
        sys.exit(1)


if __name__ == "__main__":
    main()

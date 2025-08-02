#!/usr/bin/env python3
"""
Test script to verify communication with remote Windows GTO service
"""
import requests
import json
import time
import sys
from datetime import datetime

# Configuration from inventory.yml
WINDOWS_VM_IP = "192.168.15.234"
SERVICE_PORT = 8080
BASE_URL = f"http://{WINDOWS_VM_IP}:{SERVICE_PORT}"


def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check PASSED")
            print(f"   Status: {data.get('status')}")
            print(f"   Server: {data.get('server')}")
            print(f"   Timestamp: {datetime.fromtimestamp(data.get('timestamp', 0))}")
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("   Check if:")
        print("   - Windows VM is running")
        print("   - GTO service is started")
        print("   - Firewall allows port 8080")
        print("   - IP address is correct")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_analysis_endpoint():
    """Test the analysis endpoint with sample data"""
    print("\n🔍 Testing analysis endpoint...")

    sample_hand = {
        "hand_id": "test_001",
        "hand_history": """PokerStars Hand #123456789: Tournament #987654321, $10+$1 USD Hold'em No Limit - Level V (30/60) - 2024/01/15 20:30:00 ET
Table '987654321 123' 9-max Seat #3 is the button
Seat 1: Player1 (2850 in chips)
Seat 2: Player2 (3200 in chips)
Seat 3: Hero (2940 in chips)
*** HOLE CARDS ***
Dealt to Hero [Kh Ks]
Player1: folds
Player2: raises 120 to 180
Hero: raises 300 to 480
Player2: calls 300
*** FLOP *** [9s 4h 2c]
Player2: checks
Hero: bets 600
Player2: calls 600
*** TURN *** [9s 4h 2c] [7d]
Player2: checks
Hero: bets 1200
Player2: folds
Hero collected 2160 from pot
*** SUMMARY ***
Total pot 2160 | Rake 0
Board [9s 4h 2c 7d]
Seat 1: Player1 folded before Flop (didn't bet)
Seat 2: Player2 folded on the Turn
Seat 3: Hero (button) collected (2160)""",
    }

    try:
        print(f"   Sending hand analysis request...")
        response = requests.post(
            f"{BASE_URL}/api/analyze", json=sample_hand, timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Analysis request PASSED")
            print(f"   Hand ID: {data.get('hand_id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Processing time: {data.get('processing_time', 0):.2f}s")

            # Display solver output preview
            solver_output = data.get("solver_output", "")
            if solver_output:
                print("   Solver output preview:")
                lines = solver_output.split("\\n")[:3]
                for line in lines:
                    print(f"     {line}")
                if len(solver_output.split("\\n")) > 3:
                    print("     ...")

            # Display ranges if available
            ranges = data.get("ranges", {})
            if ranges:
                print("   Position ranges:")
                for pos, range_str in list(ranges.items())[:2]:
                    print(f"     {pos}: {range_str}")

            return True
        else:
            print(f"❌ Analysis failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Analysis request timed out (>15s)")
        return False
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False


def test_performance():
    """Test multiple requests to check performance"""
    print("\n🔍 Testing performance (3 quick requests)...")

    times = []
    for i in range(3):
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"   Request {i+1}: {elapsed:.3f}s")
        except Exception as e:
            print(f"   Request {i+1}: Failed - {e}")
            return False

    avg_time = sum(times) / len(times)
    print(f"✅ Average response time: {avg_time:.3f}s")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 GTO Service Connection Test")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Run tests
    health_ok = test_health_endpoint()

    if health_ok:
        analysis_ok = test_analysis_endpoint()
        perf_ok = test_performance()

        print("\n" + "=" * 60)
        if health_ok and analysis_ok and perf_ok:
            print("🎉 ALL TESTS PASSED - Service is working correctly!")
            print("\nNext steps:")
            print("1. Update your .env file:")
            print(f"   GTO_SOLVER_URL={BASE_URL}")
            print("2. Run: make run")
        else:
            print("⚠️  Some tests failed - check service configuration")
            sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("❌ Connection failed - cannot reach service")
        print("\nTroubleshooting:")
        print(f"1. Ping test: ping {WINDOWS_VM_IP}")
        print("2. Service status: Get-Service GTOService")
        print("3. Firewall: Check port 8080 is open")
        print("4. Logs: Get-Content C:\\gto-service\\gto_service.log")
        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()

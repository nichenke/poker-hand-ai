#!/usr/bin/env python3
"""
Test script to verify dotenv and OpenAI setup
"""
import os
from dotenv import load_dotenv

print("Testing environment setup...")

# Load .env file
load_dotenv()

# Check environment variables
api_key = os.getenv("OPENAI_API_KEY")
gto_url = os.getenv("GTO_SOLVER_URL")

print(f"API Key found: {'Yes' if api_key else 'No'}")
print(f"GTO URL: {gto_url}")

if api_key:
    print(f"API Key (masked): {'***' + api_key[-4:] if len(api_key) > 4 else '***'}")

# Test OpenAI client creation
if api_key and api_key != "sk-test-key-for-testing":
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client created successfully")
    except Exception as e:
        print(f"❌ OpenAI client error: {e}")
else:
    print("⚠️  Using test API key - OpenAI client not tested")

print("Test completed.")

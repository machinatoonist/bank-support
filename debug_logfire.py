#!/usr/bin/env python3
"""
Debug script to test Logfire configuration and token validity.
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_logfire_config():
    """Test Logfire configuration and token"""

    print("🔍 LOGFIRE DEBUG TEST")
    print("=====================")
    print()

    # Check token
    token = os.getenv("LOGFIRE_TOKEN") or os.getenv("LOGFIRE_API_KEY")
    if token:
        print(f"✅ Token found: {token[:10]}... (length: {len(token)})")
    else:
        print("❌ No token found in environment")
        return

    # Test Logfire import
    try:
        import logfire
        print("✅ Logfire imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import logfire: {e}")
        return

    # Test Logfire configuration
    try:
        print("🔧 Configuring Logfire...")

        # Try different configuration approaches
        configs_to_try = [
            {
                "name": "With project_name",
                "config": {
                    "service_name": "bank-support-agent",
                    "token": token,
                    "project_name": "bank-support"
                }
            },
            {
                "name": "Without project_name",
                "config": {
                    "service_name": "bank-support-agent",
                    "token": token
                }
            },
            {
                "name": "Minimal config",
                "config": {
                    "token": token
                }
            }
        ]

        for test_config in configs_to_try:
            print(f"\n🧪 Testing: {test_config['name']}")
            try:
                logfire.configure(**test_config['config'])
                print(f"   ✅ Configuration successful")

                # Test a simple log
                logfire.info("Test log message", extra={"test": True})
                print(f"   ✅ Test log sent")

                # Try instrumentation
                logfire.instrument_openai()
                print(f"   ✅ OpenAI instrumentation successful")

                break  # If we get here, this config worked

            except Exception as e:
                print(f"   ❌ Configuration failed: {e}")
                continue

    except Exception as e:
        print(f"❌ Logfire configuration error: {e}")
        return

    print()
    print("🎯 RECOMMENDATIONS:")
    print("==================")
    print("1. Check Modal logs for our debug output")
    print("2. If token is valid, try removing 'project_name' parameter")
    print("3. Check Logfire dashboard for any error messages")
    print("4. Verify the token has write permissions for bank-support project")
    print()
    print("📊 Logfire Dashboard: https://logfire-us.pydantic.dev/mattrosinski/bank-support")


if __name__ == "__main__":
    test_logfire_config()
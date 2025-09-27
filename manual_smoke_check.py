#!/usr/bin/env python3
"""
Smoke test script for bank support API.

Tests health endpoint and support endpoint with expected risk levels:
- Balance inquiry should have risk < 3
- Lost card should have risk > 7
"""

import json
import sys
import requests
from typing import Dict, Any

API_BASE = "http://localhost:8001"

def test_health() -> bool:
    """Test the health endpoint."""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: unexpected response {data}")
                return False
        else:
            print(f"❌ Health check failed: status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_support_endpoint(question: str, customer_name: str, expected_risk_condition: str, customer_id: int = 123) -> bool:
    """Test support endpoint with risk level validation."""
    try:
        payload = {
            "question": question,
            "customer_name": customer_name,
            "customer_id": customer_id
        }

        response = requests.post(
            f"{API_BASE}/support",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Support request failed: status {response.status_code}")
            print(f"Response: {response.text}")
            return False

        data = response.json()

        # Validate response structure
        required_fields = ["support_advice", "block_card", "risk"]
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing field '{field}' in response")
                return False

        risk = data["risk"]
        advice = data["support_advice"]
        block_card = data["block_card"]

        # Validate risk level
        if expected_risk_condition == "low" and risk < 3:
            print(f"✅ Low risk test passed: risk={risk} (expected < 3)")
            risk_ok = True
        elif expected_risk_condition == "high" and risk > 7:
            print(f"✅ High risk test passed: risk={risk} (expected > 7)")
            risk_ok = True
        else:
            print(f"❌ Risk level test failed: risk={risk} (expected {expected_risk_condition})")
            risk_ok = False

        # Print response details
        print(f"   Question: {question}")
        print(f"   Customer: {customer_name}")
        print(f"   Advice: {advice}")
        print(f"   Block card: {block_card}")
        print(f"   Risk: {risk}")
        print()

        return risk_ok

    except Exception as e:
        print(f"❌ Support request failed: {e}")
        return False

def main():
    """Run all smoke tests."""
    print("🧪 Running Bank Support API Smoke Tests")
    print("=" * 50)

    tests_passed = 0
    total_tests = 3

    # Test 1: Health check
    if test_health():
        tests_passed += 1

    print()

    # Test 2: Balance inquiry (should be low risk)
    print("Testing balance inquiry (expecting low risk < 3)...")
    if test_support_endpoint(
        question="What is my balance?",
        customer_name="Alice",
        expected_risk_condition="low"
    ):
        tests_passed += 1

    # Test 3: Lost card (should be high risk)
    print("Testing lost card report (expecting high risk > 7)...")
    if test_support_endpoint(
        question="I just lost my card!",
        customer_name="Bob",
        expected_risk_condition="high"
    ):
        tests_passed += 1

    # Summary
    print("=" * 50)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")

    if tests_passed == total_tests:
        print("🎉 All smoke tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
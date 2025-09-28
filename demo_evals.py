#!/usr/bin/env python3
"""
Quick Demo of Bank Support Agent Testing

This script demonstrates how to test your Modal-deployed bank support agent
with various scenarios and shows the evaluation capabilities.
"""

import asyncio
import httpx
from typing import Dict, Any


async def quick_test_scenarios():
    """Test a few key scenarios to demonstrate the agent's capabilities"""

    # Modal API URL
    api_url = "https://mattrosinski--bank-support-bank-support-api.modal.run"

    # Test scenarios
    scenarios = [
        {
            "name": "🚨 Critical: Lost Card",
            "question": "I lost my credit card",
            "customer": "John Doe",
            "expected": "Should block card, high risk"
        },
        {
            "name": "✅ Routine: Balance Check",
            "question": "What is my account balance?",
            "customer": "Jane Smith",
            "expected": "Should NOT block card, low risk"
        },
        {
            "name": "⚠️ Urgent: Unauthorized Charges",
            "question": "I see charges on my account that I didn't make",
            "customer": "Bob Wilson",
            "expected": "Should block card, high risk"
        },
        {
            "name": "🔶 Concerning: Suspicious Activity",
            "question": "There's some unusual activity on my account but I'm not sure",
            "customer": "Alice Brown",
            "expected": "May/may not block card, medium risk"
        }
    ]

    print("🧪 Bank Support Agent - Quick Evaluation Demo")
    print("=" * 60)
    print(f"Testing API: {api_url}")
    print()

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, scenario in enumerate(scenarios, 1):
            print(f"📋 Test {i}/{len(scenarios)}: {scenario['name']}")
            print(f"   Question: {scenario['question']}")
            print(f"   Customer: {scenario['customer']}")
            print(f"   Expected: {scenario['expected']}")
            print("-" * 50)

            try:
                # Call the API
                payload = {
                    "question": scenario['question'],
                    "customer_name": scenario['customer'],
                    "customer_id": 123,
                    "include_pending": True
                }

                response = await client.post(f"{api_url}/support", json=payload)
                response.raise_for_status()
                result = response.json()

                # Display results
                advice = result.get("support_advice", "N/A")
                block_card = result.get("block_card", False)
                risk = result.get("risk", 0)
                risk_category = result.get("risk_category", "unknown")
                risk_signals = result.get("risk_signals", [])

                print(f"   ✅ Block Card: {'YES' if block_card else 'NO'}")
                print(f"   ✅ Risk Level: {risk}/10 ({risk_category.upper()})")
                print(f"   ✅ Risk Signals: {', '.join(risk_signals) if risk_signals else 'None'}")
                print(f"   ✅ Advice: {advice[:80]}{'...' if len(advice) > 80 else ''}")

                # Quick assessment
                if scenario['name'].startswith("🚨") or scenario['name'].startswith("⚠️"):
                    if block_card and risk >= 7:
                        print("   ✅ CORRECT: High-risk scenario properly handled")
                    else:
                        print("   ⚠️  REVIEW: Expected higher risk response")
                elif scenario['name'].startswith("✅"):
                    if not block_card and risk <= 3:
                        print("   ✅ CORRECT: Routine scenario properly handled")
                    else:
                        print("   ⚠️  REVIEW: Expected lower risk response")

            except Exception as e:
                print(f"   ❌ Error: {e}")

            print()

            # Small delay between requests
            await asyncio.sleep(1)

    print("🎯 Demo Complete!")
    print("\nNext Steps:")
    print("   • Run interactive mode: python test_modal_chat.py")
    print("   • Run full evaluation: python bank_support_evals.py --modal")
    print("   • View Logfire traces: https://logfire-us.pydantic.dev/mattrosinski/bank-support")


if __name__ == "__main__":
    asyncio.run(quick_test_scenarios())
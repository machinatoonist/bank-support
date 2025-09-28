#!/usr/bin/env python3
"""
Simple Modal API Testing Tool

Quick interactive testing tool for the Modal-deployed bank support agent.
Perfect for manual testing and exploring agent responses.

Usage:
    python test_modal_chat.py
    python test_modal_chat.py --url https://your-custom-modal-url.modal.run
"""

import httpx
import json
import argparse
import asyncio
from typing import Dict, Any


class ModalAPITester:
    """Simple tester for Modal-deployed bank support API"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def test_health(self) -> Dict[str, Any]:
        """Test the health endpoint"""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    async def test_support(self, question: str, customer_name: str = "Test User", customer_id: int = 123) -> Dict[str, Any]:
        """Test the support endpoint"""
        payload = {
            "question": question,
            "customer_name": customer_name,
            "customer_id": customer_id,
            "include_pending": True
        }

        response = await self.client.post(
            f"{self.base_url}/support",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    async def get_api_docs_url(self) -> str:
        """Get the API documentation URL"""
        return f"{self.base_url}/docs"


def format_response(response: Dict[str, Any]) -> str:
    """Format the agent response for display"""
    advice = response.get("support_advice", "N/A")
    block_card = response.get("block_card", False)
    risk = response.get("risk", 0)
    risk_category = response.get("risk_category", "unknown")
    risk_explanation = response.get("risk_explanation", "N/A")
    risk_signals = response.get("risk_signals", [])

    # Color codes for terminal output
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

    # Risk level styling
    if risk >= 8:
        risk_color = RED
        risk_emoji = "🚨"
    elif risk >= 5:
        risk_color = YELLOW
        risk_emoji = "⚠️"
    elif risk >= 3:
        risk_color = YELLOW
        risk_emoji = "🔶"
    else:
        risk_color = GREEN
        risk_emoji = "✅"

    block_emoji = "🔒" if block_card else "🔓"
    block_color = RED if block_card else GREEN

    output = f"""
{BOLD}🤖 Bank Support Agent Response{END}
{'=' * 50}

{BLUE}💬 Advice:{END}
{advice}

{block_color}{block_emoji} Block Card: {BOLD}{'YES' if block_card else 'NO'}{END}

{risk_color}{risk_emoji} Risk Level: {BOLD}{risk}/10{END} ({risk_category.upper()})

{BLUE}📝 Risk Explanation:{END}
{risk_explanation}

{BLUE}🔍 Risk Signals:{END}
{', '.join(risk_signals) if risk_signals else 'None detected'}
"""
    return output


async def run_predefined_tests(tester: ModalAPITester):
    """Run a set of predefined test scenarios"""
    test_cases = [
        {
            "name": "Lost Card (Critical)",
            "question": "I lost my credit card",
            "customer": "John Doe"
        },
        {
            "name": "Balance Inquiry (Routine)",
            "question": "What is my account balance?",
            "customer": "Jane Smith"
        },
        {
            "name": "Unauthorized Charges (Urgent)",
            "question": "I see charges I didn't make",
            "customer": "Bob Wilson"
        },
        {
            "name": "General Question (Routine)",
            "question": "How do I update my address?",
            "customer": "Alice Brown"
        }
    ]

    print(f"\n🧪 Running Predefined Test Cases")
    print("=" * 60)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/4: {test_case['name']}")
        print(f"Question: {test_case['question']}")
        print(f"Customer: {test_case['customer']}")
        print("-" * 40)

        try:
            response = await tester.test_support(
                question=test_case['question'],
                customer_name=test_case['customer']
            )
            print(format_response(response))
        except Exception as e:
            print(f"❌ Error: {e}")

        # Pause between tests
        if i < len(test_cases):
            print("\nPress Enter to continue to next test...")
            input()


async def interactive_mode(tester: ModalAPITester):
    """Interactive testing mode"""
    print(f"\n💬 Interactive Testing Mode")
    print("=" * 60)
    print("Commands:")
    print("  - Type any question to test the agent")
    print("  - 'health' - Check API health")
    print("  - 'docs' - Show API documentation URL")
    print("  - 'tests' - Run predefined test cases")
    print("  - 'quit' - Exit")
    print()

    while True:
        try:
            user_input = input("\n🎯 Enter command or question: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            elif user_input.lower() == 'health':
                try:
                    health = await tester.test_health()
                    print(f"✅ API Health: {json.dumps(health, indent=2)}")
                except Exception as e:
                    print(f"❌ Health check failed: {e}")

            elif user_input.lower() == 'docs':
                docs_url = await tester.get_api_docs_url()
                print(f"📚 API Documentation: {docs_url}")

            elif user_input.lower() == 'tests':
                await run_predefined_tests(tester)

            elif user_input:
                # Get customer name
                customer_name = input("Customer name (default: Test User): ").strip()
                if not customer_name:
                    customer_name = "Test User"

                print("\n🔄 Calling agent...")
                try:
                    response = await tester.test_support(
                        question=user_input,
                        customer_name=customer_name
                    )
                    print(format_response(response))
                except Exception as e:
                    print(f"❌ Error: {e}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Modal API Testing Tool")
    parser.add_argument(
        "--url",
        type=str,
        default="https://mattrosinski--bank-support-bank-support-api.modal.run",
        help="Modal API URL"
    )
    parser.add_argument(
        "--test-health",
        action="store_true",
        help="Just test health endpoint and exit"
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run predefined tests and exit"
    )

    args = parser.parse_args()

    print(f"🚀 Modal Bank Support API Tester")
    print(f"   URL: {args.url}")
    print(f"   Mode: {'Health Check' if args.test_health else 'Predefined Tests' if args.run_tests else 'Interactive'}")

    async with ModalAPITester(args.url) as tester:
        try:
            # Test health first
            print("\n🔍 Testing API health...")
            health = await tester.test_health()
            print(f"✅ API is healthy: {health}")

            if args.test_health:
                return

            if args.run_tests:
                await run_predefined_tests(tester)
            else:
                await interactive_mode(tester)

        except Exception as e:
            print(f"❌ Failed to connect to API: {e}")
            print("   Make sure the Modal deployment is running")
            return


if __name__ == "__main__":
    asyncio.run(main())
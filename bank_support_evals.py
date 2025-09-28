#!/usr/bin/env python3
"""
Bank Support Agent Evaluation Framework

This script provides comprehensive evaluation capabilities for the bank support AI agent
using Pydantic AI Evals. It can test both local and Modal-deployed versions.

Usage:
    # Test local version
    python bank_support_evals.py --local

    # Test Modal deployment
    python bank_support_evals.py --modal

    # Interactive testing mode
    python bank_support_evals.py --interactive

    # Run all evaluations with detailed report
    python bank_support_evals.py --full-report
"""

import asyncio
import json
import httpx
import argparse
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field, conint

# Pydantic Evals imports
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import IsInstance, LLMJudge

# Local imports (for local testing)
try:
    from app.main import support_agent, SupportDependencies, DatabaseConn, SupportOutput, Query
    LOCAL_AVAILABLE = True
except ImportError:
    LOCAL_AVAILABLE = False


class BankSupportQuery(BaseModel):
    """Query model for bank support agent"""
    question: str
    customer_name: str
    customer_id: int = 123
    include_pending: bool = True


class BankSupportResponse(BaseModel):
    """Expected response model"""
    support_advice: str
    block_card: bool
    risk: int
    risk_explanation: str
    risk_category: str
    risk_signals: List[str]


@dataclass
class TestScenario:
    """A test scenario for the bank support agent"""
    name: str
    question: str
    customer_name: str
    expected_block_card: bool
    expected_risk_range: tuple[int, int]  # (min, max)
    expected_category: str
    expected_signals: List[str]
    customer_id: int = 123


# Comprehensive test scenarios
TEST_SCENARIOS = [
    # Critical scenarios (should block card)
    TestScenario(
        name="lost_card",
        question="I lost my credit card",
        customer_name="John Doe",
        expected_block_card=True,
        expected_risk_range=(8, 10),
        expected_category="critical",
        expected_signals=["lost"]
    ),
    TestScenario(
        name="stolen_card",
        question="My card was stolen from my wallet",
        customer_name="Jane Smith",
        expected_block_card=True,
        expected_risk_range=(9, 10),
        expected_category="critical",
        expected_signals=["stolen"]
    ),
    TestScenario(
        name="unauthorized_transactions",
        question="I see charges on my account that I didn't make",
        customer_name="Bob Wilson",
        expected_block_card=True,
        expected_risk_range=(7, 9),
        expected_category="urgent",
        expected_signals=["unauthorized", "charges"]
    ),
    TestScenario(
        name="fraud_suspicion",
        question="I think someone is using my card fraudulently",
        customer_name="Alice Brown",
        expected_block_card=True,
        expected_risk_range=(8, 10),
        expected_category="critical",
        expected_signals=["fraud", "fraudulently"]
    ),

    # Routine scenarios (should NOT block card)
    TestScenario(
        name="balance_inquiry",
        question="What is my current account balance?",
        customer_name="Mary Johnson",
        expected_block_card=False,
        expected_risk_range=(0, 2),
        expected_category="routine",
        expected_signals=[]
    ),
    TestScenario(
        name="transaction_history",
        question="Can you show me my recent transactions?",
        customer_name="David Lee",
        expected_block_card=False,
        expected_risk_range=(0, 2),
        expected_category="routine",
        expected_signals=[]
    ),
    TestScenario(
        name="account_info",
        question="I need to update my contact information",
        customer_name="Sarah Davis",
        expected_block_card=False,
        expected_risk_range=(0, 3),
        expected_category="routine",
        expected_signals=[]
    ),

    # Concerning scenarios (should NOT block card but higher risk)
    TestScenario(
        name="forgotten_transaction",
        question="I don't remember making this purchase, but it might be mine",
        customer_name="Mike Chen",
        expected_block_card=False,
        expected_risk_range=(3, 6),
        expected_category="concerning",
        expected_signals=["don't remember"]
    ),
    TestScenario(
        name="suspicious_activity",
        question="I noticed some unusual activity on my account but I'm not sure",
        customer_name="Lisa Rodriguez",
        expected_block_card=False,
        expected_risk_range=(4, 7),
        expected_category="concerning",
        expected_signals=["unusual", "suspicious"]
    )
]


class BankSupportEvaluator:
    """Evaluator for bank support agent responses"""

    def __init__(self, use_modal: bool = False, modal_url: str = None):
        self.use_modal = use_modal
        self.modal_url = modal_url or "https://mattrosinski--bank-support-bank-support-api.modal.run"

    async def call_agent(self, query: BankSupportQuery) -> BankSupportResponse:
        """Call the agent (local or modal) and return response"""
        if self.use_modal:
            return await self._call_modal_agent(query)
        else:
            return await self._call_local_agent(query)

    async def _call_modal_agent(self, query: BankSupportQuery) -> BankSupportResponse:
        """Call the Modal-deployed agent"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.modal_url}/support",
                json=query.model_dump()
            )
            response.raise_for_status()
            return BankSupportResponse(**response.json())

    async def _call_local_agent(self, query: BankSupportQuery) -> BankSupportResponse:
        """Call the local agent"""
        if not LOCAL_AVAILABLE:
            raise RuntimeError("Local agent not available. Run with --modal instead.")

        deps = SupportDependencies(
            customer_id=query.customer_id,
            customer_name=query.customer_name,
            db=DatabaseConn()
        )
        result = await support_agent.run_async(query.question, deps=deps)
        return BankSupportResponse(**result.output.model_dump())


def create_evaluation_cases() -> List[Case]:
    """Create evaluation cases from test scenarios"""
    cases = []

    for scenario in TEST_SCENARIOS:
        # Create the input query
        query = BankSupportQuery(
            question=scenario.question,
            customer_name=scenario.customer_name,
            customer_id=scenario.customer_id
        )

        # Define expected output for comparison
        expected_output = {
            "block_card": scenario.expected_block_card,
            "risk_range": scenario.expected_risk_range,
            "risk_category": scenario.expected_category,
            "expected_signals": scenario.expected_signals
        }

        # Create evaluators
        evaluators = [
            # Check response type
            IsInstance(type_name="BankSupportResponse"),

            # LLM Judge for card blocking decision
            LLMJudge(
                rubric=f"""
                Evaluate if the card blocking decision is appropriate:
                - Question: "{scenario.question}"
                - Expected block_card: {scenario.expected_block_card}
                - The response should block the card if there are security concerns like lost/stolen cards or fraud
                - Score 1.0 if the blocking decision is correct, 0.0 if incorrect
                """,
                name="card_blocking_decision"
            ),

            # LLM Judge for risk assessment
            LLMJudge(
                rubric=f"""
                Evaluate if the risk score is appropriate:
                - Question: "{scenario.question}"
                - Expected risk range: {scenario.expected_risk_range[0]}-{scenario.expected_risk_range[1]}
                - Expected category: {scenario.expected_category}
                - Score 1.0 if risk is in expected range and category matches, 0.5 if close, 0.0 if way off
                """,
                name="risk_assessment"
            ),

            # LLM Judge for overall response quality
            LLMJudge(
                rubric=f"""
                Evaluate the overall quality of the bank support response:
                - Is the advice helpful and appropriate?
                - Is the tone professional and reassuring?
                - Does it address the customer's concern?
                - Is the risk explanation clear and logical?
                Score 1.0 for excellent, 0.7 for good, 0.4 for acceptable, 0.0 for poor
                """,
                name="response_quality"
            )
        ]

        case = Case(
            name=scenario.name,
            inputs=query,
            expected_output=expected_output,
            evaluators=evaluators,
            metadata={
                "scenario_type": scenario.expected_category,
                "customer_name": scenario.customer_name,
                "expected_block_card": scenario.expected_block_card,
                "expected_risk_range": scenario.expected_risk_range
            }
        )
        cases.append(case)

    return cases


async def run_evaluation(use_modal: bool = False, modal_url: str = None) -> None:
    """Run the complete evaluation suite"""
    print(f"🔍 Running Bank Support Agent Evaluation")
    print(f"   Mode: {'Modal Deployment' if use_modal else 'Local Agent'}")
    print(f"   URL: {modal_url if use_modal else 'Local'}")
    print(f"   Test Cases: {len(TEST_SCENARIOS)}")
    print("=" * 60)

    # Create evaluator
    evaluator = BankSupportEvaluator(use_modal=use_modal, modal_url=modal_url)

    # Create dataset
    cases = create_evaluation_cases()
    dataset = Dataset(cases=cases)

    # Define the task function
    async def bank_support_task(query: BankSupportQuery) -> BankSupportResponse:
        return await evaluator.call_agent(query)

    # Run evaluation
    print("🚀 Starting evaluation...")
    report = await dataset.evaluate_async(bank_support_task)

    # Print results
    print("\n📊 Evaluation Results:")
    print("=" * 60)
    report.print()

    # Print detailed analysis
    print("\n🔍 Detailed Analysis:")
    print("=" * 60)

    for case_result in report.case_results:
        case_name = case_result.case.name
        metadata = case_result.case.metadata

        print(f"\n📋 {case_name.upper()}")
        print(f"   Question: {case_result.case.inputs.question}")
        print(f"   Customer: {case_result.case.inputs.customer_name}")
        print(f"   Expected Block Card: {metadata['expected_block_card']}")
        print(f"   Expected Risk Range: {metadata['expected_risk_range']}")

        if case_result.output:
            output = case_result.output
            print(f"   ✅ Actual Block Card: {output.block_card}")
            print(f"   ✅ Actual Risk: {output.risk} ({output.risk_category})")
            print(f"   ✅ Risk Signals: {output.risk_signals}")
            print(f"   ✅ Advice: {output.support_advice[:100]}...")

            # Check if results match expectations
            block_correct = output.block_card == metadata['expected_block_card']
            risk_in_range = metadata['expected_risk_range'][0] <= output.risk <= metadata['expected_risk_range'][1]

            print(f"   {'✅' if block_correct else '❌'} Block Decision: {'Correct' if block_correct else 'Incorrect'}")
            print(f"   {'✅' if risk_in_range else '❌'} Risk Score: {'In Range' if risk_in_range else 'Out of Range'}")
        else:
            print(f"   ❌ Failed to get response")

        # Print evaluator scores
        if case_result.evaluator_results:
            print(f"   📈 Evaluator Scores:")
            for eval_result in case_result.evaluator_results:
                score = eval_result.score if eval_result.score is not None else "N/A"
                print(f"      - {eval_result.evaluator.name}: {score}")


async def interactive_testing(use_modal: bool = False, modal_url: str = None) -> None:
    """Interactive testing mode for manual queries"""
    print("🎯 Interactive Bank Support Agent Testing")
    print("   Type 'quit' to exit, 'help' for commands")
    print(f"   Mode: {'Modal Deployment' if use_modal else 'Local Agent'}")
    print("=" * 60)

    evaluator = BankSupportEvaluator(use_modal=use_modal, modal_url=modal_url)

    while True:
        try:
            print("\n💬 Enter your query:")
            question = input("Question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif question.lower() == 'help':
                print("""
📚 Available commands:
   - Type any question to test the agent
   - 'scenarios' - Show predefined test scenarios
   - 'modal' - Switch to Modal mode
   - 'local' - Switch to local mode
   - 'quit' - Exit
                """)
                continue
            elif question.lower() == 'scenarios':
                print("\n📋 Predefined Test Scenarios:")
                for i, scenario in enumerate(TEST_SCENARIOS, 1):
                    print(f"   {i}. {scenario.name}: {scenario.question}")
                continue
            elif question.lower() == 'modal':
                evaluator.use_modal = True
                print("🔄 Switched to Modal deployment mode")
                continue
            elif question.lower() == 'local':
                evaluator.use_modal = False
                print("🔄 Switched to local agent mode")
                continue

            if not question:
                continue

            # Get customer name
            customer_name = input("Customer name (default: Test User): ").strip() or "Test User"
            customer_id = 123

            # Create query
            query = BankSupportQuery(
                question=question,
                customer_name=customer_name,
                customer_id=customer_id
            )

            print("\n🤖 Agent Response:")
            print("-" * 40)

            try:
                # Call agent
                response = await evaluator.call_agent(query)

                # Display response
                print(f"💬 Advice: {response.support_advice}")
                print(f"🔒 Block Card: {'YES' if response.block_card else 'NO'}")
                print(f"⚠️  Risk Level: {response.risk}/10 ({response.risk_category})")
                print(f"🔍 Risk Signals: {', '.join(response.risk_signals) if response.risk_signals else 'None'}")
                print(f"📝 Risk Explanation: {response.risk_explanation}")

                # Color-coded risk assessment
                if response.risk >= 8:
                    print("🚨 HIGH RISK - Immediate action required")
                elif response.risk >= 5:
                    print("⚠️  MEDIUM RISK - Monitor closely")
                elif response.risk >= 3:
                    print("🔶 LOW-MEDIUM RISK - Some concern")
                else:
                    print("✅ LOW RISK - Routine inquiry")

            except Exception as e:
                print(f"❌ Error calling agent: {e}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Bank Support Agent Evaluation")
    parser.add_argument("--modal", action="store_true", help="Test Modal deployment")
    parser.add_argument("--local", action="store_true", help="Test local agent")
    parser.add_argument("--interactive", action="store_true", help="Interactive testing mode")
    parser.add_argument("--full-report", action="store_true", help="Run comprehensive evaluation")
    parser.add_argument("--modal-url", type=str, help="Custom Modal URL")

    args = parser.parse_args()

    # Default to Modal if nothing specified
    use_modal = args.modal or not args.local
    modal_url = args.modal_url

    if args.interactive:
        asyncio.run(interactive_testing(use_modal=use_modal, modal_url=modal_url))
    else:
        asyncio.run(run_evaluation(use_modal=use_modal, modal_url=modal_url))


if __name__ == "__main__":
    main()
# How to Build a Risk-Ranking Bank Support Agent (Without Compromising on Accuracy)

In 1854, John Snow faced a deadly cholera outbreak in London's Soho district. While the medical establishment blamed "bad air," Snow took a different approach—he mapped every case, analyzed the data, and identified the contaminated water pump on Broad Street as the source. His methodical approach to **ranking** the risk of each water source based on evidence saved countless lives and revolutionized public health.

Today, we face a similar challenge in financial services. Customer support agents handle thousands of interactions daily, from routine balance inquiries to urgent fraud reports. The difference between correctly identifying a critical security threat versus a routine question can mean the difference between preventing financial loss and allowing it to happen.

Traditional rule-based systems fail because they're either too rigid (flagging legitimate transactions) or too permissive (missing actual threats). What if we could combine the pattern recognition power of Large Language Models with the precision and reliability that banking demands?

The answer lies in building an AI agent that doesn't just classify risk—it **ranks** it with mathematical precision while providing clear reasoning for every decision. By using Pydantic's structured outputs and comprehensive observability, we can create a system that's both intelligent and auditable.

Just as Snow's data-driven approach transformed how we think about disease prevention, this methodology transforms how we approach financial risk assessment. Let's explore how to build a bank support agent that ranks risk with surgical precision.

**Here's what we'll cover:**
1. **Structured Risk Assessment** - Using Pydantic to constrain LLM outputs and ensure reliable **ranking** scales
2. **Real-Time Risk Ranking** - Implementing the agent to assess customer queries with mathematical precision
3. **Observability & Improvement** - Building monitoring systems to validate and refine your **ranking** accuracy

## 1. Structured Risk Assessment with Pydantic

The foundation of reliable risk ranking lies in constraining your LLM outputs. Here's how we define a structured risk assessment:

```python
from pydantic import BaseModel, Field, conint
from pydantic_ai import Agent

class SupportOutput(BaseModel):
    support_advice: str = Field(description="Advice returned to the customer")
    block_card: bool = Field(description="Whether to block their card")
    risk: conint(ge=0, le=10) = Field(description="Risk level 0–10 (inclusive)")
    risk_explanation: str = Field(description="1 sentence explanation of risk level")
    risk_category: str = Field(description="Risk category: routine, concerning, urgent, or critical")
    risk_signals: list[str] = Field(default_factory=list, description="Signals/keywords found")

# Configure the agent with calibrated instructions
support_agent = Agent(
    "openai:gpt-4o",
    output_type=SupportOutput,
    instructions=(
        "You are a support agent for a bank. "
        "Return concise, actionable advice, and a calibrated risk score from 0–10: "
        "0–2 routine inquiries; 3–5 concerning issues; 6–8 urgent security matters; "
        "9–10 critical threats like fraud or theft. "
        "If loss/theft or suspicious activity is indicated, set block_card=True."
    ),
)
```

**Key insight**: The `conint(ge=0, le=10)` constraint ensures your risk scores are always within bounds, while the structured fields force the model to provide reasoning alongside its decisions.

## 2. Real-Time Risk Ranking in Production

Here's how the agent performs risk ranking with actual customer queries:

```python
# Test scenarios with different risk levels
test_cases = [
    "What is my account balance?",  # Expected: Low risk (0-2)
    "I see charges I didn't make",  # Expected: High risk (7-9)
    "I lost my credit card yesterday"  # Expected: Critical risk (9-10)
]

for query in test_cases:
    result = support_agent.run_sync(query)

    print(f"Query: {query}")
    print(f"Risk: {result.output.risk}/10 ({result.output.risk_category})")
    print(f"Block Card: {result.output.block_card}")
    print(f"Signals: {result.output.risk_signals}")
    print(f"Reasoning: {result.output.risk_explanation}")
    print("-" * 50)
```

**Expected output:**
```
Query: I lost my credit card yesterday
Risk: 9/10 (critical)
Block Card: True
Signals: ['lost']
Reasoning: Card loss poses critical risk of unauthorized transactions.
```

The beauty of this approach is that you get both the decision (block_card=True) and the mathematical reasoning (risk=9) with explicit signals that triggered the assessment.

## 3. Observability and Continuous Improvement

To ensure your risk ranking remains accurate, implement comprehensive observability:

```python
import logfire
from fastapi import FastAPI

# Configure observability
logfire.configure(service_name="bank-support-agent")
logfire.instrument_pydantic_ai()
logfire.instrument_openai()

app = FastAPI()

@app.post("/support", response_model=SupportOutput)
def support_endpoint(query: CustomerQuery):
    # The agent call is automatically traced
    result = support_agent.run_sync(query.question)

    # Log key metrics for monitoring
    logfire.info(
        "Risk assessment completed",
        risk_score=result.output.risk,
        risk_category=result.output.risk_category,
        blocked_card=result.output.block_card,
        signals=result.output.risk_signals
    )

    return result.output
```

**Monitoring dashboard queries:**
- Average risk scores by time period
- Distribution of risk categories
- Card blocking frequency and false positives
- Response time and token usage trends

**Decision framework**: Set up alerts when risk score distributions change significantly—this indicates either new threat patterns or model drift that requires attention.

---

## The Power of Data-Driven Risk Ranking

Just as John Snow's methodical **ranking** of water sources by contamination risk revolutionized public health, this structured approach to risk assessment transforms financial security. By combining LLM intelligence with Pydantic's mathematical constraints and comprehensive observability, we've created a system that doesn't just detect threats—it **ranks** them with precision.

The three pillars we've explored work together:
- **Structured outputs** ensure reliable **ranking** scales (0-10) with clear reasoning
- **Real-time assessment** provides instant, actionable risk **rankings** for every customer interaction
- **Continuous monitoring** validates that your **ranking** system stays accurate as threats evolve

**Ready to build your own risk-ranking agent?** The complete implementation with Modal deployment, evaluation framework, and production observability is available on GitHub. The key is starting with structured outputs, validating with real scenarios, and monitoring everything.

*What's your experience with LLM reliability in production? Share your insights in the comments below.*

#DataScience #MachineLearning #Pydantic #AI #FinTech #RiskManagement #BetterDecisions
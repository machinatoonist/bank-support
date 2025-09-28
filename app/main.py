# app/main.py
from dataclasses import dataclass
from typing import Optional
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, conint
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv
import logfire

# Load environment variables from .env file
load_dotenv()

# ---------- 1) Logfire ----------
# Configure Logfire for both development and production environments
logfire_token = os.getenv("LOGFIRE_TOKEN") or os.getenv("LOGFIRE_API_KEY")
logfire_enabled = False

try:
    if logfire_token:
        # Production mode: Use token for authentication
        logfire.configure(service_name="bank-support", token=logfire_token)
        logfire_enabled = True
    else:
        # Development mode: Use stored credentials from `logfire auth`
        logfire.configure(service_name="bank-support")
        logfire_enabled = True
    
    if logfire_enabled:
        logfire.instrument_pydantic_ai()
        logfire.instrument_openai()
except Exception as e:
    print(f"Warning: Logfire configuration failed: {e}")
    print("Continuing without Logfire instrumentation...")
    logfire_enabled = False

# ---------- 2) Domain stubs ----------
class DatabaseConn:
    """Fake DB for demo. Swap with real data access later."""

    @classmethod
    async def customer_name(cls, *, id: int, name: str) -> str:
        # Return the provided name for any customer ID
        return name

    @classmethod
    async def customer_balance(cls, *, id: int, include_pending: bool) -> float:
        # All customers have the same balance
        if include_pending:
            return 123.45
        else:
            return 100.00

@dataclass
class SupportDependencies:
    customer_id: int
    customer_name: str
    db: DatabaseConn

# ---------- 3) Output schema with validation ----------
class SupportOutput(BaseModel):
    support_advice: str = Field(description="Advice returned to the customer")
    block_card: bool = Field(description="Whether to block their card")
    risk: conint(ge=0, le=10) = Field(description="Risk level 0–10 (inclusive)")
    risk_explanation: str = Field(description="1 sentence explanation of why this risk level was assigned")
    risk_category: str = Field(description="Risk category: routine, concerning, urgent, or critical")
    risk_signals: list[str] = Field(default_factory=list, description="Signals/keywords found")

# ---------- 4) Agent with calibrated instructions ----------
# Check if OpenAI API key is available and configure agent
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
    # do not change this unless explicitly requested by the user
    support_agent = Agent(
        "openai:gpt-5",
        deps_type=SupportDependencies,
        output_type=SupportOutput,
        instructions=(
            "You are a support agent for a bank. "
            "Return concise, actionable advice, and a calibrated risk score from 0–10: "
            "0–2 routine inquiries; 3–5 concerning issues; 6–8 urgent security matters; "
            "9–10 critical threats like fraud or theft. "
            "If loss/theft or suspicious activity is indicated, set block_card=True. "
            "Provide a clear explanation of why you assigned the risk level. "
            "Risk categories: 'routine' (0-2), 'concerning' (3-5), "
            "'urgent' (6-8), 'critical' (9-10). "
            "Identify specific risk signals/keywords from the query that "
            "contributed to your risk assessment (e.g., 'lost', 'stolen', "
            "'unauthorized', 'fraud', 'suspicious'). "
            "Use the customer's name if known."
        ),
    )

    # Provide the customer's name as additional instruction at runtime
    @support_agent.instructions
    async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
        customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id, name=ctx.deps.customer_name)
        return f"The customer's name is {customer_name!r}"

    # ---------- 5) Tool: balance lookup ----------
    @support_agent.tool
    async def customer_balance(
        ctx: RunContext[SupportDependencies], include_pending: bool
    ) -> str:
        """Returns the customer's current account balance as a formatted string."""
        balance = await ctx.deps.db.customer_balance(
            id=ctx.deps.customer_id,
            include_pending=include_pending,
        )
        return f"${balance:.2f}"

    use_mock_agent = False
else:
    print("Warning: No OpenAI API key found. Using mock agent for demonstration...")
    support_agent = None
    use_mock_agent = True

# Mock agent function for when API key is not available
def mock_support_response(question: str, customer_name: str) -> SupportOutput:
    """Mock support agent that provides demo responses."""
    question_lower = question.lower()
    
    # Determine risk level based on keywords
    risk_signals = []
    risk = 1
    block_card = False
    
    if any(word in question_lower for word in ["lost", "stolen", "missing"]):
        risk = 9
        block_card = True
        risk_signals.extend(["lost", "stolen"])
        advice = f"Hi {customer_name}, I understand you've reported a lost or stolen card. I've immediately blocked your card for security. We'll expedite a replacement card to you within 2-3 business days."
        risk_category = "critical"
        risk_explanation = "Card reported as lost or stolen requires immediate blocking."
    elif any(word in question_lower for word in ["fraud", "suspicious", "unauthorized"]):
        risk = 8
        block_card = True
        risk_signals.extend(["fraud", "suspicious"])
        advice = f"Hi {customer_name}, I take fraud concerns very seriously. I've blocked your card as a precaution and our fraud team will investigate. You'll receive a call within 24 hours."
        risk_category = "urgent"
        risk_explanation = "Potential fraud requires immediate card blocking and investigation."
    elif any(word in question_lower for word in ["balance", "account"]):
        risk = 1
        advice = f"Hi {customer_name}, I can help you with your account balance. Your current balance is $123.45 (including pending transactions)."
        risk_category = "routine"
        risk_explanation = "Standard account inquiry poses no security risk."
        risk_signals.append("balance inquiry")
    else:
        risk = 2
        advice = f"Hi {customer_name}, thank you for contacting us. I'm here to help with your banking needs. Could you please provide more details about your inquiry?"
        risk_category = "routine"
        risk_explanation = "General inquiry with no specific risk indicators."
    
    return SupportOutput(
        support_advice=advice,
        block_card=block_card,
        risk=risk,
        risk_explanation=risk_explanation,
        risk_category=risk_category,
        risk_signals=risk_signals
    )

# ---------- 6) FastAPI app and endpoint ----------
app = FastAPI(title="bank-support")

# Add CORS middleware to allow frontend requests
# Get the Replit domain for CORS
replit_domain = os.getenv("REPLIT_DEV_DOMAIN")
allowed_origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:5000",  # Local frontend on port 5000
]

if replit_domain:
    allowed_origins.extend([
        f"https://{replit_domain}",
        f"http://{replit_domain}",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument FastAPI after app creation only if Logfire is enabled
if logfire_enabled:
    logfire.instrument_fastapi(app)

class Query(BaseModel):
    question: str
    customer_name: str
    customer_id: int = 123
    include_pending: bool = True

@app.post("/support", response_model=SupportOutput)
async def support(q: Query) -> SupportOutput:
    if use_mock_agent or not support_agent:
        # Use mock agent for demonstration
        return mock_support_response(q.question, q.customer_name)
    else:
        # Use real AI agent
        deps = SupportDependencies(customer_id=q.customer_id, customer_name=q.customer_name, db=DatabaseConn())
        # The agent can decide to call the tool (customer_balance) if needed
        result = await support_agent.run(q.question, deps=deps)
        return result.data

@app.get("/health")
def health():
    return {"status": "ok", "ai_enabled": not use_mock_agent}
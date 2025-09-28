# app/main.py - Simple bank support demo without external API dependencies
from dataclasses import dataclass
from typing import Optional
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, conint
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---------- 1) Domain stubs ----------
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

# ---------- 2) Output schema with validation ----------
class SupportOutput(BaseModel):
    support_advice: str = Field(description="Advice returned to the customer")
    block_card: bool = Field(description="Whether to block their card")
    risk: conint(ge=0, le=10) = Field(description="Risk level 0–10 (inclusive)")
    risk_explanation: str = Field(description="1 sentence explanation of why this risk level was assigned")
    risk_category: str = Field(description="Risk category: routine, concerning, urgent, or critical")
    risk_signals: list[str] = Field(default_factory=list, description="Signals/keywords found")

# ---------- 3) Mock support agent ----------
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

# ---------- 4) FastAPI app and endpoint ----------
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

class Query(BaseModel):
    question: str
    customer_name: str
    customer_id: int = 123
    include_pending: bool = True

@app.post("/support", response_model=SupportOutput)
def support(q: Query) -> SupportOutput:
    # Use mock agent for demonstration
    return mock_support_response(q.question, q.customer_name)

@app.get("/health")
def health():
    return {"status": "ok"}
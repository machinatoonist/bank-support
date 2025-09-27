"""Small but complete example of using Pydantic AI to build a support agent for a bank.

Run with:

    uv run uvicorn bank_support_example:app --reload --port 8001
"""

from dataclasses import dataclass

from pydantic import BaseModel, Field
from fastapi import FastAPI
from dotenv import load_dotenv

from pydantic_ai import Agent, RunContext

# Load environment variables
load_dotenv()


class DatabaseConn:
    """This is a fake database for example purposes.

    In reality, you'd be connecting to an external database
    (e.g. PostgreSQL) to get information about customers.
    """

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


class SupportOutput(BaseModel):
    support_advice: str = Field(description="Advice returned to the customer")
    block_card: bool = Field(description="Whether to block their card or not")
    risk: int = Field(ge=0, le=10, description="Risk level of query (0-10)")
    risk_explanation: str = Field(description="1 sentence explanation of why this risk level was assigned")
    risk_category: str = Field(description="Risk category: routine, concerning, urgent, or critical")
    risk_signals: list[str] = Field(default_factory=list, description="Signals/keywords found")


support_agent = Agent(
    'openai:gpt-4o',
    deps_type=SupportDependencies,
    output_type=SupportOutput,
    instructions=(
        'You are a support agent in our bank, give the '
        'customer support and judge the risk level of their query. '
        'Risk level must be between 0-10: 0-2 for routine inquiries, '
        '3-5 for concerning issues, 6-8 for urgent security matters, '
        '9-10 for critical threats like fraud or theft. '
        'Provide a clear explanation of why you assigned the risk level. '
        'Risk categories: "routine" (0-2), "concerning" (3-5), '
        '"urgent" (6-8), "critical" (9-10). '
        'Identify specific risk signals/keywords from the query that '
        'contributed to your risk assessment (e.g., "lost", "stolen", '
        '"unauthorized", "fraud", "suspicious"). '
        "Reply using the customer's name."
    ),
)


@support_agent.instructions
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id, name=ctx.deps.customer_name)
    return f"The customer's name is {customer_name!r}"


@support_agent.tool
async def customer_balance(
    ctx: RunContext[SupportDependencies], include_pending: bool
) -> str:
    """Returns the customer's current account balance."""
    balance = await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id,
        include_pending=include_pending,
    )
    return f'${balance:.2f}'


# FastAPI app
app = FastAPI(title="Bank Support API")

class Query(BaseModel):
    question: str
    customer_name: str
    customer_id: int = 123

@app.post("/support", response_model=SupportOutput)
def support(q: Query) -> SupportOutput:
    deps = SupportDependencies(customer_id=q.customer_id, customer_name=q.customer_name, db=DatabaseConn())
    result = support_agent.run_sync(q.question, deps=deps)
    return result.output

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    deps = SupportDependencies(customer_id=123, customer_name="John", db=DatabaseConn())
    result = support_agent.run_sync('What is my balance?', deps=deps)
    print(result.output)
    """
    support_advice='Hello John, your current account balance, including pending transactions, is $123.45.' block_card=False risk=1
    """

    result = support_agent.run_sync('I just lost my card!', deps=deps)
    print(result.output)
    """
    support_advice="I'm sorry to hear that, John. We are temporarily blocking your card to prevent unauthorized transactions." block_card=True risk=8
    """
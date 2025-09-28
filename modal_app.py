"""
Modal deployment configuration for Bank Support AI Agent.

This deploys the FastAPI application with Pydantic AI and Logfire to Modal.
Includes both the backend API and React frontend for a complete production system.
"""

import modal

# Type imports for IDE support (these will be available in the Modal container)
try:
    import logfire
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field, conint
    from pydantic_ai import Agent, RunContext
    from dataclasses import dataclass
    from typing import Optional, List
except ImportError:
    # These packages are only available in the Modal container
    # The imports inside the function will work correctly at runtime
    pass

# Production image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "pydantic-ai[openai]>=1.0.10",  # Pydantic AI with OpenAI support
        "logfire[httpx,fastapi]>=4.10.0",  # Logfire with HTTPX & FastAPI instrumentation
        "fastapi>=0.117.1",             # FastAPI framework
        "uvicorn>=0.37.0",              # ASGI server
        "pydantic>=2.11.9",             # Pydantic for data validation
        "python-dotenv>=1.0.0",         # For environment variable loading
        "openai>=1.109.1",              # OpenAI API client
        "httpx>=0.28.1",                # HTTP client
    )
    .apt_install("curl")  # For health checks
)

# Create Modal app
app = modal.App(name="bank-support")

# Production secrets (configure these in Modal dashboard)
secrets = [
    modal.Secret.from_name("openai"),    # OPENAI_API_KEY
    modal.Secret.from_name("logfire"),   # LOGFIRE_TOKEN
]

@app.function(
    image=image,
    secrets=secrets,
    memory=1024,        # 1GB RAM
    timeout=600,        # 10 minutes timeout for AI processing
    min_containers=1,   # Keep one instance warm for faster response
    max_containers=10   # Scale up to 10 containers if needed
)
@modal.asgi_app()
def bank_support_api():
    """
    Production FastAPI application with bank support AI agent.

    Features:
    - Pydantic AI agent with OpenAI GPT-4o
    - Risk assessment and card blocking decisions
    - Logfire telemetry and monitoring
    - CORS enabled for frontend integration
    """
    import os

    # Import packages available in Modal container environment
    # Note: These imports are resolved at runtime in the Modal container
    import logfire  # type: ignore
    from dataclasses import dataclass  # type: ignore
    from typing import Optional, List  # type: ignore
    from fastapi import FastAPI  # type: ignore
    from fastapi.middleware.cors import CORSMiddleware  # type: ignore
    from pydantic import BaseModel, Field, conint  # type: ignore
    from pydantic_ai import Agent, RunContext  # type: ignore

    # Configure Logfire inside the container
    print("🔧 Starting Logfire configuration...")

    logfire_token = os.getenv("LOGFIRE_TOKEN") or os.getenv("LOGFIRE_API_KEY")
    print(f"🔍 Environment check:")
    print(f"   LOGFIRE_TOKEN exists: {bool(os.getenv('LOGFIRE_TOKEN'))}")
    print(f"   LOGFIRE_API_KEY exists: {bool(os.getenv('LOGFIRE_API_KEY'))}")

    # Debug: Print token status (first few chars only for security)
    if logfire_token:
        print(f"✅ Logfire token found: {logfire_token[:10]}... (length: {len(logfire_token)})")
        try:
            logfire.configure(
                service_name="bank-support-agent",
                token=logfire_token
            )
            print("✅ Logfire configured with token")

            # Test a simple log message
            logfire.info("Modal container startup - Logfire test", extra={"test": "modal_startup"})
            print("✅ Test log message sent")

        except Exception as e:
            print(f"❌ Logfire configuration failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️ No Logfire token found, using local auth")
        try:
            logfire.configure(service_name="bank-support-agent")
            print("✅ Logfire configured without token")
        except Exception as e:
            print(f"❌ Logfire local configuration failed: {e}")

    # Instrument Logfire for tracing
    try:
        print("🔧 Setting up Logfire instrumentation...")
        logfire.instrument_pydantic_ai()
        print("✅ Pydantic AI instrumentation enabled")

        logfire.instrument_openai()
        print("✅ OpenAI instrumentation enabled")

    except Exception as e:
        print(f"❌ Instrumentation failed: {e}")
        import traceback
        traceback.print_exc()

    # ---------- Domain stubs ----------
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

    # ---------- Output schema with validation ----------
    class SupportOutput(BaseModel):
        support_advice: str = Field(description="Advice returned to the customer")
        block_card: bool = Field(description="Whether to block their card")
        risk: conint(ge=0, le=10) = Field(description="Risk level 0–10 (inclusive)")
        risk_explanation: str = Field(description="1 sentence explanation of why this risk level was assigned")
        risk_category: str = Field(description="Risk category: routine, concerning, urgent, or critical")
        risk_signals: list[str] = Field(default_factory=list, description="Signals/keywords found")

    # ---------- Agent with calibrated instructions ----------
    support_agent = Agent(
        "openai:gpt-4o",
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

    # ---------- Tool: balance lookup ----------
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

    # ---------- FastAPI app and endpoint ----------
    fastapi_app = FastAPI(title="bank-support-agent")

    # Add CORS middleware for production frontend
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure specific origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Instrument FastAPI after app creation
    logfire.instrument_fastapi(fastapi_app)

    class Query(BaseModel):
        question: str
        customer_name: str
        customer_id: int = 123
        include_pending: bool = True

    @fastapi_app.post("/support", response_model=SupportOutput)
    def support(q: Query) -> SupportOutput:
        deps = SupportDependencies(customer_id=q.customer_id, customer_name=q.customer_name, db=DatabaseConn())
        # The agent can decide to call the tool (customer_balance) if needed
        result = support_agent.run_sync(q.question, deps=deps)
        return result.output

    @fastapi_app.get("/health")
    def health():
        return {"status": "ok", "service": "bank-support-agent", "environment": "modal"}

    @fastapi_app.get("/")
    def root():
        return {"message": "Bank Support Agent API - Modal Deployment", "docs": "/docs"}

    return fastapi_app

# Static file serving for React frontend
@app.function(
    image=modal.Image.debian_slim()
    .apt_install("curl")
    .pip_install("fastapi", "aiofiles"),
    timeout=60,
)
@modal.asgi_app()
def frontend_app():
    """
    Serve the React frontend application.
    """
    # Import packages available in Modal container environment
    from fastapi import FastAPI  # type: ignore
    from fastapi.staticfiles import StaticFiles  # type: ignore
    from fastapi.responses import FileResponse  # type: ignore
    import os

    frontend = FastAPI()

    # Serve static files (will be created by build process)
    static_path = "/app/frontend/build"
    if os.path.exists(static_path):
        frontend.mount("/static", StaticFiles(directory=f"{static_path}/static"), name="static")

        @frontend.get("/{full_path:path}")
        async def serve_react_app(full_path: str):
            """Serve React app with proper routing."""
            if full_path.startswith("static/"):
                return FileResponse(f"{static_path}/{full_path}")
            return FileResponse(f"{static_path}/index.html")
    else:
        @frontend.get("/")
        async def placeholder():
            return {"message": "Frontend not built yet. Run the build process first."}

    return frontend

"""
Modal deployment configuration for Bank Support AI Agent.

This deploys the FastAPI application with Pydantic AI and Logfire to Modal.
Includes both the backend API and React frontend for a complete production system.
"""

import modal

# Production image with all dependencies
image = (
    modal.Image.debian_slim()
    .pip_install(
        "fastapi",
        "uvicorn",
        "pydantic-ai",
        "pydantic>=2",
        "logfire",
        "openai>=1.0.0",
        "python-dotenv",
    )
    .apt_install("curl")  # For health checks
)

# Create Modal app
app = modal.App(name="bank-support")

# Production secrets (configure these in Modal dashboard)
secrets = [
    modal.Secret.from_name("openai-secret"),    # OPENAI_API_KEY
    modal.Secret.from_name("logfire-secret"),   # LOGFIRE_TOKEN
]

@app.function(
    image=image,
    secrets=secrets,
    timeout=300,  # 5 minute timeout for AI processing
    keep_warm=1,  # Keep one instance warm for faster response
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
    from app.main import app as fastapi_app

    # Add CORS middleware for production frontend
    from fastapi.middleware.cors import CORSMiddleware

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure specific origins in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
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

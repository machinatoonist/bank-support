# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a bank customer support application built with FastAPI and Pydantic AI. The application provides an AI-powered support agent that can assist customers with banking inquiries, assess risk levels, and make decisions about card blocking based on customer interactions.

## Architecture

### Core Components

- **FastAPI Application** (`app/main.py`): Main web service with REST endpoints and CORS middleware
- **Next.js Frontend** (`frontend/`): Modern React-based UI with TypeScript and Tailwind CSS
- **Pydantic AI Agent**: OpenAI GPT-4o powered support agent with structured output
- **Database Layer**: Mock database implementation (`DatabaseConn`) for customer data
- **Observability**: Logfire integration for tracing FastAPI, Pydantic AI, and OpenAI calls

### Key Architecture Patterns

1. **Agent-Based Design**: Uses Pydantic AI Agent with:
   - Structured output via `SupportOutput` model
   - Dynamic instructions that include customer context
   - Tool integration for balance lookups
   - Risk assessment scoring (0-10 scale)

2. **Dependency Injection**: `SupportDependencies` dataclass provides context to the agent including customer ID and database connection

3. **Structured Output**: All agent responses follow the `SupportOutput` schema with validation for advice, card blocking decisions, and risk scores

## Environment Setup

### Required Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
LOGFIRE_API_KEY=your_logfire_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
```

### Virtual Environment

Use uv for dependency management:
```bash
# Create and activate environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync

# For shell environment variables
set -a && source .env && set +a
```

## Development Commands

### Running the Application

#### Full Development Stack (Recommended)

```bash
# Use the local development script to start all services
./start_local.sh
```

This starts:
- Backend API on `http://localhost:8000`
- Frontend UI on `http://localhost:3000`
- Example API on `http://localhost:8001`

#### Manual Service Management

```bash
# Start Backend API (required for frontend)
uv run uvicorn app.main:app --reload --port 8000

# Start Frontend UI (in another terminal)
cd frontend && npm run dev

# Start Example API (optional)
uv run uvicorn bank_support_example:app --reload --port 8001

# Run basic script
uv run python main.py
```

#### Service URLs

- **Frontend UI**: http://localhost:3000 (Bank Support AI Agent interface)
- **Backend API**: http://localhost:8000 (FastAPI with OpenAPI docs at /docs)
- **Example API**: http://localhost:8001 (Alternative FastAPI implementation)

#### Quick Development Workflow

1. Start all services: `./start_local.sh`
2. Open browser to http://localhost:3000
3. Enter your name and test the AI agent
4. View real-time telemetry at https://logfire-us.pydantic.dev/mattrosinski/bank-support
5. Run tests: `./test_local.sh`

### Working with Pydantic AI Examples

```bash
# Run Pydantic AI examples (requires environment variables loaded first)
set -a && source .env && set +a && uv run --with "pydantic-ai[examples]" -m pydantic_ai_examples.pydantic_model
```

### Testing

```bash
# Run comprehensive test suite (starts services, runs tests, stops services)
./test_local.sh

# Manual testing (requires services running)
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest test_bank_support_api.py -v

# Run Logfire telemetry verification (requires running server)
uv run pytest test_logfire.py -v

# Run smoke tests (alternative testing approach)
uv run python smoke_test.py
./smoke_test.sh

# Frontend tests
cd frontend && npm run lint
```

### Jupyter Development

```bash
# Register kernel for Jupyter
uv run python -m ipykernel install --user --name=bank-support

# The kernel "bank-support" will be available in Jupyter notebooks
```

## API Endpoints

- **POST /support**: Main support endpoint accepting customer questions
  - Input: `Query` model with question, customer_id, include_pending flag
  - Output: `SupportOutput` with advice, card blocking decision, and risk score

- **GET /health**: Health check endpoint

## Code Style

- Follow PEP 8 Python style guidelines
- Use type hints throughout the codebase
- Leverage Pydantic models for data validation
- Maintain structured logging with Logfire

## Development Notes

- The current `DatabaseConn` is a mock implementation with hardcoded data for customer ID 123
- The AI agent is configured to provide calibrated risk scores and make card blocking decisions
- Logfire provides comprehensive tracing across the FastAPI application, Pydantic AI agent, and OpenAI API calls

## Logfire Setup

The application supports both development and production Logfire configurations, automatically detecting which mode to use based on environment variables.

### Development Setup (Interactive)

For local development with interactive project setup:

1. **Authenticate**: `logfire auth` (credentials stored in ~/.logfire/default.toml)
2. **Set project**: `logfire projects use bank-support`
3. **Run app**: The app will automatically detect and use stored credentials
4. **View traces**: https://logfire-us.pydantic.dev/mattrosinski/bank-support

### Production Setup (Token-based)

For production deployments (Modal, Docker, cloud services):

1. **Generate Write Token**: Create a write token in the Logfire dashboard for your project
2. **Set Environment Variable**:
   ```bash
   export LOGFIRE_TOKEN=your_write_token_here
   ```
   Or add to your production environment:
   ```
   LOGFIRE_TOKEN=your_write_token_here
   ```
3. **Deploy**: The application will automatically detect the token and use it for authentication

### Modal Deployment Context

When deploying to Modal:

- **Environment Variables**: Set `LOGFIRE_TOKEN` in your Modal secrets or environment
- **No Interactive Auth**: Modal containers cannot use interactive authentication (`logfire auth`)
- **Automatic Detection**: The app will automatically use token-based auth when `LOGFIRE_TOKEN` is present
- **Service Name**: All traces will appear under service `bank-support` in your Logfire dashboard

Example Modal deployment with Logfire:
```python
import modal

# Set Logfire token in Modal secrets
app = modal.App("bank-support")

@app.function(
    secrets=[
        modal.Secret.from_name("openai-secret"),  # OPENAI_API_KEY
        modal.Secret.from_name("logfire-secret")  # LOGFIRE_TOKEN
    ]
)
def run_app():
    # App automatically detects LOGFIRE_TOKEN and configures appropriately
    ...
```

### Authentication Mode Detection

The application automatically detects which authentication mode to use:

- **Token Found**: Uses `LOGFIRE_TOKEN` or `LOGFIRE_API_KEY` (production mode)
- **No Token**: Falls back to stored credentials from `logfire auth` (development mode)
- **Priority**: `LOGFIRE_TOKEN` > `LOGFIRE_API_KEY` > stored credentials

### Token vs API Key

- `LOGFIRE_TOKEN`: Preferred for production, generated write tokens from Logfire dashboard
- `LOGFIRE_API_KEY`: Legacy environment variable, still supported for backward compatibility
- Both variables will authenticate with Logfire, but `LOGFIRE_TOKEN` is the modern approach

### Troubleshooting

- **Development**: If traces don't appear, ensure `logfire auth` and `logfire projects use bank-support` are completed
- **Production**: If traces don't appear, verify `LOGFIRE_TOKEN` environment variable is set correctly
- **Modal**: Ensure Logfire token is properly configured in Modal secrets
- **Testing**: Use `uv run pytest test_logfire.py -v` to verify telemetry is working (requires running server at localhost:8000)
- **Dashboard Verification**: Check https://logfire-us.pydantic.dev/mattrosinski/bank-support for real-time telemetry events
- Integrate Logfire
In this section, we'll focus on integrating Logfire with your application.

OpenTelemetry Instrumentation¶
Harnessing the power of OpenTelemetry, Logfire not only offers broad compatibility with any OpenTelemetry instrumentation package, but also includes a user-friendly CLI command that effortlessly highlights any missing components in your project.

To inspect your project, run the following command:


logfire inspect
This will output the projects you need to install to have optimal OpenTelemetry instrumentation:

Logfire inspect command

To install the missing packages, copy the command provided by the inspect command, and run it in your terminal.

Each instrumentation package has its own way to be configured. Check our Integrations page to learn how to configure them.
- uv run logfire projects use bank-support
Project configured successfully. You will be able to view it at: https://logfire-us.pydantic.dev/mattrosinski/bank-support
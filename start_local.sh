#!/bin/bash

# Bank Support Application - Local Development Server Startup Script
# This script starts all services needed for local development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_error "Please create a .env file with required API keys:"
    echo "OPENAI_API_KEY=your_openai_api_key"
    echo "LOGFIRE_API_KEY=your_logfire_api_key"
    echo "ANTHROPIC_API_KEY=your_anthropic_api_key"
    echo "GOOGLE_API_KEY=your_google_api_key"
    exit 1
fi

print_header "Bank Support Application - Local Development Setup"
echo

# Load environment variables
print_status "Loading environment variables..."
set -a
source .env
set +a

# Check for required dependencies
print_status "Checking dependencies..."

# Check uv
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install uv first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
uv sync

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

# Check if Logfire is configured
print_status "Checking Logfire configuration..."
if [ -z "$LOGFIRE_TOKEN" ] && [ -z "$LOGFIRE_API_KEY" ]; then
    print_warning "No Logfire token found. Checking for interactive auth..."
    if [ ! -f "$HOME/.logfire/default.toml" ]; then
        print_warning "Logfire not configured. Run 'logfire auth' and 'logfire projects use bank-support' first."
    fi
fi

# Create a function to handle cleanup
cleanup() {
    print_status "Shutting down services..."
    jobs -p | xargs -r kill
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

print_header "Starting Services"
echo

# Start backend API
print_status "Starting Backend API on http://localhost:8000..."
uv run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
print_status "Starting Frontend UI on http://localhost:3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Start example API
print_status "Starting Example API on http://localhost:8001..."
uv run uvicorn bank_support_example:app --reload --port 8001 &
EXAMPLE_PID=$!

# Wait a moment for services to start
sleep 5

echo
print_header "Services Status"
echo
print_status "✅ Backend API:  http://localhost:8000"
print_status "   - OpenAPI docs: http://localhost:8000/docs"
print_status "   - Health check: http://localhost:8000/health"
echo
print_status "✅ Frontend UI:  http://localhost:3000"
print_status "   - Bank Support AI Agent interface"
echo
print_status "✅ Example API:  http://localhost:8001"
print_status "   - Alternative implementation"
echo
print_status "📊 Logfire Dashboard: https://logfire-us.pydantic.dev/mattrosinski/bank-support"
echo

print_header "Development Workflow"
echo
echo "1. 🌐 Open your browser to http://localhost:3000"
echo "2. 👤 Enter your name to start a session"
echo "3. 💬 Test the AI agent with queries like:"
echo "   - 'I've lost my credit card'"
echo "   - 'Check my account balance'"
echo "   - 'I see suspicious activity'"
echo "4. 📊 Monitor telemetry in real-time on Logfire"
echo "5. 🔧 Backend API docs available at http://localhost:8000/docs"
echo

print_warning "Press Ctrl+C to stop all services"
echo

# Wait for background processes
wait
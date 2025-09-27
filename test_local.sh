#!/bin/bash

# Bank Support Application - Local Testing Script
# This script starts services, runs tests, and cleans up

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
    echo -e "${BLUE}[TEST]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_error "Please create a .env file with required API keys"
    exit 1
fi

print_header "Bank Support Application - Test Suite"
echo

# Load environment variables
print_status "Loading environment variables..."
set -a
source .env
set +a

# Install dependencies
print_status "Installing dependencies..."
uv sync

# Initialize variables
BACKEND_RUNNING=false
EXAMPLE_RUNNING=false
BACKEND_PID=""
EXAMPLE_PID=""

# Create a function to handle cleanup
cleanup() {
    print_status "Stopping test services..."
    # Only kill processes we started
    if [ "$BACKEND_RUNNING" = false ] && [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ "$EXAMPLE_RUNNING" = false ] && [ ! -z "$EXAMPLE_PID" ]; then
        kill $EXAMPLE_PID 2>/dev/null || true
    fi
    # Wait for processes to stop
    sleep 2
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM EXIT

print_header "Starting Test Services"
echo

# Check if services are already running

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Backend API already running on http://localhost:8000"
    BACKEND_RUNNING=true
else
    print_status "Starting Backend API on http://localhost:8000..."
    uv run uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
fi

if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_status "Example API already running on http://localhost:8001"
    EXAMPLE_RUNNING=true
else
    print_status "Starting Example API on http://localhost:8001..."
    uv run uvicorn bank_support_example:app --reload --port 8001 &
    EXAMPLE_PID=$!
fi

# Wait for services to start (only if we started them)
if [ "$BACKEND_RUNNING" = false ] || [ "$EXAMPLE_RUNNING" = false ]; then
    print_status "Waiting for services to start..."
    sleep 10
else
    print_status "All services already running, proceeding with tests..."
fi

# Health check
print_status "Performing health checks..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ Backend API is healthy"
else
    print_error "❌ Backend API health check failed"
    exit 1
fi

if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    print_status "✅ Example API is healthy"
else
    print_warning "⚠️  Example API health check failed (non-critical)"
fi

echo

print_header "Running Test Suite"
echo

# Run Python tests
print_status "Running Python tests..."
uv run pytest -v

echo

# Run API tests
print_status "Running API integration tests..."
uv run pytest test_bank_support_api.py -v

echo

# Run Logfire telemetry tests
print_status "Running Logfire telemetry tests..."
uv run pytest test_logfire.py -v

echo

# Run smoke tests
print_status "Running smoke tests..."
if [ -f "manual_smoke_check.py" ]; then
    uv run python manual_smoke_check.py
elif [ -f "smoke_test.sh" ]; then
    ./smoke_test.sh
else
    print_warning "No smoke tests found, skipping..."
fi

echo

# Test frontend if available
if [ -d "frontend" ]; then
    print_status "Running frontend linting..."
    cd frontend
    if [ -f "package.json" ]; then
        npm run lint || print_warning "Frontend linting failed"
    fi
    cd ..
fi

echo

print_header "Test Results Summary"
echo
print_status "✅ All tests completed successfully!"
print_status "📊 View detailed telemetry at: https://logfire-us.pydantic.dev/mattrosinski/bank-support"
echo

print_status "Test services will be stopped automatically..."
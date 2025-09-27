#!/bin/bash

# Build script for Bank Support AI application
# This script builds the React frontend and prepares for Modal deployment

set -e

echo "🚀 Building Bank Support AI Application"
echo "========================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo "🏗️  Building React frontend..."
npm run build

echo "📁 Creating deployment directory structure..."
cd ..
mkdir -p deploy/frontend
cp -r frontend/build/* deploy/frontend/

echo "✅ Build completed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure Modal secrets: modal secret create openai-secret OPENAI_API_KEY=your_key"
echo "2. Configure Modal secrets: modal secret create logfire-secret LOGFIRE_TOKEN=your_token"
echo "3. Deploy to Modal: modal deploy modal_app.py"
echo ""
echo "🎉 Ready for deployment!"
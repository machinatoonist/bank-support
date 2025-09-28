# Bank Support AI Agent - Replit Setup

## Overview
This is a bank support AI agent application with a Python FastAPI backend and Next.js React frontend. The application demonstrates intelligent risk assessment for banking customer inquiries.

## Recent Changes (September 28, 2025)
- Successfully imported from GitHub repository
- Installed Python dependencies (FastAPI, uvicorn, pydantic)
- Installed Node.js dependencies (Next.js, React, TailwindCSS)
- Configured backend to work without external API dependencies using mock agent
- Set up CORS to allow frontend-backend communication
- Configured Next.js for Replit environment (port 5000, host 0.0.0.0)
- Set up workflows for both frontend and backend
- Configured deployment for production autoscale

## Project Architecture
- **Backend**: Python FastAPI application (`app/main.py`)
  - Runs on localhost:8000 in development
  - Provides `/support` endpoint for AI chat responses
  - Uses mock agent when OpenAI API key is not available
  - Includes health check endpoint
- **Frontend**: Next.js React application (`frontend/`)
  - Runs on 0.0.0.0:5000 for Replit compatibility
  - Modern chat interface with risk assessment display
  - TailwindCSS for styling
  - Connects to backend API for chat functionality

## Configuration
- Backend CORS configured for Replit domain
- Frontend configured to trust proxy/bypass host verification
- Environment variables: NEXT_PUBLIC_API_URL for API base URL
- Deployment configured for autoscale with build process

## Current State
- Both frontend and backend are running successfully
- Application is fully functional with mock AI responses
- Ready for production deployment
- Can be enhanced with real OpenAI API key for actual AI responses

## User Preferences
- Clean, modern UI with risk assessment visualization
- Responsive design for different screen sizes
- Mock data provides realistic banking support scenarios
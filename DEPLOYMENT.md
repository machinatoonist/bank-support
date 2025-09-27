# Modal Deployment Guide

This guide explains how to deploy the Bank Support AI application to Modal with both the FastAPI backend and React frontend.

## Prerequisites

1. **Modal Account**: Sign up at [modal.com](https://modal.com)
2. **Modal CLI**: Install with `pip install modal`
3. **Node.js**: Version 16+ for building the React frontend
4. **API Keys**:
   - OpenAI API key for GPT-4o
   - Logfire token for telemetry

## Setup Instructions

### 1. Configure Modal

```bash
# Authenticate with Modal
modal token new

# Verify authentication
modal profile current
```

### 2. Create Modal Secrets

Create secrets in the Modal dashboard or via CLI:

```bash
# OpenAI API Key
modal secret create openai-secret OPENAI_API_KEY=sk-your-openai-key

# Logfire Token (get from Logfire dashboard)
modal secret create logfire-secret LOGFIRE_TOKEN=your-logfire-token
```

### 3. Build the Frontend

```bash
# Run the build script
./build.sh

# Or manually:
cd frontend
npm install
npm run build
```

### 4. Deploy to Modal

```bash
# Deploy the application
modal deploy modal_app.py

# This will create two endpoints:
# - bank_support_api: FastAPI backend with AI agent
# - frontend_app: React frontend (if built)
```

## Production Configuration

### Environment Variables

The application automatically detects production mode when `LOGFIRE_TOKEN` is available and configures:

- **Authentication**: Token-based Logfire authentication
- **CORS**: Enabled for frontend integration
- **Timeouts**: Extended to 5 minutes for AI processing
- **Keep Warm**: One instance kept warm for faster response

### Monitoring

- **Logfire Dashboard**: https://logfire-us.pydantic.dev/mattrosinski/bank-support
- **Modal Dashboard**: View logs, metrics, and scaling at modal.com
- **Health Check**: GET `/health` endpoint for monitoring

### Security

- API keys are stored as Modal secrets (encrypted)
- CORS configured for production
- No sensitive data in logs
- Structured telemetry for audit trails

## Frontend Configuration

### Development

```bash
cd frontend
npm start
# Runs on http://localhost:3000
# Proxies API calls to http://localhost:8000
```

### Production

The frontend automatically detects the API URL:
- Development: `http://localhost:8000`
- Production: Set `REACT_APP_API_URL` in build environment

### Features

- **Professional Chat Interface**: Clean, modern design
- **Real-time Risk Assessment**: Visual indicators for risk levels
- **Complete Response Display**: All AI agent fields shown for development
- **Responsive Design**: Works on desktop and mobile
- **Loading States**: Smooth user experience during AI processing

## Testing Deployment

### Local Testing

```bash
# Terminal 1: Start backend
uv run uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend && npm start

# Visit http://localhost:3000
```

### Production Testing

After deployment:

1. Visit the Modal app URL for the API
2. Test endpoints: `/health`, `/support`
3. Check Logfire dashboard for telemetry
4. Monitor Modal dashboard for performance

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Ensure Node.js 16+ is installed
   - Check frontend dependencies: `cd frontend && npm install`

2. **Deployment Errors**
   - Verify Modal authentication: `modal profile current`
   - Check secrets are created: `modal secret list`

3. **API Errors**
   - Verify OpenAI API key in Modal secrets
   - Check Logfire token configuration

4. **Frontend Issues**
   - Update API URL in frontend/.env
   - Check CORS configuration in modal_app.py

### Debugging

- **Modal Logs**: `modal logs <app-name>`
- **Local Development**: Run backend locally for debugging
- **Logfire Traces**: Check telemetry in Logfire dashboard

## Scaling

Modal automatically handles scaling based on demand:
- **Cold Start**: ~2-3 seconds for new instances
- **Keep Warm**: 1 instance kept warm for faster response
- **Auto Scaling**: Scales up during high traffic
- **Cost Optimization**: Scales down to zero when idle

## Next Steps

1. **Custom Domain**: Configure custom domain in Modal dashboard
2. **Enhanced Security**: Implement authentication for production use
3. **A/B Testing**: Deploy multiple versions for testing
4. **Monitoring**: Set up alerts for errors and performance
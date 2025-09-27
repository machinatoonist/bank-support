# Modal Deployment TODO List

This document outlines the steps required to deploy the Bank Support Application to Modal for production use.

## ✅ Completed
- [x] Local development environment setup
- [x] FastAPI backend with CORS middleware
- [x] Next.js frontend with TypeScript and Tailwind CSS
- [x] Pydantic AI agent with structured output
- [x] Logfire telemetry integration
- [x] Local testing scripts

## 🚧 In Progress

### Backend Deployment to Modal

- [ ] **Create Modal app configuration** (`modal_app.py`)
  - [ ] Configure Modal app with proper secrets
  - [ ] Set up Logfire token for production
  - [ ] Configure OpenAI API key
  - [ ] Set up CORS for production frontend URL
  - [ ] Configure proper resource limits (CPU, memory)
  - [ ] Set up custom domains if needed

- [ ] **Environment Variables & Secrets**
  - [ ] Create Modal secrets for API keys:
    - [ ] `openai-secret` with `OPENAI_API_KEY`
    - [ ] `logfire-secret` with `LOGFIRE_TOKEN`
    - [ ] `anthropic-secret` with `ANTHROPIC_API_KEY` (optional)
    - [ ] `google-secret` with `GOOGLE_API_KEY` (optional)
  - [ ] Update CORS origins for production domain
  - [ ] Configure production database connection (if replacing mock)

- [ ] **Backend Code Modifications**
  - [ ] Update CORS middleware for production origins
  - [ ] Add health check endpoint optimizations
  - [ ] Configure production logging levels
  - [ ] Add rate limiting middleware
  - [ ] Implement proper error handling for production
  - [ ] Add metrics collection endpoints

### Frontend Deployment

- [ ] **Choose Frontend Hosting Platform**
  - [ ] Option A: Vercel (recommended for Next.js)
  - [ ] Option B: Netlify
  - [ ] Option C: AWS Amplify
  - [ ] Option D: Modal (if supporting static sites)

- [ ] **Frontend Configuration**
  - [ ] Update API base URL to Modal backend
  - [ ] Configure environment variables for production
  - [ ] Set up proper build pipeline
  - [ ] Configure custom domain and SSL
  - [ ] Add analytics tracking (optional)

- [ ] **Frontend Code Modifications**
  - [ ] Update API endpoints to production URLs
  - [ ] Add error boundaries for production
  - [ ] Implement proper loading states
  - [ ] Add SEO metadata
  - [ ] Configure proper favicon and app icons

### Infrastructure & DevOps

- [ ] **CI/CD Pipeline**
  - [ ] Set up GitHub Actions workflow
  - [ ] Configure automated testing on PR
  - [ ] Set up deployment triggers
  - [ ] Add rollback capabilities
  - [ ] Configure staging environment

- [ ] **Monitoring & Observability**
  - [ ] Set up production Logfire project
  - [ ] Configure alerts for critical errors
  - [ ] Set up uptime monitoring
  - [ ] Add performance monitoring
  - [ ] Configure log aggregation

- [ ] **Security & Compliance**
  - [ ] Implement rate limiting
  - [ ] Add input validation and sanitization
  - [ ] Set up HTTPS with proper certificates
  - [ ] Configure security headers
  - [ ] Implement API authentication (if needed)
  - [ ] Add CSRF protection

### Database & Storage

- [ ] **Production Database**
  - [ ] Replace mock database with real implementation
  - [ ] Choose database provider (PostgreSQL, MongoDB, etc.)
  - [ ] Set up database migrations
  - [ ] Configure backup strategies
  - [ ] Implement connection pooling

- [ ] **Data Management**
  - [ ] Design customer data schema
  - [ ] Implement data privacy controls
  - [ ] Set up data retention policies
  - [ ] Add audit logging
  - [ ] Configure data encryption

### Testing & Quality Assurance

- [ ] **Production Testing**
  - [ ] Set up end-to-end tests
  - [ ] Configure load testing
  - [ ] Test deployment pipeline
  - [ ] Validate production environment
  - [ ] Performance testing and optimization

- [ ] **Quality Gates**
  - [ ] Set up code coverage requirements
  - [ ] Configure security scanning
  - [ ] Add dependency vulnerability checks
  - [ ] Implement code quality checks

### Documentation & Maintenance

- [ ] **Production Documentation**
  - [ ] Update deployment instructions
  - [ ] Document production architecture
  - [ ] Create runbooks for common issues
  - [ ] Document backup and recovery procedures
  - [ ] Add API documentation for production

- [ ] **Maintenance Procedures**
  - [ ] Set up automated dependency updates
  - [ ] Configure backup verification
  - [ ] Plan disaster recovery procedures
  - [ ] Document scaling procedures

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing locally
- [ ] Environment variables configured
- [ ] Modal secrets created
- [ ] Production domain configured
- [ ] SSL certificates ready

### Deployment
- [ ] Deploy backend to Modal
- [ ] Deploy frontend to chosen platform
- [ ] Configure DNS settings
- [ ] Update CORS settings
- [ ] Test production deployment

### Post-Deployment
- [ ] Verify all endpoints working
- [ ] Check Logfire telemetry
- [ ] Test end-to-end functionality
- [ ] Monitor performance metrics
- [ ] Set up alerts and monitoring

## 🔧 Development Scripts for Modal

### Required Scripts
- [ ] `deploy_backend.py` - Script to deploy backend to Modal
- [ ] `deploy_frontend.sh` - Script to deploy frontend
- [ ] `setup_secrets.py` - Script to configure Modal secrets
- [ ] `test_production.py` - Script to test production deployment

### Configuration Files
- [ ] `modal_requirements.txt` - Production Python dependencies
- [ ] `docker/Dockerfile` - If using custom containers
- [ ] `.github/workflows/deploy.yml` - GitHub Actions deployment
- [ ] `production.env.example` - Example production environment file

## 🎯 Success Criteria

The deployment is considered successful when:
- [ ] Frontend accessible at production URL
- [ ] Backend API responding correctly
- [ ] AI agent functioning with proper risk assessment
- [ ] Logfire telemetry working in production
- [ ] All tests passing in production environment
- [ ] Performance meets requirements
- [ ] Security measures in place
- [ ] Monitoring and alerts configured

## 📞 Emergency Contacts

- Modal Support: [Modal documentation](https://modal.com/docs)
- Frontend Hosting Support: (depends on chosen platform)
- Logfire Support: [Logfire documentation](https://docs.pydantic.dev/logfire/)

## 📅 Timeline Estimate

- **Backend Deployment**: 1-2 days
- **Frontend Deployment**: 1 day
- **Infrastructure Setup**: 2-3 days
- **Testing & QA**: 2-3 days
- **Documentation**: 1 day

**Total Estimated Time**: 7-10 days

---

*This TODO list should be updated as deployment progresses. Mark items as completed and add any additional requirements discovered during implementation.*
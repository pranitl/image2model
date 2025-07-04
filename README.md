# AI 3D Model Generator

An AI-powered platform that converts 2D images into 3D models using advanced machine learning algorithms. Built with a vanilla JavaScript frontend and FastAPI/Python backend in a containerized monorepo architecture.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Development Setup

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd image2model
   cp .env.example .env
   ```

2. **Start the application**
   ```bash
   # Using Docker Compose v2 (recommended)
   docker compose up -d
   
   # Or using the Makefile (handles Docker Compose version automatically)
   make up
   
   # Alternative legacy command (if using older Docker)
   docker-compose up -d
   ```

3. **Access the application**
   - **Frontend**: http://localhost:3000 (Vanilla JavaScript)
   - **Backend API**: http://localhost:8000 (FastAPI)
   - **API Documentation**: http://localhost:8000/docs (Swagger UI)
   - **Database Admin**: http://localhost:5050 (PgAdmin) - *Development only*
   - **Task Monitor**: http://localhost:5555 (Flower - Celery) - *Username: admin, Password: password*
   - **Redis Admin**: http://localhost:8081 (Redis Commander) - *Development only*

## 🏗️ Architecture

### Project Structure
```
image2model/
├── frontend-simple/       # Vanilla JavaScript frontend
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript modules
│   │   ├── api.js         # API client
│   │   ├── upload.js      # Upload functionality
│   │   ├── processing.js  # Progress tracking
│   │   └── results.js     # Results display
│   ├── assets/            # Static assets
│   └── *.html             # HTML pages
├── backend/               # FastAPI/Python application
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Configuration and utilities
│   │   ├── models/        # Database models
│   │   └── workers/       # Background task workers
│   ├── uploads/           # File upload storage
│   ├── results/           # Generated model storage
│   └── models/            # AI model storage
├── docker/                # Docker configuration files
├── docs/                  # Project documentation
└── .taskmaster/           # Task management configuration
```

### Technology Stack

**Frontend:**
- Vanilla JavaScript (ES6+) with modular architecture
- Native HTML5 APIs for drag-and-drop file uploads
- Server-Sent Events (SSE) for real-time progress updates
- Fetch API for backend communication
- Model Viewer library for 3D model preview
- Responsive CSS with modern design patterns
- No build step required - direct browser execution

**Backend:**
- FastAPI 0.104+ with async/await support
- SQLAlchemy 2.0+ ORM with PostgreSQL
- Celery 5.3+ for background task processing with parallel execution
- Redis 7.0+ for message brokering and caching
- Pydantic 2.5+ for data validation and settings
- Uvicorn ASGI server with hot reload
- Python-multipart for file upload handling
- FAL.AI API integration for 3D model generation
- Structured logging with correlation IDs
- Enhanced progress tracking with file-level updates

**Infrastructure:**
- Docker & Docker Compose v2
- PostgreSQL 15 database (internal network only)
- Redis 7 Alpine (internal network only)
- Nginx for static file serving
- Multiple Celery workers for load balancing
- Health checks for all services

## 🔧 Development

### Available Commands

```bash
# Docker operations (automatically uses 'docker compose' or 'docker-compose')
make up              # Start all services
make down            # Stop all services
make restart         # Restart all services
make logs            # View logs from all services
make clean           # Remove containers and volumes

# Production deployment
make prod-build      # Build production images
make prod-deploy     # Deploy production environment
make prod-start      # Start production services
make prod-stop       # Stop production services
make prod-logs       # Show production logs
make prod-status     # Show production container status

# Development
make shell-frontend  # Access frontend container shell
make shell-backend   # Access backend container shell
make install-deps    # Install dependencies in both frontend/backend

# Database
make db-migrate      # Run database migrations
make db-reset        # Reset database (destructive)
```

### Running Without Docker

**Frontend:**
```bash
cd frontend-simple
# No installation needed - open index.html in browser
# Or use a simple HTTP server:
python -m http.server 3000
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=image2model

# Redis
REDIS_URL=redis://localhost:6379

# FAL.AI API Configuration (required for 3D model generation)
FAL_API_KEY=your_fal_api_key_here

# Application
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

## 📝 API Documentation

The API provides comprehensive endpoints for:

### ✅ Core Processing Endpoints
- **File Upload (Single)**: `POST /api/v1/upload/image` - Upload single image for processing
- **File Upload (Batch)**: `POST /api/v1/upload/batch` - Upload multiple images (max 25)
- **Upload Status**: `GET /api/v1/upload/status/{upload_id}` - Check upload processing status
- **Task Stream (SSE)**: `GET /api/status/tasks/{task_id}/stream` - Real-time progress via Server-Sent Events
- **Task Status**: `GET /api/status/tasks/{task_id}/status` - One-time task status check
- **Model Download**: `GET /api/v1/download/{job_id}/{filename}` - Download individual 3D model files
- **Job Files List**: `GET /api/v1/download/{job_id}/all` - List all files for a completed job

### ✅ Admin & File Management
- **Disk Usage**: `GET /api/v1/admin/disk-usage` - Get current disk usage statistics
- **System Health**: `GET /api/v1/admin/system-health` - Overall system health with disk warnings
- **Manual Cleanup**: `POST /api/v1/admin/cleanup` - Trigger cleanup of old files (configurable hours)
- **Job Cleanup**: `POST /api/v1/admin/cleanup-job` - Clean up files for specific job ID
- **File Listing**: `GET /api/v1/admin/list-files` - List files in uploads/results directories
- **Delete Job**: `DELETE /api/v1/admin/delete-job/{job_id}` - Delete all files for a job
- **Admin Dashboard**: `GET /admin` - Frontend file management interface

### ✅ Health & Monitoring
- **Basic Health**: `GET /api/v1/health` - Simple service health check
- **Detailed Health**: `GET /api/v1/health/detailed` - Comprehensive system health with components
- **Metrics**: `GET /api/v1/health/metrics` - Prometheus metrics endpoint
- **Liveness Probe**: `GET /api/v1/health/liveness` - Kubernetes liveness probe
- **Readiness Probe**: `GET /api/v1/health/readiness` - Kubernetes readiness probe

### ✅ Logging & Analytics
- **Log Analysis**: `GET /api/v1/logs/analyze` - Real-time log pattern analysis
- **Daily Summary**: `GET /api/v1/logs/daily-summary` - Log summary with metrics
- **Export Logs**: `GET /api/v1/logs/export` - Export logs in various formats
- **Log Health**: `GET /api/v1/logs/health` - Log system health status

### ✅ Production Infrastructure (Tasks 13-14)
- **Docker Production Config**: ✅ Multi-stage builds, Nginx reverse proxy, Redis optimization
- **Automated Deployment**: ✅ Production deployment scripts with health validation
- **Security Features**: ✅ Security headers, non-root containers, environment isolation
- **Monitoring & Metrics**: ✅ Prometheus metrics, structured logging, system monitoring
- **Health Checks**: ✅ Comprehensive health checks for all services (Redis, Celery, FAL.AI, disk space)
- **Log Management**: ✅ Automated log rotation, compression, and cleanup with analytics
- **Background Tasks**: ✅ System monitoring, log maintenance, and health alerts
- **Resource Monitoring**: ✅ CPU, memory, disk usage tracking with configurable thresholds

### 🔄 Final Phase (Task 15)
- **End-to-End Testing**: Production testing and validation

### File Upload Specifications
- **Max Files**: 25 images per batch upload
- **File Size**: 10MB maximum per file
- **Formats**: .jpg, .jpeg, .png only
- **Face Limit**: Optional parameter for processing control

## 🛡️ Error Handling & Reliability

### Comprehensive Error Management
- **Custom Exceptions**: Specialized error classes for different failure types (API, Network, Validation, Processing)
- **Standardized Responses**: Consistent error format with error codes, messages, and actionable details
- **User-Friendly Messages**: Non-technical error messages with clear next steps for users

### Retry Logic & Circuit Breakers
- **Exponential Backoff**: Smart retry delays (60s to 15min for rate limits, 30s to 5min for timeouts)
- **Circuit Breaker**: Automatic failure detection prevents cascading errors after 3 consecutive failures
- **Error Classification**: Automatic detection of retryable vs permanent failures
- **Rate Limit Handling**: Intelligent backoff when FAL.AI API limits are exceeded

### Frontend Error Recovery
- **Error Boundaries**: React components gracefully handle and recover from JavaScript errors
- **Toast Notifications**: User-friendly error messages with retry options and progress indicators
- **Global Error State**: Centralized error management with automatic retry and recovery flows
- **Network Resilience**: Automatic retry for network failures with offline detection

### Backend Resilience
- **FastAPI Middleware**: Global exception handling with proper HTTP status codes
- **Celery Retries**: Background task retry with job-specific error handling and recovery
- **File Validation**: Comprehensive upload validation with detailed error feedback
- **API Error Mapping**: FAL.AI specific error handling with appropriate user messaging

### Monitoring & Testing
- **Comprehensive Test Suite**: Unit tests, integration tests, and load testing for error scenarios
- **Error Logging**: Detailed error tracking with context and correlation IDs
- **Health Monitoring**: Service health checks with error rate and performance metrics
- **Recovery Verification**: Automated testing of error recovery and system stability
- **Validation**: Comprehensive file type and size validation
- **Progress**: Real-time upload and processing progress

Interactive API documentation is available at http://localhost:8000/docs when running.

## 🔄 Current Workflow (Tasks 1-6 Complete)

### ✅ Implemented Features
1. **Upload Interface**: Vanilla JS drag-and-drop file upload with validation
2. **File Validation**: Comprehensive client and server-side validation
3. **Batch Processing**: Support for multiple file uploads (max 25 images)
4. **Background Tasks**: Celery worker infrastructure with Redis message broker
5. **Progress Tracking**: Real-time file-level progress updates via SSE
6. **Error Handling**: Robust error handling with user-friendly messages

### ✅ Production-Ready Features (Tasks 7-14)
7. ✅ **FAL.AI Integration**: AI-powered 3D model generation from 2D images
8. ✅ **Real-time Updates**: Server-sent events for live progress monitoring
9. ✅ **Processing Dashboard**: Real-time progress interface with file status grid
10. ✅ **Download System**: Generated model download and file management
11. ✅ **Error Handling**: Comprehensive retry logic and circuit breakers
12. ✅ **File Management**: Automated cleanup with disk space monitoring
13. ✅ **Docker Configuration**: Production-ready deployment infrastructure
14. ✅ **Monitoring & Logging**: Enterprise-grade observability and metrics

### Technical Flow
1. **Frontend Upload**: Users drag/drop images in vanilla JS interface
2. **Client Validation**: File type, size, and count validation
3. **API Upload**: Multipart form data sent to FastAPI backend
4. **Server Validation**: Additional security and format validation
5. **Celery Queue**: Background tasks queued for parallel processing
6. **Worker Processing**: Multiple Celery workers handle image processing in parallel
7. **Progress Updates**: Real-time file-level status updates via SSE
8. **FAL.AI Processing**: Workers coordinate with FAL.AI API for 3D generation
9. **Result Download**: Generated GLB files available for download

## 🧪 Testing

### Comprehensive Test Suite

The Image2Model platform includes a comprehensive integration and end-to-end testing suite with focus on MVP validation and production readiness.

#### Quick Start

```bash
# Install all dependencies (includes test dependencies)
pip install -r requirements.txt

# Quick smoke test (30 seconds)
python tests/run_tests.py smoke

# Integration tests (5-10 minutes)
python tests/run_tests.py integration

# End-to-end tests (10-20 minutes)  
python tests/run_tests.py e2e

# All tests with HTML report
python tests/run_tests.py all --html --verbose
```

#### Test Categories

- **Smoke Tests**: Quick production health validation
- **Integration Tests**: API endpoints and workflow validation
- **End-to-End Tests**: Complete user journey simulation  
- **Load Tests**: Performance and scalability validation
- **Docker Tests**: Production deployment configuration

#### Advanced Features

- Parallel test execution with pytest-xdist
- Coverage reporting with HTML output
- Real-time progress monitoring validation
- Docker Compose configuration testing
- Prometheus metrics validation
- Service dependency health checks
- Production readiness validation

See `tests/README.md` for comprehensive testing documentation.

### Legacy Test Commands

```bash
# Run all tests
make test

# Frontend tests (vanilla JS - no test framework)

# Backend tests
cd backend && python -m pytest
```

## 🚢 Deployment

### Production Build

```bash
# Automated production deployment (recommended)
make prod-deploy

# Manual production build
make prod-build
make prod-start

# Alternative manual approach with Docker Compose v2
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Legacy approach (older Docker versions)
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Environment-Specific Configurations

- **Development**: Uses `docker-compose.yml` + `docker-compose.override.yml` automatically
- **Production**: Uses `docker-compose.yml` + `docker-compose.prod.yml`
- **Staging**: Can use custom staging configurations

### Production Features

✅ **Security & Performance**:
- Nginx reverse proxy with security headers
- Multi-stage Docker builds for smaller images
- Non-root container users
- GZIP compression and static file caching
- Redis persistence and memory optimization

✅ **Automated Deployment**:
- Health validation during deployment
- Service dependency management
- Environment validation and prerequisite checking
- Automatic rollback on deployment failures

## 📊 Monitoring

### Available Monitoring Tools

- **Application Logs**: `docker compose logs -f` or `make logs`
- **Production Logs**: `make prod-logs` for production environment
- **Celery Tasks**: Flower UI at http://localhost:5555
- **Database**: PgAdmin at http://localhost:5050
- **Redis**: Redis Commander at http://localhost:8081
- **Health Checks**: Built-in endpoint monitoring at `/api/v1/health`
- **Metrics**: Prometheus metrics at `/api/v1/health/metrics`
- **File Management**: Admin dashboard at http://localhost:3000/admin.html
- **Log Analytics**: Real-time log analysis at `/api/v1/logs/analyze`

### Performance Metrics

The application includes comprehensive monitoring and metrics collection:

### ✅ **System Metrics**
- **CPU Usage**: Real-time CPU utilization tracking
- **Memory Usage**: Memory consumption monitoring with alerts
- **Disk Usage**: Disk space monitoring with automated cleanup
- **Network Performance**: Request/response time tracking

### ✅ **Application Metrics**
- **API Response Times**: HTTP request duration and status code tracking
- **Background Task Processing**: Celery task execution monitoring
- **Database Connection Health**: PostgreSQL connectivity and performance
- **Redis Connectivity**: Cache and message broker health checks
- **FAL.AI Integration**: 3D model generation API monitoring
- **Error Rates**: Comprehensive error tracking and classification

### ✅ **Operational Metrics**
- **File System Usage**: Upload and result directory monitoring
- **File Retention Policies**: Automated cleanup statistics
- **Health Check Status**: Service dependency monitoring
- **Log Analytics**: Pattern detection and anomaly monitoring

## 🤝 Contributing

### Development Workflow

1. Create feature branch from `main`
2. Make changes following project conventions
3. Test changes locally with Docker
4. Submit pull request with descriptive commit messages
5. Ensure all CI checks pass

### Code Style

- **Frontend**: ESLint + Prettier configuration
- **Backend**: Black + isort + mypy
- **Commits**: Follow conventional commit format

## 📋 Task Management

This project uses Task Master AI for project management:

```bash
# View current tasks
task-master list

# Get next task to work on
task-master next

# Mark task complete
task-master set-status --id=<task-id> --status=done
```

## 🐛 Troubleshooting

### Common Issues

**Docker Compose command not found:**
```bash
# If you get "zsh: command not found: docker-compose"
# Use the newer Docker Compose v2 syntax instead:
docker compose up -d

# Or use the Makefile which handles both versions:
make up
```

**Docker Compose version warnings:**
```bash
# If you see warnings about deprecated 'version' field, these are harmless
# The application will work correctly - these warnings can be ignored
```

**Environment validation errors:**
```bash
# Fix environment mapping errors in docker-compose.override.yml
# Make sure all environment variables use proper YAML syntax:
environment:
  REDIS_HOSTS: "local:redis:6379"  # ✅ Correct (quoted)
  # REDIS_HOSTS=local:redis:6379   # ❌ Wrong (shell syntax)
```

**Docker containers won't start:**
```bash
make clean  # Remove containers and volumes
make up     # Restart fresh
```

**Database connection errors:**
```bash
make db-reset  # Reset database
```

**Frontend/Backend not hot reloading:**
- Ensure volume mounts are working in docker-compose.override.yml
- Check file permissions on mounted volumes

See `DOCKER.md` for comprehensive troubleshooting guide.

## 📚 Documentation

- `DOCKER.md` - Docker setup and troubleshooting
- `CLAUDE.md` - Claude Code integration and task management
- `/docs` - Additional project documentation
- API docs at `/docs` endpoint when running

## 📄 License

[License information to be added]

---

**Last Updated**: 2025-07-04  
**Recent Changes**: 
- Migrated from React to vanilla JavaScript frontend for simplicity
- Enhanced parallel processing with file-level progress tracking
- Improved container security by removing unnecessary port exposures
- Fixed Flower monitoring container authentication issues


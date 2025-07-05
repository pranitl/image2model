# Image2Model Backend

FastAPI backend service for generating 3D models from images using AI/ML models.

## Quick Start

### Using Docker Compose (Recommended)

1. **Start all services:**
   ```bash
   docker compose up -d
   ```

2. **Check service health:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **View API documentation:**
   Open http://localhost:8000/docs in your browser

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Start Celery worker (in another terminal):**
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info
   ```

## API Endpoints

### Health Check
- `GET /health` - Basic health check
- `GET /api/v1/health/` - API health check
- `GET /api/v1/health/detailed` - Detailed system health

### File Upload
- `POST /api/v1/upload/image` - Upload image for processing
- `GET /api/v1/upload/status/{file_id}` - Get upload status

### 3D Model Generation
- `POST /api/v1/models/generate` - Start 3D model generation
- `GET /api/v1/models/job/{job_id}` - Get generation job status
- `GET /api/v1/models/available` - List available models
- `GET /api/v1/models/download/{job_id}` - Download generated model

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── api.py          # Main API router
│   │   └── endpoints/      # Individual endpoint files
│   │       ├── health.py   # Health check endpoints
│   │       ├── upload.py   # File upload endpoints
│   │       └── models.py   # Model generation endpoints
│   ├── core/               # Core application modules
│   │   ├── __init__.py
│   │   └── config.py       # Application configuration
│   ├── models/             # Database models
│   │   ├── __init__.py
│   │   ├── base.py         # Base database setup
│   │   └── file.py         # File-related models
│   └── workers/            # Background task workers
│       ├── __init__.py
│       ├── celery_app.py   # Celery configuration
│       └── tasks.py        # Background tasks
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker compose.yml     # Multi-service setup
└── .env.example          # Environment variables template
```

## Configuration

Key environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `CELERY_BROKER_URL` - Redis URL for Celery broker
- `CELERY_RESULT_BACKEND` - Redis URL for Celery results
- `BACKEND_CORS_ORIGINS` - Allowed CORS origins
- `UPLOAD_DIR` - Directory for uploaded files
- `MAX_FILE_SIZE` - Maximum upload file size
- `DEFAULT_MODEL` - Default AI model for generation

## Dependencies

### Core Dependencies
- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **SQLAlchemy** - Database ORM
- **Celery** - Background task queue

### AI/ML Dependencies
- **PyTorch** - Deep learning framework
- **Transformers** - Pre-trained models
- **OpenCV** - Computer vision
- **Pillow** - Image processing
- **NumPy** - Numerical computing

### Infrastructure
- **PostgreSQL** - Primary database
- **Redis** - Task queue backend
- **Docker** - Containerization

## Development

### Code Style
```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Deployment

### Docker
```bash
# Build image
docker build -t image2model-backend .

# Run container
docker run -p 8000:8000 image2model-backend
```

### Production Considerations
- Use environment variables for configuration
- Set up proper logging and monitoring
- Configure reverse proxy (nginx/traefik)
- Set up SSL/TLS certificates
- Monitor Celery workers and Redis
- Implement backup strategy for PostgreSQL
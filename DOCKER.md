# Docker Setup for Image2Model

This document provides instructions for setting up and running the Image2Model application using Docker.

## Prerequisites

- Docker Engine 20.10 or later
- Docker Compose v2.0 or later
- At least 4GB of available RAM
- At least 10GB of available disk space

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd image2model
   ```

2. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

3. **Edit environment variables:**
   ```bash
   # Edit .env file with your preferred settings
   nano .env
   ```

4. **Start the application:**
   ```bash
   # Using Docker Compose
   docker-compose up -d

   # OR using Makefile
   make up
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Celery Flower: http://localhost:5555
   - PgAdmin: http://localhost:5050 (admin@image2model.local / admin)
   - Redis Commander: http://localhost:8081

## Services Overview

| Service | Port | Description |
|---------|------|-------------|
| **frontend** | 3000 | React application with Vite dev server |
| **backend** | 8000 | FastAPI application with hot reload |
| **worker** | - | Celery worker for background tasks |
| **postgres** | 5432 | PostgreSQL database |
| **redis** | 6379 | Redis for Celery message broker |
| **flower** | 5555 | Celery monitoring interface |
| **pgadmin** | 5050 | PostgreSQL admin interface (dev only) |
| **redis-commander** | 8081 | Redis admin interface (dev only) |

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=image2model

# Backend
BACKEND_CORS_ORIGINS=http://localhost:3000
SECRET_KEY=your-secret-key-here

# Frontend
VITE_API_URL=http://localhost:8000

# Optional API Keys
OPENAI_API_KEY=your-openai-key
HUGGING_FACE_API_KEY=your-hf-key
```

### Volume Mounts

The following directories are mounted for development:

- `./backend` → `/app` (backend source code)
- `./frontend` → `/app` (frontend source code)
- `backend_uploads` → `/app/uploads` (file uploads)
- `backend_results` → `/app/results` (processing results)
- `backend_models` → `/app/models` (ML models cache)
- `postgres_data` → PostgreSQL data persistence
- `redis_data` → Redis data persistence

## Development Commands

### Using Makefile (Recommended)

```bash
# Start services
make up

# View logs
make logs

# Access shells
make shell-backend
make shell-frontend
make shell-db

# Database operations
make db-migrate
make db-reset

# Maintenance
make restart
make clean
make prune
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh

# Database shell
docker-compose exec postgres psql -U postgres -d image2model

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build
```

## Development Workflow

### Hot Reload

Both frontend and backend support hot reload:

- **Frontend**: Vite automatically reloads on file changes
- **Backend**: Uvicorn reloads on Python file changes
- **Worker**: Watchdog automatically restarts Celery worker

### Database Migrations

```bash
# Run migrations
make db-migrate
# OR
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Testing

```bash
# Run backend tests
docker-compose exec backend python -m pytest

# Run frontend tests
docker-compose exec frontend npm test

# OR using Makefile
make test
```

### Debugging

#### Backend Debugging

1. **View logs:**
   ```bash
   make logs-backend
   ```

2. **Access backend shell:**
   ```bash
   make shell-backend
   ```

3. **Check health:**
   ```bash
   curl http://localhost:8000/health
   ```

#### Frontend Debugging

1. **View logs:**
   ```bash
   make logs-frontend
   ```

2. **Access frontend shell:**
   ```bash
   make shell-frontend
   ```

3. **Check build:**
   ```bash
   docker-compose exec frontend npm run build
   ```

## Production Deployment

### Production Build

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Production Considerations

1. **Environment Variables:**
   - Set `NODE_ENV=production`
   - Set `ENVIRONMENT=production`
   - Use strong passwords and secrets
   - Configure proper CORS origins

2. **Security:**
   - Use non-root users (already configured)
   - Enable SSL/TLS termination
   - Configure firewall rules
   - Regular security updates

3. **Performance:**
   - Use production builds
   - Enable gzip compression
   - Configure proper caching
   - Monitor resource usage

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check if ports are in use
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Stop conflicting services
docker-compose down
```

#### Volume Permission Issues
```bash
# Fix ownership (Linux/macOS)
sudo chown -R $USER:$USER ./backend/uploads
sudo chown -R $USER:$USER ./backend/results
sudo chown -R $USER:$USER ./backend/models
```

#### Database Connection Issues
```bash
# Reset database
make db-reset

# Check database logs
make logs-db

# Access database directly
make shell-db
```

#### Build Failures
```bash
# Clean Docker cache
make prune

# Rebuild from scratch
docker-compose build --no-cache
```

### Log Analysis

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Follow logs for specific service
make logs-backend
```

### Performance Monitoring

- **Flower**: http://localhost:5555 - Celery task monitoring
- **PgAdmin**: http://localhost:5050 - Database monitoring
- **Redis Commander**: http://localhost:8081 - Redis monitoring

### Resource Usage

```bash
# Container stats
docker stats

# System resource usage
docker system df

# Container resource limits
docker-compose exec backend cat /sys/fs/cgroup/memory/memory.limit_in_bytes
```

## Additional Tools

### Database Management

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres image2model > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres image2model < backup.sql

# Access PgAdmin
open http://localhost:5050
```

### Redis Management

```bash
# Redis CLI
docker-compose exec redis redis-cli

# Monitor Redis
docker-compose exec redis redis-cli monitor

# Access Redis Commander
open http://localhost:8081
```

### Celery Management

```bash
# View active tasks
docker-compose exec worker celery -A app.workers.celery_app inspect active

# View registered tasks
docker-compose exec worker celery -A app.workers.celery_app inspect registered

# Purge all tasks
docker-compose exec worker celery -A app.workers.celery_app purge
```

## Support

For additional help:

1. Check logs: `make logs`
2. Verify configuration: `make env-info`
3. Reset environment: `make clean && make up`
4. Check Docker system: `docker system info`

## Contributing

When contributing to the Docker setup:

1. Test changes with a clean environment
2. Update this documentation
3. Verify both development and production builds
4. Test on different platforms (Linux, macOS, Windows)
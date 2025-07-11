# Quick Start Guide

> **Last Updated**: 2025-07-11  
> **Status**: Complete  
> **Version**: 1.0

## Overview

Get image2model running on your local machine in 5 minutes! This guide provides the fastest path to a working development environment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing Your Setup](#testing-your-setup)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker Desktop** (includes Docker Compose)
- **Git** for cloning the repository
- **FAL.AI API Key** ([Get one here](https://fal.ai))

### System Requirements

- **OS**: macOS, Linux, or Windows with WSL2
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk**: At least 5GB free space

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/image2model.git
cd image2model
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your FAL.AI API key:

```env
# FAL.AI Configuration
FAL_API_KEY=your-fal-api-key-here

# Application Settings
API_KEY=your-secure-api-key-here
MAX_UPLOAD_SIZE_MB=10
```

## Configuration

### Generate a Secure API Key

Run this command to generate a secure API key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as the value for `API_KEY` in your `.env` file.

### Verify Docker Setup

Ensure Docker is running:

```bash
docker --version
docker compose version
```

## Running the Application

### Start All Services

From the project root directory:

```bash
docker compose up --build
```

This command will:
1. Build the frontend and backend containers
2. Start Redis for task queuing
3. Launch Celery workers for background processing
4. Start all services with hot-reload enabled

### Access the Application

Once all services are running, open your browser to:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Testing Your Setup

### 1. Quick Functionality Test

1. Navigate to http://localhost:3000
2. Click "Upload Images" on the home page
3. Select one or more test images (JPG/PNG)
4. Set face limit to 10000 (default)
5. Click "Process Images"
6. Watch real-time progress updates
7. Download your generated 3D model (GLB format)

### 2. API Health Check

```bash
curl -X GET "http://localhost:8000/health" \
  -H "X-API-Key: your-api-key-here"
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-11T10:30:00Z"
}
```

### 3. Test File Upload

Use the provided test images:

```bash
# Frontend test images location
ls frontend-svelte/tests/fixtures/

# Backend test images location
ls tests/fixtures/
```

## Development Workflow

### Frontend Development

For frontend-only development with hot reload:

```bash
cd frontend-svelte
npm install
npm run dev
```

### Backend Development

For backend-only development:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Running Tests

```bash
# Frontend tests
cd frontend-svelte && npm test

# Backend tests
cd backend && pytest

# E2E tests
cd frontend-svelte && npm run test:e2e
```

## Common Commands

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Rebuild Services

```bash
# Rebuild specific service
docker compose build backend

# Rebuild all services
docker compose build
```

## Next Steps

Now that you have image2model running:

1. **Explore the Architecture**: Read the [Architecture Overview](./architecture-overview.md)
2. **Understand the API**: Check out the [API Documentation](http://localhost:8000/docs)
3. **Customize Settings**: See [Configuration Guide](../06-development/configuration/) (coming soon)
4. **Deploy to Production**: Follow the [Deployment Guide](../04-deployment/) (coming soon)

## Troubleshooting

### Issue: "Cannot connect to Docker daemon"

**Solution**: Ensure Docker Desktop is running

### Issue: "Port already in use"

**Solution**: Check for conflicting services:
```bash
# Find process using port 3000
lsof -i :3000

# Find process using port 8000
lsof -i :8000
```

### Issue: "FAL.AI API errors"

**Solution**: 
1. Verify your API key is correct in `.env`
2. Check your FAL.AI account has sufficient credits
3. Ensure you have internet connectivity

### Issue: "File upload fails"

**Solution**:
1. Check file format (only JPG/PNG supported)
2. Verify file size (max 10MB per file)
3. Ensure API key is set in requests

## Getting Help

- Check the [Architecture Overview](./architecture-overview.md) for system details
- Review [Common Errors](../07-reference/troubleshooting/common-errors.md) (coming soon)
- Search existing [GitHub Issues](https://github.com/your-org/image2model/issues)
- Ask in the development channel

---

**Success!** You should now have a working image2model development environment. Happy coding! 🚀
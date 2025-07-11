# Reference Documentation

> **Last Updated**: 2025-01-11  
> **Status**: Planned  
> **Version**: 0.1

Quick reference materials and troubleshooting guides for image2model.

## 📋 In This Section

### API

- **[OpenAPI Specification](./api/openapi-spec.md)** *(coming soon)* - Complete API documentation
- **[Postman Collection](./api/postman-collection.md)** *(coming soon)* - API testing collection

### Troubleshooting

- **[Common Errors](./troubleshooting/common-errors.md)** *(coming soon)* - Error solutions
- **[FAQ](./troubleshooting/faq.md)** *(coming soon)* - Frequently asked questions
- **[Known Issues](./troubleshooting/known-issues.md)** *(coming soon)* - Current limitations

### Reference

- **[Glossary](./glossary.md)** *(coming soon)* - Technical terms explained

## 🎯 Quick Links

### Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify endpoint URL |
| 413 | Payload Too Large | Reduce file size |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Check server logs |
| 502 | Bad Gateway | Backend unavailable |
| 503 | Service Unavailable | System overloaded |

### API Endpoints

#### Upload
```
POST /api/v1/upload/
Content-Type: multipart/form-data
Authorization: Bearer {API_KEY}
```

#### Status
```
GET /api/v1/status/tasks/{task_id}/stream
GET /api/v1/status/tasks/{task_id}
GET /api/v1/status/jobs/{job_id}/progress
```

#### Download
```
GET /api/v1/download/{job_id}/all
GET /api/v1/download/{job_id}/{filename}
GET /api/v1/download/direct/{filename}
```

## 🔍 Common Issues

### Upload Failures

#### "File too large"
**Cause**: File exceeds 10MB limit  
**Solution**: Compress or resize image before upload

#### "Invalid file type"
**Cause**: Non-image file or unsupported format  
**Solution**: Use JPG, JPEG, or PNG only

#### "Too many files"
**Cause**: More than 25 files selected  
**Solution**: Upload in batches of 25 or fewer

### Processing Errors

#### "FAL.AI API error"
**Cause**: External API failure  
**Solution**: 
- Check FAL.AI status
- Verify API key is valid
- Retry after a few minutes

#### "Task timeout"
**Cause**: Processing took too long  
**Solution**: 
- Try with smaller images
- Reduce face_limit parameter
- Contact support for large jobs

### Download Issues

#### "File not found"
**Cause**: File expired or doesn't exist  
**Solution**: 
- Files expire after 24 hours
- Regenerate if needed
- Check job_id is correct

#### "Access denied"
**Cause**: Invalid or missing authentication  
**Solution**: 
- Include API key in request
- Verify key hasn't expired

## 📖 Glossary

### A-F

**API Key**: Authentication token for API access

**Batch Processing**: Processing multiple images in one job

**Celery**: Python task queue for background jobs

**Docker**: Container platform for application deployment

**Face Limit**: Parameter controlling 3D model detail level

**FastAPI**: Modern Python web framework for APIs

### G-M

**GLB**: Binary 3D model file format

**Job ID**: Unique identifier for a batch processing job

**Middleware**: Software layer between frontend and backend

**Model**: In this context, a 3D representation of an object

### N-S

**Nginx**: Web server and reverse proxy

**Pydantic**: Data validation library for Python

**Redis**: In-memory data store used for queuing

**SSE**: Server-Sent Events for real-time updates

**SvelteKit**: Full-stack framework for Svelte apps

### T-Z

**Task ID**: Unique identifier for a processing task

**Tripo3D**: The AI model used for 3D generation

**Worker**: Background process that handles tasks

## 🛠️ Configuration Reference

### Environment Variables

```bash
# Required
API_KEY=              # Internal API authentication
FAL_AI_KEY=          # FAL.AI API key

# Optional
REDIS_URL=           # Default: redis://localhost:6379
LOG_LEVEL=           # Default: INFO
MAX_WORKERS=         # Default: 4
UPLOAD_LIMIT=        # Default: 10485760 (10MB)
BATCH_LIMIT=         # Default: 25
```

### Docker Compose Variables

```yaml
# Override defaults
FRONTEND_PORT: 5173
BACKEND_PORT: 8000
REDIS_PORT: 6379
WORKER_CONCURRENCY: 4
```

## 📊 Performance Benchmarks

### Processing Times

| Image Size | Average Time | Face Limit |
|------------|--------------|------------|
| < 1MB | 30-60s | Auto |
| 1-5MB | 60-120s | Auto |
| 5-10MB | 120-180s | Auto |
| < 1MB | 45-90s | 50000 |
| 1-5MB | 90-150s | 50000 |

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Frontend Memory | 512MB | 1GB |
| Backend Memory | 1GB | 2GB |
| Worker Memory | 2GB | 4GB |
| Redis Memory | 256MB | 512MB |
| Disk Space | 20GB | 50GB |

## 🔐 Security Reference

### API Authentication

All API requests require authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.yourdomain.com/api/v1/upload/
```

### CORS Configuration

Allowed origins:
- Production frontend URL
- Localhost for development
- Configured additional origins

### Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| Upload | 100 | 1 hour |
| Status | 1000 | 1 hour |
| Download | 500 | 1 hour |

## 🐛 Debug Commands

### Check Service Health

```bash
# Frontend
curl http://localhost:5173/health

# Backend
curl http://localhost:8000/health

# Redis
redis-cli ping

# Celery
celery -A app.core.celery_app inspect ping
```

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend

# Follow logs
docker-compose logs -f worker
```

### Monitor Resources

```bash
# Docker stats
docker stats

# Redis info
redis-cli info

# Celery stats
celery -A app.core.celery_app inspect stats
```

## 📚 Additional Resources

### Internal Docs

- [Getting Started](../01-getting-started/)
- [Development Guide](../06-development/)
- [API Documentation](../03-backend/api-reference/)

### External Links

- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [SvelteKit Troubleshooting](https://kit.svelte.dev/docs/troubleshooting)
- [Docker Debugging](https://docs.docker.com/config/containers/logging/)

### Support Channels

- GitHub Issues: Bug reports
- GitHub Discussions: Questions
- Email: support@yourdomain.com

---

**Need Help?** Can't find what you're looking for? Check the [FAQ](./troubleshooting/faq.md) or [Common Errors](./troubleshooting/common-errors.md).

*Reference documentation is continuously updated. Last review: 2025-01-11*
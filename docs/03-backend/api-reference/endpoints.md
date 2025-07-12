# API Endpoints Reference

## Overview

The Image2Model API provides endpoints for converting 2D images into 3D models using the FAL.AI Tripo3D service. All endpoints are versioned under `/api/v1/`.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Most endpoints require API key authentication. Include your API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Health Check

#### GET `/health`
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### GET `/health/ready`
Kubernetes readiness probe endpoint. Checks all service dependencies.

**Response:**
```json
{
  "status": "ready",
  "checks": {
    "redis": "connected",
    "fal_api": "reachable"
  }
}
```

### Upload

#### POST `/upload/batch`
Upload one or more images for 3D model generation.

**Request:**
- Content-Type: `multipart/form-data`
- Form fields:
  - `files`: Image files (max 25 files, max 10MB each)
  - `face_limit`: (optional) Maximum number of faces for the 3D model

**Supported formats:** JPG, JPEG, PNG

**Response:**
```json
{
  "job_id": "batch_20240315_123456_abc123",
  "session_id": "sess_xyz789",
  "files": [
    {
      "file_id": "file_001",
      "filename": "image1.jpg",
      "status": "pending"
    }
  ],
  "total_files": 1,
  "status": "processing"
}
```

### Model Generation

#### POST `/models/generate-single`
Generate a 3D model from a single uploaded image.

**Request:**
```json
{
  "job_id": "batch_20240315_123456_abc123",
  "file_id": "file_001",
  "face_limit": 10000
}
```

**Response:**
```json
{
  "job_id": "batch_20240315_123456_abc123",
  "file_id": "file_001",
  "model_task_id": "task_def456",
  "status": "processing"
}
```

### Status

#### GET `/status/{job_id}`
Get the status of a batch job.

**Response:**
```json
{
  "job_id": "batch_20240315_123456_abc123",
  "status": "processing",
  "total_files": 3,
  "processed_files": 1,
  "failed_files": 0,
  "progress": 33.33,
  "files": [
    {
      "file_id": "file_001",
      "filename": "image1.jpg",
      "status": "completed",
      "model_url": "https://fal.ai/models/...",
      "model_task_id": "task_def456"
    }
  ]
}
```

#### GET `/status/stream/{job_id}`
Server-Sent Events (SSE) endpoint for real-time status updates.

**Event Format:**
```
data: {"type": "progress", "job_id": "batch_...", "file_id": "file_001", "progress": 50}

data: {"type": "log", "job_id": "batch_...", "file_id": "file_001", "message": "Processing texture..."}

data: {"type": "completed", "job_id": "batch_...", "file_id": "file_001", "model_url": "https://..."}
```

### Download

#### GET `/download/{job_id}/{file_id}/model`
Download or redirect to the generated 3D model.

**Query Parameters:**
- `session_id`: (optional) Session ID for ownership verification

**Response:**
- If FAL.AI URL available: 302 redirect to model URL
- If local file: Binary GLB file download

#### GET `/download/{job_id}/all`
Download all models from a batch as a ZIP file.

**Response:**
- Content-Type: `application/zip`
- Contains all successfully generated GLB files

### Admin

#### GET `/admin/system-info`
Get system information (requires admin API key).

**Response:**
```json
{
  "system": {
    "platform": "linux",
    "cpu_count": 8,
    "memory": {
      "total": 16384,
      "available": 8192,
      "percent": 50.0
    },
    "disk": {
      "total": 1024000,
      "used": 512000,
      "free": 512000,
      "percent": 50.0
    }
  },
  "jobs": {
    "active": 5,
    "completed": 100,
    "failed": 2
  }
}
```

#### POST `/admin/cleanup`
Trigger manual cleanup of old files.

**Request:**
```json
{
  "older_than_hours": 24
}
```

**Response:**
```json
{
  "cleaned_files": 45,
  "freed_space_mb": 1024
}
```

### Logs

#### GET `/logs`
Retrieve application logs (requires admin API key).

**Query Parameters:**
- `lines`: Number of lines to return (default: 100)
- `level`: Log level filter (ERROR, WARNING, INFO, DEBUG)
- `since`: Timestamp to get logs from

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-03-15T10:30:00Z",
      "level": "INFO",
      "message": "Processing image file_001",
      "correlation_id": "req_123"
    }
  ],
  "total_lines": 100
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid file format",
    "details": {
      "file": "image.bmp",
      "allowed_formats": ["jpg", "jpeg", "png"]
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid API key |
| `INVALID_API_KEY` | 403 | API key is not authorized |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `FILE_TOO_LARGE` | 413 | File exceeds size limit |
| `PROCESSING_ERROR` | 500 | Internal processing error |
| `FAL_API_ERROR` | 502 | FAL.AI service error |

## Rate Limiting

Default rate limits:
- 60 requests per minute
- 1000 requests per hour

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1710500000
```
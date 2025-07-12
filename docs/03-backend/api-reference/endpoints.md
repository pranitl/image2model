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

#### GET `/api/v1/health/`
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "image2model-backend",
  "version": "1.0.0",
  "timestamp": "2024-03-15T10:30:00Z"
}
```

#### GET `/api/v1/health/detailed`
Comprehensive health check with system and component information.

**Response:**
```json
{
  "status": "healthy",
  "service": "image2model-backend",
  "version": "1.0.0",
  "timestamp": "2024-03-15T10:30:00Z",
  "system": {
    "platform": "Linux",
    "cpu_usage_percent": 25.5,
    "memory_usage_percent": 60.2,
    "disk_usage_percent": 45.0
  },
  "components": [
    {
      "name": "redis",
      "status": "healthy",
      "response_time_ms": 2.5
    },
    {
      "name": "celery",
      "status": "healthy", 
      "response_time_ms": 15.2
    }
  ],
  "uptime_seconds": 86400
}
```

#### GET `/api/v1/health/metrics`
Prometheus metrics endpoint.

**Response:**
- Content-Type: `text/plain; version=0.0.4; charset=utf-8`
- Returns metrics in Prometheus format

#### GET `/api/v1/health/liveness`
Kubernetes liveness probe endpoint.

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2024-03-15T10:30:00Z"
}
```

#### GET `/api/v1/health/readiness`
Kubernetes readiness probe endpoint. Checks all service dependencies.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2024-03-15T10:30:00Z",
  "components": [
    {"name": "celery", "status": "healthy"},
    {"name": "disk_space", "status": "healthy"}
  ]
}
```

### Upload

#### POST `/api/v1/upload/`
Upload one or more images for 3D model generation.

**Authentication:** Required

**Request:**
- Content-Type: `multipart/form-data`
- Form fields:
  - `files`: Image files (max 25 files, max 10MB each)
  - `face_limit`: (optional) Maximum number of faces for the 3D model

**Supported formats:** JPG, JPEG, PNG

**Response:**
```json
{
  "batch_id": "batch_20240315_123456_abc123",
  "job_id": "job_456",
  "task_id": "task_789",
  "uploaded_files": [
    {
      "file_id": "file_001",
      "filename": "image1.jpg",
      "file_size": 1048576,
      "content_type": "image/jpeg",
      "status": "uploaded"
    }
  ],
  "face_limit": 10000,
  "total_files": 1,
  "status": "uploaded",
  "message": "Files uploaded successfully, processing started"
}
```

#### GET `/api/v1/upload/status/{file_id}`
Get the status of an uploaded file.

**Parameters:**
- `file_id`: The unique identifier of the uploaded file

**Response:**
```json
{
  "file_id": "file_001",
  "status": "uploaded",
  "processing_status": "pending"
}
```

#### GET `/api/v1/upload/batch/{batch_id}/status`
Get the status of a batch upload job.

**Parameters:**
- `batch_id`: The batch identifier

**Response:**
```json
{
  "batch_id": "batch_20240315_123456_abc123",
  "status": "processing",
  "total_files": 3,
  "completed_files": 1,
  "failed_files": 0,
  "progress": 33.33
}
```

### Model Generation

#### POST `/api/v1/models/generate`
Generate a 3D model from a single uploaded image.

**Request:**
```json
{
  "file_id": "file_001",
  "model_type": "tripo3d",
  "quality": "standard",
  "texture_enabled": true
}
```

**Response:**
```json
{
  "job_id": "job_456",
  "status": "processing",
  "estimated_time": 120
}
```

#### GET `/api/v1/models/job/{job_id}`
Get the status of a 3D model generation job.

**Parameters:**
- `job_id`: The unique identifier of the generation job

**Response:**
```json
{
  "job_id": "job_456",
  "status": "completed",
  "progress": 100,
  "model_url": "https://fal.ai/models/generated_model.glb",
  "estimated_time_remaining": 0
}
```

#### GET `/api/v1/models/available`
Get list of available 3D model generation models.

**Response:**
```json
[
  {
    "name": "Tripo3D",
    "description": "AI-powered 3D model generation from single images",
    "type": "tripo3d",
    "supported_formats": ["glb", "obj"]
  }
]
```

#### GET `/api/v1/models/download/{job_id}`
Download the generated 3D model.

**Parameters:**
- `job_id`: The job identifier
- `format`: (query) The desired model format (obj, ply, stl) - default: obj

**Response:**
- Binary file download of the 3D model

### Status

#### GET `/api/v1/status/jobs/{job_id}/progress`
Get aggregated progress for a parallel batch job.

**Parameters:**
- `job_id`: The job identifier

**Response:**
```json
{
  "job_id": "job_456",
  "overall_progress": 33.33,
  "total_files": 3,
  "completed_files": 1,
  "failed_files": 0,
  "files": {
    "file_001": {
      "status": "completed",
      "progress": 100,
      "filename": "image1.jpg"
    }
  }
}
```

#### GET `/api/v1/status/tasks/{task_id}/stream`
Stream real-time progress updates for a specific Celery task via Server-Sent Events.

**Parameters:**
- `task_id`: The Celery task ID to monitor
- `timeout`: (query) Maximum time in seconds to keep connection alive (default: 3600)

**Response:**
- Content-Type: `text/event-stream`

**Event Format:**
```
data: {"type": "progress", "task_id": "task_123", "progress": 50, "status": "processing"}

data: {"type": "log", "task_id": "task_123", "message": "Processing texture..."}

data: {"type": "completed", "task_id": "task_123", "result": "success", "model_url": "https://..."}

data: {"type": "error", "task_id": "task_123", "error": "Processing failed"}
```

#### GET `/api/v1/status/tasks/{task_id}/status`
Get current status of a specific Celery task (non-streaming endpoint).

**Parameters:**
- `task_id`: The Celery task ID to check

**Response:**
```json
{
  "task_id": "task_123",
  "status": "processing",
  "progress": 75,
  "result": null,
  "error": null,
  "timestamp": "2024-03-15T10:30:00Z"
}
```

### Download

#### GET `/api/v1/download/{job_id}/{filename}`
Download a single 3D model file from a completed job.

**Authentication:** Required

**Parameters:**
- `job_id`: Unique job identifier
- `filename`: Name of the file to download

**Response:**
- Binary file download (GLB, OBJ, etc.)

#### GET `/api/v1/download/{job_id}/all`
List all available files for a specific job with download URLs.

**Parameters:**
- `job_id`: Unique job identifier

**Response:**
```json
{
  "job_id": "job_456",
  "files": [
    {
      "filename": "model.glb",
      "size": 1048576,
      "mime_type": "model/gltf-binary",
      "created_time": 1710500000,
      "rendered_image": null
    }
  ],
  "download_urls": [
    "/api/v1/download/job_456/model.glb"
  ],
  "total_files": 1
}
```

#### GET `/api/v1/download/direct/{filename}`
Download a file directly by filename from the results directory.

**Parameters:**
- `filename`: Name of the file to download

**Response:**
- Binary file download

#### GET `/api/v1/debug/job/{job_id}`
Debug endpoint to check job store connectivity and data.

**Parameters:**
- `job_id`: Job ID to debug

**Response:**
```json
{
  "job_id": "job_456",
  "found": true,
  "files": ["model.glb"],
  "metadata": {
    "created": "2024-03-15T10:30:00Z",
    "status": "completed"
  }
}
```

### Admin

**Authentication:** Admin API key required for all admin endpoints

#### GET `/api/v1/admin/disk-usage`
Get current disk usage statistics for upload and output directories.

**Response:**
```json
{
  "upload_dir": {
    "total_gb": 100.0,
    "used_gb": 25.5,
    "free_gb": 74.5,
    "usage_percent": 25.5
  },
  "output_dir": {
    "total_gb": 500.0,
    "used_gb": 125.0,
    "free_gb": 375.0,
    "usage_percent": 25.0
  },
  "timestamp": "2024-03-15T10:30:00Z"
}
```

#### POST `/api/v1/admin/cleanup`
Trigger manual cleanup of old files.

**Request:**
```json
{
  "hours": 24,
  "dry_run": false
}
```

**Response:**
```json
{
  "freed_space_mb": 1024.5,
  "files_removed": 45,
  "directories_removed": 3,
  "errors": [],
  "cleanup_hours": 24,
  "timestamp": "2024-03-15T10:30:00Z"
}
```

#### POST `/api/v1/admin/cleanup-job`
Clean up files for a specific job ID.

**Request:**
```json
{
  "job_id": "job_456"
}
```

**Response:**
```json
{
  "job_id": "job_456",
  "files_removed": 3,
  "space_freed_mb": 15.2,
  "status": "success"
}
```

#### GET `/api/v1/admin/list-files`
List files in a specific directory with size and modification information.

**Query Parameters:**
- `directory`: Directory to list ('uploads' or 'results') - required
- `limit`: Maximum number of items to return (default: 100)

**Response:**
```json
{
  "directory": "uploads",
  "total_size_mb": 256.7,
  "total_files": 150,
  "items": [
    {
      "path": "image1.jpg",
      "size_mb": 2.5,
      "modified": "2024-03-15T10:30:00Z",
      "is_directory": false,
      "file_count": null
    }
  ]
}
```

#### DELETE `/api/v1/admin/delete-job/{job_id}`
Delete all files associated with a specific job ID.

**Parameters:**
- `job_id`: The job ID whose files should be deleted

**Response:**
```json
{
  "job_id": "job_456",
  "files_deleted": 5,
  "space_freed_mb": 25.8,
  "status": "success"
}
```

#### GET `/api/v1/admin/system-health`
Get overall system health including disk usage and cleanup status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-03-15T10:30:00Z",
  "disk_usage": {
    "uploads_gb": 25.5,
    "results_gb": 125.0,
    "logs_gb": 5.2
  },
  "cleanup_status": {
    "last_run": "2024-03-15T09:00:00Z",
    "files_cleaned": 45,
    "space_freed_mb": 1024.5
  }
}
```

### Logs

**Authentication:** Admin API key required for all log endpoints

#### GET `/api/v1/logs/statistics`
Get comprehensive statistics about log files.

**Response:**
```json
{
  "total_files": 15,
  "total_size_mb": 125.5,
  "oldest_file": "2024-03-01T10:00:00Z",
  "newest_file": "2024-03-15T10:30:00Z",
  "by_type": {
    "celery_worker": 8,
    "celery_errors": 2,
    "application": 5
  },
  "log_directory": "/app/logs",
  "disk_usage": {
    "used_mb": 125.5,
    "available_mb": 1024.0
  }
}
```

#### POST `/api/v1/logs/rotate`
Manually trigger log rotation for all log files that need it.

**Response:**
```json
{
  "rotated_files": [
    "celery_worker.log",
    "application.log"
  ],
  "skipped_files": [
    "celery_worker.log.1"
  ],
  "errors": []
}
```

#### DELETE `/api/v1/logs/cleanup`
Clean up old log files beyond the retention period.

**Query Parameters:**
- `older_than_days`: Remove logs older than this many days (default: 30, max: 365)

**Response:**
```json
{
  "status": "success",
  "removed_files": 8,
  "total_size_removed_mb": 45.2,
  "errors": []
}
```

#### GET `/api/v1/logs/analyze`
Analyze log patterns for insights and anomalies.

**Query Parameters:**
- `log_type`: Type of log to analyze (default: "celery_worker")
- `hours_back`: Hours back to analyze (default: 24, max: 168)

**Response:**
```json
{
  "time_range": {
    "start": "2024-03-14T10:30:00Z",
    "end": "2024-03-15T10:30:00Z"
  },
  "log_levels": {
    "ERROR": 5,
    "WARNING": 15,
    "INFO": 1250,
    "DEBUG": 3500
  },
  "error_patterns": {
    "Connection timeout": 3,
    "Processing failed": 2
  },
  "request_patterns": {
    "/api/v1/upload": 145,
    "/api/v1/models/generate": 78
  },
  "performance_metrics": {
    "avg_response_time_ms": 245,
    "max_response_time_ms": 2500
  },
  "lines_analyzed": 4770
}
```

#### GET `/api/v1/logs/summary/daily`
Get daily log summary for analysis.

**Query Parameters:**
- `date`: Date in YYYY-MM-DD format (default: today)

**Response:**
```json
{
  "date": "2024-03-15",
  "total_entries": 4770,
  "error_count": 5,
  "warning_count": 15,
  "top_endpoints": [
    {
      "endpoint": "/api/v1/upload",
      "count": 145
    }
  ],
  "error_summary": [
    "Connection timeout (3)",
    "Processing failed (2)"
  ]
}
```

#### GET `/api/v1/logs/types`
Get available log types for analysis.

**Response:**
```json
{
  "types": [
    "celery_worker",
    "celery_errors", 
    "application",
    "access"
  ],
  "descriptions": {
    "celery_worker": "Celery worker process logs",
    "celery_errors": "Celery error logs",
    "application": "Main application logs",
    "access": "HTTP access logs"
  }
}
```

#### POST `/api/v1/logs/export`
Export logs for a date range (background task).

**Query Parameters:**
- `start_date`: Start date in YYYY-MM-DD format - required
- `end_date`: End date in YYYY-MM-DD format - required
- `log_types`: Comma-separated log types (optional)
- `format`: Export format (json, csv, txt) - default: json

**Response:**
```json
{
  "export_id": "export_456",
  "status": "started",
  "estimated_completion": "2024-03-15T10:35:00Z",
  "download_url": "/api/v1/logs/export/export_456/download"
}
```

#### GET `/api/v1/logs/health`
Check the health of the logging system.

**Response:**
```json
{
  "status": "healthy",
  "log_directory_writable": true,
  "disk_space_available": true,
  "rotation_working": true,
  "recent_errors": 0,
  "last_log_entry": "2024-03-15T10:30:00Z"
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
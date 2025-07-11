# API Endpoints Mapping

This document maps the actual implemented endpoints in the backend API.

## Health Endpoints (`/api/v1/health`)
- `GET /` - Basic health check
- `GET /detailed` - Detailed health status
- `GET /metrics` - System metrics
- `GET /liveness` - Kubernetes liveness probe
- `GET /readiness` - Kubernetes readiness probe

## Upload Endpoints (`/api/v1/upload`)
- `POST /` - Batch file upload
- `GET /status/{file_id}` - Get upload status
- `GET /batch/{batch_id}/status` - Get batch upload status

## Models Endpoints (`/api/v1/models`)
- `POST /generate` - Generate 3D model
- `GET /job/{job_id}` - Get job status
- `GET /available` - List available model types
- `GET /download/{job_id}` - Download model file

## Status Endpoints (`/api/v1/status`)
- `GET /tasks/{task_id}/stream` - SSE stream for task status
- `GET /tasks/{task_id}/status` - Get task status
- `GET /jobs/{job_id}/progress` - Get job progress

## Download Endpoints (`/api/v1`)
- `GET /download/direct/{filename}` - Direct file download
- `GET /download/{job_id}/all` - Download all files for job
- `GET /download/{job_id}/{filename}` - Download specific file for job
- `GET /debug/job/{job_id}` - Debug job information

## Admin Endpoints (`/api/v1/admin`)
- `GET /disk-usage` - Get disk usage statistics
- `POST /cleanup` - Trigger file cleanup
- `POST /cleanup-job` - Clean up specific job files
- `GET /list-files?directory={uploads|results}` - List files in directory (requires directory param)
- `DELETE /delete-job/{job_id}` - Delete job files
- `GET /system-health` - Get system health status

## Logs Endpoints (`/api/v1/logs`)
- `GET /statistics` - Get log statistics
- `POST /rotate` - Rotate log files
- `DELETE /cleanup` - Clean up old logs
- `GET /analyze` - Analyze log patterns
- `GET /summary/daily` - Get daily log summary (NOT /daily-summary)
- `GET /types` - Get available log types
- `POST /export` - Export logs
- `GET /health` - Log system health

## Notes

1. **Authentication**: 
   - Regular endpoints use `X-API-Key` header
   - Admin endpoints use `X-Admin-Key` header

2. **Missing Endpoints**:
   - No `/upload/url` endpoint for URL-based uploads
   - No direct image upload endpoint (uses batch upload)

3. **SSE Endpoints**:
   - `/status/tasks/{task_id}/stream` provides Server-Sent Events

4. **Parameter Requirements**:
   - `/admin/list-files` requires `directory` query parameter (values: "uploads" or "results")
   - Many endpoints require specific IDs (task_id, job_id, etc.)
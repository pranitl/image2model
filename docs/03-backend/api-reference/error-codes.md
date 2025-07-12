# Error Codes and Responses

## Overview

The Image2Model API uses a consistent error response format across all endpoints. This guide documents all error codes, their meanings, and how to handle them.

## Error Response Format

All errors follow this standard format:

```json
{
  "error": true,
  "error_code": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "additional": "context-specific information"
  }
}
```

## Error Code Reference

### Authentication Errors (4xx)

#### AUTHENTICATION_REQUIRED
- **HTTP Status**: 500 Internal Server Error
- **Description**: Request requires authentication but no API key provided
- **Example**:
```json
{
  "error": true,
  "error_code": "AUTHENTICATION_REQUIRED",
  "message": "API key not configured"
}
```

#### INVALID_API_KEY
- **HTTP Status**: 403 Forbidden
- **Description**: Provided API key is invalid or revoked
- **Example**:
```json
{
  "error": true,
  "error_code": "INVALID_API_KEY",
  "message": "Invalid API key"
}
```

#### INSUFFICIENT_PERMISSIONS
- **HTTP Status**: 403 Forbidden
- **Description**: API key lacks required permissions (e.g., admin access)
- **Example**:
```json
{
  "error": true,
  "error_code": "INSUFFICIENT_PERMISSIONS",
  "message": "Invalid admin API key"
}
```

### Validation Errors (4xx)

#### VALIDATION_ERROR
- **HTTP Status**: 400 Bad Request
- **Description**: Request parameters failed validation
- **Example**:
```json
{
  "error": true,
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid file format",
  "details": {
    "file": "image.bmp",
    "allowed_formats": ["jpg", "jpeg", "png"]
  }
}
```

#### FILE_TOO_LARGE
- **HTTP Status**: 413 Payload Too Large
- **Description**: Uploaded file exceeds size limit
- **Example**:
```json
{
  "error": true,
  "error_code": "FILE_TOO_LARGE",
  "message": "File size exceeds 10MB limit",
  "details": {
    "file_size": 15728640,
    "max_size": 10485760
  }
}
```

#### TOO_MANY_FILES
- **HTTP Status**: 400 Bad Request
- **Description**: Batch upload exceeds file count limit
- **Example**:
```json
{
  "detail": {
    "code": "TOO_MANY_FILES",
    "message": "Maximum 25 files allowed per batch",
    "details": {
      "provided": 30,
      "limit": 25
    }
  }
}
```

#### INVALID_JOB_ID
- **HTTP Status**: 400 Bad Request
- **Description**: Job ID format is invalid
- **Example**:
```json
{
  "detail": {
    "code": "INVALID_JOB_ID",
    "message": "Invalid job ID format",
    "details": {
      "job_id": "invalid@id",
      "pattern": "^[a-zA-Z0-9_-]+$"
    }
  }
}
```

### Resource Errors (4xx)

#### JOB_NOT_FOUND
- **HTTP Status**: 404 Not Found
- **Description**: Requested job does not exist
- **Example**:
```json
{
  "detail": {
    "code": "JOB_NOT_FOUND",
    "message": "Job not found",
    "details": {
      "job_id": "batch_20240315_123456_abc123"
    }
  }
}
```

#### FILE_NOT_FOUND
- **HTTP Status**: 404 Not Found
- **Description**: Requested file does not exist in job
- **Example**:
```json
{
  "detail": {
    "code": "FILE_NOT_FOUND",
    "message": "File not found in job",
    "details": {
      "job_id": "batch_20240315_123456_abc123",
      "file_id": "file_999"
    }
  }
}
```

#### MODEL_NOT_READY
- **HTTP Status**: 404 Not Found
- **Description**: 3D model not yet generated
- **Example**:
```json
{
  "detail": {
    "code": "MODEL_NOT_READY",
    "message": "Model generation still in progress",
    "details": {
      "status": "processing",
      "progress": 75
    }
  }
}
```

### Rate Limiting Errors (4xx)

#### RATE_LIMIT_EXCEEDED
- **HTTP Status**: 429 Too Many Requests
- **Description**: API rate limit exceeded
- **Headers**:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp
- **Example**:
```json
{
  "detail": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 60,
      "window": "1 minute",
      "retry_after": 45
    }
  }
}
```

### Processing Errors (5xx)

#### PROCESSING_ERROR
- **HTTP Status**: 500 Internal Server Error
- **Description**: General processing error
- **Example**:
```json
{
  "detail": {
    "code": "PROCESSING_ERROR",
    "message": "Failed to process image",
    "details": {
      "error": "Internal processing error",
      "correlation_id": "req_abc123"
    }
  }
}
```

#### FAL_API_ERROR
- **HTTP Status**: 502 Bad Gateway
- **Description**: Error from FAL.AI service
- **Example**:
```json
{
  "detail": {
    "code": "FAL_API_ERROR",
    "message": "External service error",
    "details": {
      "service": "fal.ai",
      "error": "Model generation failed"
    }
  }
}
```

#### FAL_RATE_LIMIT
- **HTTP Status**: 503 Service Unavailable
- **Description**: FAL.AI rate limit reached
- **Example**:
```json
{
  "detail": {
    "code": "FAL_RATE_LIMIT",
    "message": "External service rate limit",
    "details": {
      "retry_after": 60,
      "service": "fal.ai"
    }
  }
}
```

#### STORAGE_ERROR
- **HTTP Status**: 507 Insufficient Storage
- **Description**: Storage space exhausted
- **Example**:
```json
{
  "error": true,
  "error_code": "STORAGE_ERROR",
  "message": "Insufficient storage space",
  "details": {
    "required": 1048576,
    "available": 524288
  }
}
```

### Custom Application Errors (5xx)

#### APIEXCEPTION
- **HTTP Status**: 500 Internal Server Error
- **Description**: General API-related errors
- **Example**:
```json
{
  "error": true,
  "error_code": "APIEXCEPTION",
  "message": "API operation failed"
}
```

#### FALAPIEXCEPTION
- **HTTP Status**: 502 Bad Gateway
- **Description**: FAL.AI API service errors
- **Example**:
```json
{
  "error": true,
  "error_code": "FALAPIEXCEPTION",
  "message": "External FAL.AI service error",
  "details": {
    "service": "fal.ai",
    "error": "Model generation failed"
  }
}
```

#### DATABASEEXCEPTION
- **HTTP Status**: 500 Internal Server Error
- **Description**: Database operation failures
- **Example**:
```json
{
  "error": true,
  "error_code": "DATABASEEXCEPTION",
  "message": "Database operation failed"
}
```

#### PROCESSINGEXCEPTION
- **HTTP Status**: 500 Internal Server Error
- **Description**: Image or model processing failures
- **Example**:
```json
{
  "error": true,
  "error_code": "PROCESSINGEXCEPTION",
  "message": "Failed to process image"
}
```

#### NETWORKEXCEPTION
- **HTTP Status**: 503 Service Unavailable
- **Description**: Network-related errors
- **Example**:
```json
{
  "error": true,
  "error_code": "NETWORKEXCEPTION",
  "message": "Network connectivity issue"
}
```

#### MODELEXCEPTION
- **HTTP Status**: 500 Internal Server Error
- **Description**: Model operation failures
- **Example**:
```json
{
  "error": true,
  "error_code": "MODELEXCEPTION",
  "message": "Model operation failed"
}
```

#### CONFIGURATIONEXCEPTION
- **HTTP Status**: 500 Internal Server Error
- **Description**: Configuration-related errors
- **Example**:
```json
{
  "error": true,
  "error_code": "CONFIGURATIONEXCEPTION",
  "message": "Invalid configuration"
}
```

## Error Handling Best Practices

### Client-Side Handling

```python
import requests
from time import sleep

def api_request_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            
            error = response.json()
            error_code = error['detail']['code']
            
            # Handle specific errors
            if error_code == 'RATE_LIMIT_EXCEEDED':
                retry_after = error['detail']['details'].get('retry_after', 60)
                sleep(retry_after)
                continue
                
            elif error_code == 'FAL_RATE_LIMIT':
                # External service rate limit - wait longer
                sleep(120)
                continue
                
            elif error_code in ['AUTHENTICATION_REQUIRED', 'INVALID_API_KEY']:
                # Authentication errors - don't retry
                raise Exception(f"Authentication error: {error['detail']['message']}")
                
            elif response.status_code >= 500:
                # Server errors - retry with backoff
                sleep(2 ** attempt)
                continue
                
            else:
                # Client errors - don't retry
                raise Exception(f"Client error: {error['detail']['message']}")
                
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            sleep(2 ** attempt)
    
    raise Exception("Max retries exceeded")
```

### Error Recovery Strategies

#### Validation Errors
- Validate inputs before sending requests
- Provide clear feedback to users
- Don't retry - fix the input

#### Rate Limiting
- Implement exponential backoff
- Respect retry-after headers
- Consider request queuing

#### Processing Errors
- Retry with exponential backoff
- Log correlation IDs for debugging
- Implement circuit breakers

#### Authentication Errors
- Prompt for new credentials
- Clear cached tokens
- Don't retry with same credentials

## Correlation IDs

All errors include a correlation ID for tracking:

```json
{
  "detail": {
    "code": "PROCESSING_ERROR",
    "message": "Internal error",
    "correlation_id": "req_abc123xyz"
  }
}
```

Use correlation IDs when:
- Reporting issues to support
- Searching logs
- Debugging complex workflows

## WebSocket/SSE Error Events

For streaming endpoints, errors are sent as events:

```
event: error
data: {"code": "PROCESSING_ERROR", "message": "Failed to generate model", "file_id": "file_001"}

event: close
data: {"reason": "error"}
```

## Common Error Scenarios

### Scenario 1: File Upload Validation
```
Client uploads unsupported file format
→ 400 VALIDATION_ERROR
→ Show supported formats to user
→ Allow retry with correct format
```

### Scenario 2: Model Generation Failure
```
FAL.AI fails to generate model
→ 502 FAL_API_ERROR
→ Retry automatically (up to 3 times)
→ If still failing, mark as failed
→ Allow manual retry later
```

### Scenario 3: Concurrent Request Limit
```
Too many simultaneous requests
→ 429 RATE_LIMIT_EXCEEDED
→ Queue requests client-side
→ Retry after indicated time
→ Implement request throttling
```
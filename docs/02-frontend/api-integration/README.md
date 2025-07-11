# API Integration Documentation

> **Last Updated**: 2025-01-11  
> **Status**: Complete  
> **Version**: 1.0

## Overview

This directory contains comprehensive documentation for the API integration layer of the image2model SvelteKit frontend. It covers how the frontend communicates with the backend API, handles real-time updates via Server-Sent Events (SSE), and manages errors gracefully.

## Documentation Structure

### Core Documentation

1. **[API Service](./api-service.md)**
   - Central API communication hub
   - Authentication and request handling
   - File upload and download methods
   - Retry logic implementation

2. **[SSE Handling](./sse-handling.md)**
   - Real-time progress updates
   - Event stream management
   - Connection lifecycle
   - Event type specifications

3. **[Error Handling](./error-handling.md)**
   - Error categories and patterns
   - Recovery strategies
   - User feedback mechanisms
   - Validation and retry logic

## Quick Start

### Basic API Usage

```javascript
import api from '$lib/services/api';
import { apiKey } from '$lib/stores/auth';

// Set API key
api.setApiKey($apiKey);

// Upload files
const result = await api.uploadBatch(files, faceLimit);

// Track progress
const stream = api.createProgressStream(taskId, {
  onProgress: (data) => console.log(`${data.progress}% complete`),
  onComplete: (data) => console.log('Done!', data)
});
```

### Error Handling Pattern

```javascript
import { toast } from '$lib/stores/toast';

try {
  const result = await api.someOperation();
  if (result.success) {
    // Handle success
  } else {
    throw new Error(result.error);
  }
} catch (error) {
  toast.error(`Operation failed: ${error.message}`);
}
```

## Key Concepts

### API Service Singleton

The API service is implemented as a singleton to ensure consistent configuration and authentication across the application:

```javascript
// Always import the singleton instance
import api from '$lib/services/api';
```

### Authentication Flow

1. API key is loaded from environment or configuration
2. Stored in the auth store
3. Applied to API service before requests
4. Included in all request headers as Bearer token

### Real-time Updates

SSE provides unidirectional server-to-client communication for progress tracking:

- Automatic reconnection on connection loss
- Multiple event types for granular updates
- Proper cleanup in component lifecycle

### Error Recovery

Comprehensive error handling ensures resilient operation:

- Automatic retry for transient failures
- Exponential backoff to prevent overwhelming the server
- User-friendly error messages
- Data preservation during errors

## Common Patterns

### File Upload with Progress

```javascript
// Upload files and navigate to processing
async function uploadAndProcess(files) {
  const result = await api.uploadBatch(files, faceLimit);
  
  if (result.success) {
    // Store file info for processing page
    sessionStorage.setItem('processingFiles', JSON.stringify({
      files: files.map(f => f.name),
      taskId: result.taskId
    }));
    
    // Navigate to processing
    await goto(`/processing?taskId=${result.taskId}`);
  }
}
```

### SSE Connection Management

```javascript
import { onMount, onDestroy } from 'svelte';

let stream;

onMount(() => {
  stream = api.createProgressStream(taskId, callbacks);
});

onDestroy(() => {
  stream?.close();
});
```

### Retry with Backoff

```javascript
const result = await api.retryOperation(
  () => api.uploadBatch(files, faceLimit),
  3,    // max attempts
  1000  // initial delay
);
```

## Architecture Decisions

### Why SSE over WebSockets?

- Simpler implementation for unidirectional updates
- Built-in reconnection handling
- Works over standard HTTP
- No additional protocol overhead

### Why Singleton API Service?

- Centralized configuration
- Consistent authentication
- Easier testing and mocking
- Reduced code duplication

### Error Handling Philosophy

- Fail gracefully with user feedback
- Preserve user data during failures
- Automatic recovery where possible
- Clear guidance for resolution

## Testing Considerations

### Mocking the API Service

```javascript
// Mock for testing
const mockApi = {
  uploadBatch: jest.fn().mockResolvedValue({ success: true, taskId: '123' }),
  createProgressStream: jest.fn().mockReturnValue({
    close: jest.fn(),
    readyState: jest.fn().mockReturnValue(1)
  })
};
```

### Testing Error Scenarios

```javascript
// Test error handling
it('should handle upload failure', async () => {
  api.uploadBatch.mockRejectedValue(new Error('Network error'));
  
  const result = await uploadFiles(files);
  
  expect(toast.error).toHaveBeenCalledWith(
    expect.stringContaining('Network error')
  );
});
```

## Performance Considerations

### Connection Management

- Reuse SSE connections when possible
- Close connections promptly when done
- Implement connection pooling for multiple tasks

### Error Retry Optimization

- Exponential backoff prevents server overload
- Max retry limits prevent infinite loops
- Skip retry for non-transient errors

### Memory Management

- Clean up object URLs after use
- Close event streams in cleanup
- Clear large data from session storage

## Security Notes

### API Key Handling

- Never expose API keys in client code
- Use environment variables for configuration
- Implement key rotation strategy
- Monitor for unauthorized usage

### Input Validation

- Validate file types and sizes client-side
- Sanitize error messages from server
- Prevent injection via file names
- Limit batch sizes to prevent DoS

## Related Documentation

- [Frontend Architecture](../architecture/README.md) - Overall frontend structure
- [Component Documentation](../components/README.md) - UI component reference
- [Backend API Reference](../../03-backend/api-reference/README.md) - Server API documentation
- [Testing Guide](../../05-testing/frontend-testing/README.md) - Frontend testing strategies
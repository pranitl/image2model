# Celery Worker Testing Guide

This document provides instructions for testing the Celery worker configuration implemented in Task 6.

## Prerequisites

1. **Redis Server**: Ensure Redis is running on localhost:6379
   ```bash
   # Install Redis (macOS)
   brew install redis
   
   # Start Redis
   redis-server
   
   # Or start as a service
   brew services start redis
   ```

2. **Python Dependencies**: Ensure all requirements are installed
   ```bash
   pip install -r requirements.txt
   ```

## Configuration Tests

Run the configuration tests to verify the Celery setup:

```bash
cd backend
python test_celery_config.py
```

This will test:
- ✅ Redis connection
- ✅ Celery app configuration
- ✅ Task registration
- ✅ Logging configuration
- ✅ Worker startup script
- ✅ Task signature creation
- ✅ Directory creation

## Task Unit Tests

Run the task unit tests:

```bash
cd backend
python test_tasks.py
```

This will test:
- ✅ Individual task functions
- ✅ Task retry mechanisms
- ✅ Task metadata and binding
- ✅ Logging in tasks
- ✅ Task time limits

## Starting the Worker

Once Redis is running, you can start the Celery worker:

```bash
cd backend
python start_worker.py
```

Or manually with celery command:

```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info --concurrency=2
```

## Testing Task Execution

With the worker running, you can test task execution from a Python shell:

```python
# In a Python shell or script
from app.core.celery_app import celery_app

# Test health check
result = celery_app.send_task('app.workers.tasks.health_check_task')
print(f"Health check result: {result.get()}")

# Test batch processing (with dummy data)
job_id = "test_job_123"
file_paths = ["/path/to/test/image1.jpg", "/path/to/test/image2.jpg"]
result = celery_app.send_task('app.workers.tasks.process_batch', 
                             args=[job_id, file_paths])

# Monitor progress
while not result.ready():
    state = result.state
    if state == 'PROGRESS':
        info = result.info
        print(f"Progress: {info.get('current', 0)}/{info.get('total', 0)} - {info.get('status', 'Processing...')}")
    time.sleep(1)

# Get final result
final_result = result.get()
print(f"Batch processing result: {final_result}")
```

## Monitoring

### Queue Monitoring

Check Redis queues:

```bash
redis-cli
> KEYS celery*
> LLEN celery
```

### Worker Logs

Worker logs are stored in:
- `logs/celery_worker.log` - All worker logs (JSON format)
- `logs/celery_errors.log` - Error logs only (JSON format)
- Console output - Formatted logs

### Task States

Celery tasks support these states:
- `PENDING` - Task is waiting for execution
- `PROGRESS` - Task is currently being executed
- `SUCCESS` - Task executed successfully
- `FAILURE` - Task execution failed
- `RETRY` - Task is being retried

## Performance Testing

For performance testing, you can use:

```python
# Test concurrent task execution
from celery import group
from app.core.celery_app import celery_app

# Create a group of tasks
job = group(
    celery_app.signature('app.workers.tasks.health_check_task')
    for i in range(10)
)

# Execute all tasks
result = job.apply_async()

# Wait for completion
results = result.get()
print(f"Completed {len(results)} tasks")
```

## Error Testing

Test error handling and retries:

```python
# This would cause the process_batch task to fail and retry
result = celery_app.send_task('app.workers.tasks.process_batch', 
                             args=["test_job", ["/nonexistent/file.jpg"]])

# Monitor retries in the logs
```

## Configuration Details

### Task Queues

The worker is configured with these queues:
- `default` - General tasks
- `batch_processing` - Batch processing tasks
- `model_generation` - 3D model generation tasks
- `maintenance` - Cleanup and maintenance tasks
- `priority` - High priority tasks

### Time Limits

- **Hard limit**: 30 minutes (1800 seconds)
- **Soft limit**: 25 minutes (1500 seconds)

### Retry Policy

- **Max retries**: 3
- **Countdown**: 60 seconds between retries
- **Autoretry on**: Any Exception

### Worker Settings

- **Concurrency**: 2 processes
- **Pool**: prefork
- **Max tasks per child**: 1000
- **Max memory per child**: 200MB

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```
   Error 61 connecting to localhost:6379. Connection refused.
   ```
   Solution: Start Redis server

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'app'
   ```
   Solution: Run from the backend directory

3. **Permission Errors**
   ```
   Permission denied: logs/celery_worker.log
   ```
   Solution: Ensure proper write permissions for logs directory

### Debugging

1. **Enable debug logging**:
   ```bash
   celery -A app.core.celery_app worker --loglevel=debug
   ```

2. **Check task registration**:
   ```python
   from app.core.celery_app import celery_app
   print(list(celery_app.tasks.keys()))
   ```

3. **Monitor with Flower** (optional):
   ```bash
   pip install flower
   celery -A app.core.celery_app flower
   ```
   Then open http://localhost:5555

## Task 7 Integration

This Celery worker configuration is designed to integrate with Task 7 (FAL.AI API integration). The `process_single_image` function in `app/workers/tasks.py` is prepared to be enhanced with actual FAL.AI API calls.

When Task 7 is implemented, the placeholder processing in `process_single_image` will be replaced with real FAL.AI API calls to generate 3D models from images.
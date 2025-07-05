# Celery worker not processing tasks - missing queue configuration

## Issue Description

Tasks are being queued but not processed by the Celery worker. Through live validation, I confirmed that tasks are accumulating in custom queues without being processed.

## Root Cause Analysis

The Celery configuration in `backend/app/core/celery_app.py` defines multiple queues for task routing:
- `default`
- `batch_processing` 
- `model_generation`
- `maintenance`
- `priority`

However, the worker command in `docker compose.yml` doesn't specify which queues to listen to:
```bash
celery -A app.core.celery_app worker --loglevel=info --concurrency=2
```

When no queues are specified, Celery workers only listen to the `default` queue, not the custom queues defined in the configuration.

## Live Validation Results

1. **Test Upload**: Successfully uploaded test image
   - File ID: `98b8016c-0018-4c00-8bb6-f9572fe37dc6`
   - Response: File uploaded successfully

2. **3D Model Generation Request**: 
   - Job ID: `554cc4cd-cfc4-48b3-92de-f47d1cd91d0e`
   - Status: `queued`
   - Task remains in PENDING state indefinitely

3. **Worker Queue Analysis**:
   - Worker logs show: `[queues] .> default exchange=default(direct) key=default`
   - Worker is ONLY listening to the `default` queue

4. **Redis Queue Inspection**:
   - `model_generation` queue: **3 tasks stuck**
   - `priority` queue: **1 task stuck**
   - These tasks are not being processed

## Impact

- Tasks like `generate_3d_model_task` (routed to `model_generation` queue) are never processed
- Batch processing tasks (routed to `batch_processing` queue) won't be processed
- Maintenance tasks (routed to `maintenance` queue) won't be processed
- Users experience indefinite "queued" status for their jobs

## Solution

Update the worker command in `docker compose.yml` (line 104) to specify all queues:

```bash
celery -A app.core.celery_app worker --loglevel=info --concurrency=2 -Q default,batch_processing,model_generation,maintenance,priority
```

## Alternative Solutions

1. **Multiple Workers**: Run separate workers for different queue types with different concurrency settings:
   ```yaml
   worker-models:
     command: celery -A app.core.celery_app worker -Q model_generation --concurrency=4
   
   worker-batch:
     command: celery -A app.core.celery_app worker -Q batch_processing --concurrency=2
   ```

2. **Environment-based Configuration**: Use environment variables to configure queues dynamically

## Files Affected

- `/docker compose.yml` (line 104)
- `/docker compose.prod.yml` (if production config exists)
- `/docker compose.override.yml` (if override config exists)
- Any deployment scripts that start Celery workers

## Verification Steps

After implementing the fix:
1. Update docker compose.yml with the new worker command
2. Restart the worker container: `docker compose restart worker`
3. Submit a test task to each queue
4. Monitor worker logs to ensure it's listening to all queues
5. Check Redis to confirm queues are being consumed
6. Verify tasks transition from PENDING to SUCCESS state

## Immediate Workaround

For immediate testing, restart the worker with all queues:
```bash
docker compose exec worker celery -A app.core.celery_app worker --loglevel=info -Q default,batch_processing,model_generation,maintenance,priority
```

## Additional Recommendations

1. Add queue monitoring to the health check endpoint
2. Implement alerts for queue depth thresholds
3. Document queue configuration in README
4. Consider using Flower (already in docker compose) for queue monitoring
5. Add integration tests that verify queue processing

## Related Configuration

The task routing configuration that's being ignored:
```python
# From app/core/celery_app.py
task_routes = {
    'app.workers.tasks.generate_3d_model_task': {'queue': 'model_generation'},
    'app.workers.tasks.process_batch': {'queue': 'batch_processing'},
    'app.workers.cleanup.cleanup_old_files': {'queue': 'maintenance'},
    # ... etc
}
```
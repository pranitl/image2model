# Enhancement: Batch-Centric Progress Tracking

## Overview
Currently, progress tracking requires the Celery `task_id`, but the business model treats everything as batches. We should enhance the system to use `batch_id` as the primary identifier throughout.

## Current State
- Upload returns: `batch_id`, `job_id`, `task_id`
- Progress tracking requires: `task_id` for SSE endpoint
- Users think in terms of batches, not Celery tasks

## Proposed Enhancement

### Backend Changes
1. Add new endpoints that accept `batch_id`:
   ```
   GET  /api/v1/batch/{batch_id}/progress
   GET  /api/v1/batch/{batch_id}/stream  (SSE)
   POST /api/v1/batch/{batch_id}/cancel
   ```

2. Backend maps `batch_id` → `task_id` internally using Redis/session store

3. Enhanced progress tracking:
   - Overall batch progress percentage
   - Individual file statuses with progress
   - File-by-file completion events

### Frontend Changes
1. Use `batch_id` exclusively in URLs and API calls
2. Show file-by-file progress in the UI:
   ```
   ✓ shoe.jpg - Complete (2.3s)
   ⟳ jacket.jpg - Processing 45% 
   ⏸ hat.jpg - Queued
   ```

### Benefits
- Aligns with business model (everything is a batch)
- Cleaner URLs: `/processing?batch=abc123`
- Better user experience with detailed progress
- Consistent identifier throughout the system

## Implementation Notes
- Maintain backward compatibility with `task_id` during transition
- Consider WebSocket instead of SSE for bi-directional updates
- Add batch metadata storage for richer UI (upload time, file count, etc.)

## Related
- fal.ai integration improvements
- File-by-file progress tracking
- Batch result downloading
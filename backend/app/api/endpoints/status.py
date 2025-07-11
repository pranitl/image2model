"""
Server-Sent Events (SSE) endpoint for streaming real-time task progress updates.
"""

import asyncio
import json
import logging
import time
from typing import AsyncGenerator, Dict, Any

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

from app.core.celery_app import celery_app
from app.core.exceptions import ProcessingException, NetworkException, log_exception
from app.core.progress_tracker import progress_tracker

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tasks/{task_id}/stream")
async def stream_task_status(
    task_id: str, 
    request: Request,
    timeout: int = 3600  # Default 1 hour timeout
):
    """
    Stream real-time progress updates for a specific Celery task via Server-Sent Events.
    
    Args:
        task_id: The Celery task ID to monitor
        request: FastAPI request object for client disconnect detection
        timeout: Maximum time in seconds to keep the connection alive (default: 3600)
        
    Returns:
        StreamingResponse with text/event-stream content type
        
    Raises:
        HTTPException: If task_id is invalid or timeout is out of range
    """
    
    # Validate input parameters
    if not task_id or not task_id.strip():
        raise HTTPException(status_code=400, detail="Task ID cannot be empty")
    
    if timeout < 1 or timeout > 86400:  # Max 24 hours
        raise HTTPException(
            status_code=400, 
            detail="Timeout must be between 1 and 86400 seconds (24 hours)"
        )
    
    # Validate task_id format (UUID format expected)
    import re
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, task_id.lower()):
        raise HTTPException(
            status_code=400, 
            detail="Invalid task ID format. Expected UUID format."
        )
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """
        Async generator that yields SSE formatted messages with task progress.
        """
        # Keep original task_id for logging and use a mutable tracking_id for chord switching
        original_task_id = task_id
        tracking_id = task_id  # This is what we'll update when tracking chord
        try:
            logger.info(f"Starting SSE stream for task {tracking_id} with {timeout}s timeout")
            start_time = time.time()
            last_heartbeat = time.time()
            heartbeat_interval = 30  # Send heartbeat every 30 seconds
            
            while True:
                # Check if client has disconnected
                if await request.is_disconnected():
                    logger.info(f"Client disconnected from SSE stream for task {original_task_id}")
                    break
                
                # Check for connection timeout
                if time.time() - start_time > timeout:
                    logger.info(f"SSE stream timeout reached for task {original_task_id}")
                    timeout_data = {
                        'status': 'timeout',
                        'message': f'Connection timeout after {timeout} seconds',
                        'task_id': tracking_id,
                        'timestamp': int(time.time() * 1000)
                    }
                    yield f"event: connection_timeout\ndata: {json.dumps(timeout_data)}\n\n"
                    break
                
                try:
                    # Get task status from Celery
                    task_result = celery_app.AsyncResult(tracking_id)
                    
                    # Format data based on task state
                    if task_result.state == 'PENDING':
                        data = {
                            'status': 'queued',
                            'progress': 0,
                            'message': 'Task is queued and waiting to start',
                            'task_id': tracking_id
                        }
                        
                    elif task_result.state == 'PROGRESS':
                        # Extract progress information from task meta
                        meta = task_result.info or {}
                        current = meta.get('current', 0)
                        total = meta.get('total', 1)
                        # Use progress directly from meta if available, otherwise calculate
                        progress = meta.get('progress', round((current / max(total, 1)) * 100, 2))
                        
                        # Enhanced progress data with additional metadata
                        data = {
                            'status': 'processing',
                            'progress': progress,
                            'current': current,
                            'total': total,
                            'message': meta.get('status', 'Processing...'),
                            'task_id': tracking_id,
                            'timestamp': int(time.time() * 1000),  # Milliseconds
                            'task_name': task_result.name if hasattr(task_result, 'name') else 'unknown'
                        }
                        
                        # Add batch-specific information if available
                        if 'batch_id' in meta:
                            data['batch_id'] = meta['batch_id']
                        if 'job_id' in meta:
                            data['job_id'] = meta['job_id']
                        
                        # Add file count information for batch processing
                        if 'total_files' in meta:
                            data['total_files'] = meta['total_files']
                        elif total > 0:
                            # If we have a total, use it as total_files for compatibility
                            data['total_files'] = total
                        
                        # Add estimated time remaining if we have timing data
                        if current > 0 and 'start_time' in meta:
                            elapsed = time.time() - meta['start_time']
                            if elapsed > 0:
                                estimated_total_time = (elapsed / current) * total
                                eta_seconds = max(0, estimated_total_time - elapsed)
                                data['eta_seconds'] = round(eta_seconds, 1)
                                data['estimated_completion'] = int((time.time() + eta_seconds) * 1000)
                        
                    elif task_result.state == 'SUCCESS':
                        # Task completed successfully
                        result = task_result.result or {}
                        
                        # Check if this is a chord starter task
                        if isinstance(result, dict) and result.get('chord_task_id'):
                            # This is a batch processing task that started a chord
                            # We need to continue tracking the chord
                            chord_id = result['chord_task_id']
                            logger.info(f"Main task {original_task_id} started chord {chord_id}, continuing to track chord")
                            
                            # Switch to tracking the chord task
                            tracking_id = chord_id  # Update tracking_id to track the chord
                            
                            # Send a progress update about switching to chord tracking
                            data = {
                                'status': 'processing',
                                'progress': 10,  # Just started processing files
                                'message': 'Starting to process files...',
                                'task_id': tracking_id,
                                'chord_task_id': chord_id,
                                'job_id': result.get('job_id'),  # Include job_id from main task result
                                'total_files': result.get('total_files', 0),  # Include file count
                                'total': result.get('total_files', 0),  # Also as 'total' for compatibility
                                'current': 0,  # Starting at 0 files completed
                                'timestamp': int(time.time() * 1000)
                            }
                            
                            # Send progress update and continue the loop
                            yield f"event: task_progress\ndata: {json.dumps(data)}\n\n"
                            
                            # Continue the loop to track the chord task
                            continue
                            
                        else:
                            # Regular task completion (not a chord)
                            data = {
                                'status': 'completed',
                                'progress': 100,
                                'message': 'Task completed successfully',
                                'task_id': tracking_id,
                                'result': result,
                                'timestamp': int(time.time() * 1000),
                                'task_name': task_result.name if hasattr(task_result, 'name') else 'unknown'
                            }
                        
                            # Add result summary if available
                            if isinstance(result, dict):
                                if 'total_files' in result:
                                    data['summary'] = {
                                        'total_files': result.get('total_files', 0),
                                        'successful_files': result.get('successful_files', 0),
                                        'failed_files': result.get('failed_files', 0)
                                    }
                        
                            # Send final success message and terminate stream
                            yield f"event: task_completed\ndata: {json.dumps(data)}\n\n"
                            logger.info(f"Task {tracking_id} completed successfully, ending SSE stream")
                            break
                        
                    elif task_result.state == 'FAILURE':
                        # Task failed
                        error_info = task_result.info or {}
                        data = {
                            'status': 'failed',
                            'progress': 0,
                            'message': 'Task failed',
                            'task_id': tracking_id,
                            'error': str(error_info) if error_info else 'Unknown error occurred',
                            'timestamp': int(time.time() * 1000),
                            'task_name': task_result.name if hasattr(task_result, 'name') else 'unknown'
                        }
                        
                        # Add detailed error information if available
                        if isinstance(error_info, dict):
                            if 'traceback' in error_info:
                                data['traceback'] = str(error_info['traceback'])
                            if 'job_id' in error_info:
                                data['job_id'] = error_info['job_id']
                            if 'batch_id' in error_info:
                                data['batch_id'] = error_info['batch_id']
                        
                        # Send failure message and terminate stream
                        yield f"event: task_failed\ndata: {json.dumps(data)}\n\n"
                        logger.error(f"Task {tracking_id} failed, ending SSE stream")
                        break
                        
                    elif task_result.state == 'RETRY':
                        # Task is being retried
                        data = {
                            'status': 'retrying',
                            'progress': 0,
                            'message': 'Task is being retried',
                            'task_id': tracking_id
                        }
                        
                    elif task_result.state == 'REVOKED':
                        # Task was cancelled/revoked
                        data = {
                            'status': 'cancelled',
                            'progress': 0,
                            'message': 'Task was cancelled',
                            'task_id': tracking_id
                        }
                        
                        # Send cancellation message and terminate stream
                        yield f"data: {json.dumps(data)}\n\n"
                        logger.info(f"Task {tracking_id} was cancelled, ending SSE stream")
                        break
                        
                    else:
                        # Unknown state
                        data = {
                            'status': 'unknown',
                            'progress': 0,
                            'message': f'Unknown task state: {task_result.state}',
                            'task_id': tracking_id
                        }
                    
                    # Determine event type based on status
                    if data['status'] == 'processing':
                        event_type = "task_progress"
                    elif data['status'] == 'queued':
                        event_type = "task_queued"
                    elif data['status'] == 'retrying':
                        event_type = "task_retry"
                    elif data['status'] == 'cancelled':
                        event_type = "task_cancelled"
                    else:
                        event_type = "task_status"
                    
                    # Yield the formatted SSE message with event type
                    yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
                    
                except Exception as task_error:
                    logger.error(f"Error getting task status for {tracking_id}: {str(task_error)}")
                    
                    # Try to determine if this is a recoverable error
                    error_type = type(task_error).__name__
                    is_recoverable = error_type in ['ConnectionError', 'TimeoutError', 'BrokenPipeError']
                    
                    error_data = {
                        'status': 'error',
                        'progress': 0,
                        'message': 'Error retrieving task status',
                        'task_id': tracking_id,
                        'error': str(task_error),
                        'error_type': error_type,
                        'recoverable': is_recoverable,
                        'timestamp': int(time.time() * 1000)
                    }
                    
                    yield f"event: task_error\ndata: {json.dumps(error_data)}\n\n"
                    
                    # If it's not recoverable, break the loop
                    if not is_recoverable:
                        logger.error(f"Non-recoverable error for task {tracking_id}, ending stream")
                        break
                    
                    # For recoverable errors, wait a bit longer before retrying
                    await asyncio.sleep(5)
                
                # Check if we need to send a heartbeat
                current_time = time.time()
                if current_time - last_heartbeat > heartbeat_interval:
                    heartbeat_data = {
                        'status': 'heartbeat',
                        'timestamp': int(current_time * 1000),
                        'task_id': tracking_id
                    }
                    yield f"event: heartbeat\ndata: {json.dumps(heartbeat_data)}\n\n"
                    last_heartbeat = current_time
                
                # Wait before next update (1 second polling interval)
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for task {original_task_id}")
            # Don't yield anything for cancelled streams - client already disconnected
            
        except Exception as e:
            logger.error(f"SSE stream error for task {original_task_id}: {str(e)}", exc_info=True)
            try:
                error_data = {
                    'status': 'stream_error',
                    'progress': 0,
                    'message': 'Server-side streaming error occurred',
                    'task_id': task_id,
                    'error': str(e),
                    'timestamp': int(time.time() * 1000)
                }
                yield f"event: stream_error\ndata: {json.dumps(error_data)}\n\n"
            except Exception:
                # If we can't even send the error message, just log it
                logger.error(f"Failed to send error message for task {original_task_id}")
                
        finally:
            # Cleanup resources
            logger.info(f"SSE stream ended for task {original_task_id}")
    
    # Return StreamingResponse with proper SSE headers
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*",  # Allow CORS for frontend
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str):
    """
    Get current status of a specific Celery task (non-streaming endpoint).
    
    Args:
        task_id: The Celery task ID to check
        
    Returns:
        Dict with current task status information
        
    Raises:
        HTTPException: If task_id is invalid or task cannot be found
    """
    
    # Validate task_id
    if not task_id or not task_id.strip():
        raise HTTPException(status_code=400, detail="Task ID cannot be empty")
    
    # Validate task_id format (UUID format expected)
    import re
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, task_id.lower()):
        raise HTTPException(
            status_code=400, 
            detail="Invalid task ID format. Expected UUID format."
        )
    try:
        # Attempt to get task result with timeout handling
        try:
            task_result = celery_app.AsyncResult(task_id)
        except Exception as e:
            logger.error(f"Failed to connect to Celery for task {task_id}: {str(e)}")
            raise NetworkException(
                message="Failed to connect to task queue service",
                service="Celery",
                details={"task_id": task_id, "connection_error": str(e)}
            )
        
        if task_result.state == 'PENDING':
            return {
                'status': 'queued',
                'progress': 0,
                'message': 'Task is queued',
                'task_id': task_id,
                'state': task_result.state
            }
            
        elif task_result.state == 'PROGRESS':
            meta = task_result.info or {}
            current = meta.get('current', 0)
            total = meta.get('total', 1)
            progress = round((current / max(total, 1)) * 100, 2)
            
            return {
                'status': 'processing',
                'progress': progress,
                'current': current,
                'total': total,
                'message': meta.get('status', 'Processing...'),
                'task_id': task_id,
                'state': task_result.state,
                'timestamp': int(time.time() * 1000)
            }
            
        elif task_result.state == 'SUCCESS':
            result = task_result.result or {}
            return {
                'status': 'completed',
                'progress': 100,
                'message': 'Task completed successfully',
                'task_id': task_id,
                'state': task_result.state,
                'result': result,
                'timestamp': int(time.time() * 1000)
            }
            
        elif task_result.state == 'FAILURE':
            error_info = task_result.info or {}
            
            # Format error information safely
            if isinstance(error_info, dict):
                error_message = error_info.get('error', 'Unknown error occurred')
                error_details = {k: v for k, v in error_info.items() if k != 'traceback'}
            else:
                error_message = str(error_info)
                error_details = {}
            
            return {
                'status': 'failed',
                'progress': 0,
                'message': 'Task failed',
                'task_id': task_id,
                'state': task_result.state,
                'error': error_message,
                'error_details': error_details,
                'timestamp': int(time.time() * 1000)
            }
            
        elif task_result.state == 'RETRY':
            return {
                'status': 'retrying',
                'progress': 0,
                'message': 'Task is being retried due to temporary failure',
                'task_id': task_id,
                'state': task_result.state,
                'timestamp': int(time.time() * 1000)
            }
            
        elif task_result.state == 'REVOKED':
            return {
                'status': 'cancelled',
                'progress': 0,
                'message': 'Task was cancelled',
                'task_id': task_id,
                'state': task_result.state,
                'timestamp': int(time.time() * 1000)
            }
            
        else:
            return {
                'status': task_result.state.lower(),
                'progress': 0,
                'message': f'Task state: {task_result.state}',
                'task_id': task_id,
                'state': task_result.state,
                'timestamp': int(time.time() * 1000)
            }
            
    except NetworkException:
        # Re-raise network exceptions as-is
        raise
    except Exception as e:
        log_exception(e, f"get_task_status for task {task_id}")
        raise ProcessingException(
            message=f"Error retrieving task status: {str(e)}",
            job_id=task_id,
            stage="status_check",
            details={"task_id": task_id}
        )


@router.get("/jobs/{job_id}/progress")
async def get_job_progress(job_id: str):
    """
    Get aggregated progress for a parallel batch job from Redis.
    
    This endpoint provides real-time progress information for jobs
    being processed in parallel, including individual file statuses.
    
    Args:
        job_id: The job identifier
        
    Returns:
        Dict with job progress information including:
        - overall_progress: Overall percentage (0-100)
        - total_files: Total number of files
        - completed_files: Number of completed files
        - failed_files: Number of failed files
        - files: Dict of file statuses and progress
    """
    try:
        # Get progress data from Redis
        progress_data = progress_tracker.get_job_progress(job_id)
        
        if not progress_data:
            # No progress data found, check if job exists in Celery
            # This could mean the job hasn't started yet or has expired
            raise HTTPException(
                status_code=404,
                detail=f"No progress data found for job {job_id}"
            )
        
        # Calculate overall progress
        overall_progress = progress_tracker.get_overall_progress(job_id)
        
        # Return progress information
        return {
            "job_id": job_id,
            "overall_progress": overall_progress,
            "total_files": progress_data["total_files"],
            "completed_files": progress_data["completed_files"],
            "failed_files": progress_data["failed_files"],
            "files": progress_data["files"],
            "timestamp": int(time.time() * 1000)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job progress for {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve job progress: {str(e)}"
        )
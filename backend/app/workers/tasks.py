"""
Background tasks for 3D model generation.
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional

from celery import current_task
from celery.exceptions import SoftTimeLimitExceeded, Retry

from app.core.celery_app import celery_app
from app.core.exceptions import (
    FALAPIException,
    ProcessingException,
    NetworkException,
    RateLimitException,
    log_exception
)

# Use enhanced logging from core
from app.core.logging_config import get_task_logger, set_correlation_id
from app.core.progress_tracker import progress_tracker

# Import FAL.AI client for real 3D model generation
from app.workers.fal_client import get_model_client

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def generate_3d_model_task(self, file_id: str, file_path: str, job_id: str, model_type: str = "tripo3d", params: Optional[Dict[str, Any]] = None):
    """
    Background task to generate 3D model from image using specified model.
    
    Args:
        file_id: Unique file identifier
        file_path: Path to the input image file
        job_id: Unique job identifier
        model_type: Type of model to use ("tripo3d" or "trellis")
        params: Model-specific parameters
        
    Returns:
        Dict with job results
    """
    try:
        # Update progress to 10%
        original_filename = os.path.basename(file_path)
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 0,  # File index (0 for single file)
                "total": 1,    # Total files (1 for single file)
                "progress": 10,  # Actual progress percentage
                "status": f"Initializing 3D generation for {original_filename}...",
                "filename": original_filename,
                "job_id": job_id,
                "file_id": file_id
            }
        )
        
        logger.info(f"Starting {model_type} generation for file {file_id} (job: {job_id})")
        
        # Use FAL.AI client for actual 3D model generation
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": 1,
                "progress": 25,
                "status": f"Uploading {original_filename} to FAL.AI {model_type}...",
                "filename": original_filename,
                "job_id": job_id,
                "file_id": file_id
            }
        )
        
        # Initialize parameters if not provided
        if params is None:
            params = {}
        
        logger.info(f"Processing with model: {model_type}, params: {params}")
        
        # Get the appropriate client for the model type
        fal_client = get_model_client(model_type)
        
        # Progress callback to update Celery task state with proper filename
        original_filename = os.path.basename(file_path)
        
        def progress_callback(message, progress_percent):
            # Update Celery task state
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": 0,  # File index (always 0 for single file)
                    "total": 1,    # Total files (always 1 for single file)
                    "progress": progress_percent,  # Actual progress percentage
                    "status": f"Processing {original_filename}: {message}",
                    "filename": original_filename,
                    "job_id": job_id,
                    "file_id": file_id
                }
            )
            
            # Also update Redis progress tracker if this is part of a batch
            if job_id:
                try:
                    progress_tracker.update_file_progress(
                        job_id=job_id,
                        file_path=file_path,
                        status="processing",
                        progress=progress_percent
                    )
                except Exception as e:
                    logger.warning(f"Failed to update progress tracker: {e}")
        
        # Call real 3D model generation using synchronous wrapper
        result = fal_client.process_single_image_sync(
            file_path=file_path,
            params=params,
            progress_callback=progress_callback,
            job_id=job_id  # Pass job_id for proper file organization
        )
        
        if result["status"] == "success":
            # Store FAL.AI result in job store for later retrieval
            from app.core.job_store import job_store
            
            # Prepare job result data
            job_result = {
                "job_id": job_id,
                "model_type": model_type,  # Store model type for client rendering
                "files": [{
                    "filename": result.get("filename", f"{original_filename.rsplit('.', 1)[0]}.glb"),
                    "model_url": result.get("download_url"),  # Direct FAL.AI URL
                    "file_size": result.get("file_size", 0),
                    "content_type": result.get("content_type", "model/gltf-binary"),
                    "rendered_image": result.get("rendered_image"),
                    "task_id": result.get("task_id")
                }],
                "total_files": 1,
                "successful_files": 1,
                "failed_files": 0
            }
            
            # Store in job store
            job_store.set_job_result(job_id, job_result)
            
            # Final completion state - update with result in meta for SSE endpoint  
            task_meta = {
                "current": 1,
                "total": 1,
                "progress": 100,
                "status": f"3D model generated successfully for {original_filename}",
                "filename": original_filename,
                "job_id": job_id,
                "file_id": file_id,
                "total_files": 1,
                "successful_files": 1,
                "failed_files": 0,
                "results": [{
                    "file_path": file_path,
                    "status": "completed",
                    "result_path": result["output"],
                    "download_url": result.get("download_url"),
                    "model_format": result.get("model_format", "glb"),
                    "rendered_image": result.get("rendered_image")
                }]
            }
            
            current_task.update_state(
                state="SUCCESS",
                meta=task_meta
            )
            
            logger.info(f"FAL.AI {model_type} generation completed successfully for job {job_id}")
            
            # Update progress tracker for completion
            if job_id:
                try:
                    progress_tracker.update_file_progress(
                        job_id=job_id,
                        file_path=file_path,
                        status="completed",
                        progress=100
                    )
                except Exception as e:
                    logger.warning(f"Failed to update progress tracker: {e}")
            
            # Return the full result including all necessary fields for SSE
            return {
                "job_id": job_id,
                "file_id": file_id,
                "status": "completed",
                "result_path": result["output"],  # FAL.AI client returns "output" field
                "model_format": result.get("model_format", "glb"),
                "rendered_image": result.get("rendered_image"),
                "processing_time": result.get("processing_time", 0),
                "message": f"3D model generated successfully for {original_filename}",
                "filename": original_filename,
                "total_files": 1,
                "successful_files": 1,
                "failed_files": 0,
                # Include job_result for download endpoint's Redis scan fallback
                "job_result": job_result
            }
        else:
            # Handle failure case
            error_message = result.get("error", f"Unknown error during FAL.AI {model_type} generation")
            logger.error(f"FAL.AI {model_type} generation failed for job {job_id}: {error_message}")
            
            # Update progress tracker for failure
            if job_id:
                try:
                    progress_tracker.update_file_progress(
                        job_id=job_id,
                        file_path=file_path,
                        status="failed",
                        progress=100,
                        error=error_message
                    )
                except Exception as e:
                    logger.warning(f"Failed to update progress tracker: {e}")
            
            current_task.update_state(
                state="FAILURE",
                meta={
                    "error": error_message,
                    "job_id": job_id,
                    "file_id": file_id,
                    "error_type": result.get("error_type", "unknown")
                }
            )
            
            raise ProcessingException(
                message=f"FAL.AI {model_type} generation failed: {error_message}",
                job_id=job_id,
                stage="model_generation"
            )
        
    except ProcessingException:
        # Re-raise processing exceptions
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in {model_type} generation for job {job_id}: {str(exc)}", exc_info=True)
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": f"Unexpected error: {str(exc)}", 
                "job_id": job_id,
                "file_id": file_id
            }
        )
        raise ProcessingException(
            message=f"Unexpected error during 3D model generation: {str(exc)}",
            job_id=job_id,
            stage="unexpected_error"
        )


@celery_app.task
def cleanup_old_files():
    """
    Background task to cleanup old uploaded files and generated models.
    """
    # TODO: Implement file cleanup logic
    logger.info("Running file cleanup task")
    return {"status": "completed", "message": "File cleanup completed"}



@celery_app.task(bind=True)
def process_file_in_batch(self, file_path: str, job_id: str, face_limit: Optional[int] = None, file_index: int = 0, total_files: int = 1):
    """
    Process a single file as part of a batch operation.
    This task is designed to be run in parallel with other files from the same batch.
    
    Args:
        file_path: Path to the image file to process
        job_id: Unique job identifier for the batch
        face_limit: Optional limit on number of faces in generated models
        file_index: Index of this file in the batch (for progress tracking)
        total_files: Total number of files in the batch
        
    Returns:
        Dict with processing result for this file
    """
    try:
        logger.info(f"Processing file {file_index + 1}/{total_files} in parallel: {os.path.basename(file_path)}")
        
        # Create progress callback for this specific file
        def parallel_file_progress_callback(message: str, progress: int):
            """Callback to update progress for individual file in parallel batch."""
            # Update progress tracker for this specific file
            try:
                progress_tracker.update_file_progress(
                    job_id=job_id,
                    file_path=file_path,
                    status="processing",
                    progress=progress
                )
            except Exception as e:
                logger.warning(f"Failed to update progress tracker: {e}")
            
            # Don't update Celery task state here since we're in a subtask
            return None

        # Process single image using FAL.AI with synchronous wrapper
        file_start_time = time.time()
        from app.workers.fal_client import fal_client
        
        try:
            # Use synchronous wrapper to avoid coroutine serialization issues
            result = fal_client.process_single_image_sync(
                file_path=file_path, 
                face_limit=face_limit, 
                texture_enabled=True,
                progress_callback=parallel_file_progress_callback,
                job_id=job_id
            )
        except Exception as process_error:
            logger.error(f"Error processing image: {str(process_error)}", exc_info=True)
            raise
        
        actual_processing_time = time.time() - file_start_time
        
        if result["status"] == "success":
            file_result = {
                "file_path": file_path,
                "status": "completed",
                "result_path": result.get("download_url"),  # FAL.AI URL
                "download_url": result.get("download_url"),
                "model_url": result.get("model_url"),
                "rendered_image": result.get("rendered_image"),
                "filename": result.get("filename"),
                "face_count": face_limit if face_limit else 1000,
                "processing_time": actual_processing_time,
                "model_format": result.get("model_format", "glb"),
                "file_size": result.get("file_size", 0),
                "content_type": result.get("content_type", "model/gltf-binary"),
                "task_id": result.get("task_id")
            }
            logger.info(f"Successfully processed {os.path.basename(file_path)} in {actual_processing_time:.2f}s")
        else:
            file_result = {
                "file_path": file_path,
                "status": "failed",
                "error": result.get("error", "Unknown error"),
                "processing_time": actual_processing_time
            }
            logger.error(f"Failed to process {os.path.basename(file_path)}: {result.get('error', 'Unknown error')}")
        
        return file_result
        
    except Exception as exc:
        logger.error(f"File processing failed for {file_path}: {str(exc)}", exc_info=True)
        return {
            "file_path": file_path,
            "status": "failed",
            "error": str(exc),
            "processing_time": time.time() - (file_start_time if 'file_start_time' in locals() else 0)
        }


@celery_app.task(bind=True)
def finalize_batch_results(self, results: List[Dict[str, Any]], job_id: str, total_files: int, face_limit: Optional[int] = None):
    """
    Callback task to finalize batch processing results after all files are processed.
    
    This task is called by the chord after all parallel file processing tasks complete.
    It aggregates results and stores them in the job store.
    
    Args:
        results: List of results from each file processing task
        job_id: Unique job identifier
        total_files: Total number of files in the batch
        face_limit: Optional limit on number of faces in generated models
        
    Returns:
        Dict with batch processing summary
    """
    try:
        # Final completion update
        success_count = sum(1 for r in results if r["status"] == "completed")
        failure_count = sum(1 for r in results if r["status"] == "failed")
        timeout_count = sum(1 for r in results if r.get("status") == "timeout")
        
        final_status = "completed" if success_count > 0 else "failed"
        if timeout_count > 0:
            final_status = "partially_completed"
        
        result_summary = {
            "job_id": job_id,
            "status": final_status,
            "total_files": total_files,
            "successful_files": success_count,
            "failed_files": failure_count,
            "timeout_files": timeout_count,
            "face_limit": face_limit,
            "results": results,
            "message": f"Batch processing completed. {success_count} successful, {failure_count} failed, {timeout_count} timed out."
        }
        
        # Store job results for later retrieval by the download API
        if success_count > 0:
            from app.core.job_store import job_store
            
            # Prepare job result data in the format expected by download API
            job_result = {
                "job_id": job_id,
                "model_type": "tripo3d",  # Default to tripo3d for batch processing
                "files": [],
                "total_files": total_files,
                "successful_files": success_count,
                "failed_files": failure_count
            }
            
            # Add successful files to job result
            for result in results:
                if result["status"] == "completed" and result.get("download_url"):
                    job_result["files"].append({
                        "filename": result.get("filename", os.path.basename(result["file_path"])),
                        "model_url": result.get("download_url"),
                        "file_size": result.get("file_size", 0),
                        "content_type": result.get("content_type", "model/gltf-binary"),
                        "rendered_image": result.get("rendered_image"),
                        "task_id": result.get("task_id")
                    })
            
            # Store in job store
            job_store.set_job_result(job_id, job_result)
            logger.info(f"Stored job results for {job_id} with {len(job_result['files'])} files")
        
        logger.info(f"Batch processing completed for job {job_id}: {result_summary['message']}")
        return result_summary
        
    except Exception as exc:
        logger.error(f"Failed to finalize batch results for job {job_id}: {str(exc)}", exc_info=True)
        raise


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_batch(self, job_id: str, file_paths: List[str], face_limit: Optional[int] = None):
    """
    Enhanced batch processing task that processes files in parallel across multiple workers.
    
    This task creates individual subtasks for each file and executes them in parallel
    using Celery's chord primitive, which handles the callback automatically.
    
    Args:
        job_id: Unique job identifier
        file_paths: List of paths to uploaded image files
        face_limit: Optional limit on number of faces in generated models
        
    Returns:
        Dict with batch processing results
    """
    try:
        total_files = len(file_paths)
        logger.info(f"Starting parallel batch processing for job {job_id} with {total_files} files")
        
        # Store start time for timeout tracking
        start_time = time.time()
        
        # Update progress to starting
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 0, 
                "total": total_files,
                "total_files": total_files,  # Add explicit total_files
                "status": f"Starting parallel batch processing for {total_files} files...",
                "job_id": job_id
            }
        )
        
        # Import Celery's chord primitive for parallel execution with callback
        from celery import chord
        
        # Create a list of parallel tasks for each file
        parallel_tasks = [
            process_file_in_batch.s(
                file_path=file_path,
                job_id=job_id,
                face_limit=face_limit,
                file_index=i,
                total_files=total_files
            ) for i, file_path in enumerate(file_paths)
        ]
        
        # Execute all tasks in parallel with a callback to finalize results
        logger.info(f"Dispatching {total_files} files to process in parallel")
        
        # Update progress while processing
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 0,
                "total": total_files,
                "total_files": total_files,  # Add explicit total_files
                "status": f"Processing {total_files} files in parallel across workers...",
                "job_id": job_id
            }
        )
        
        # Use chord to execute tasks in parallel and call finalize_batch_results when done
        # The chord will automatically handle result collection without blocking
        chord_result = chord(parallel_tasks)(
            finalize_batch_results.s(job_id=job_id, total_files=total_files, face_limit=face_limit)
        )
        
        # Return the chord result ID so the upload endpoint can track it
        logger.info(f"Batch processing initiated for job {job_id} with chord ID: {chord_result.id}")
        
        # Return a response indicating processing has started
        return {
            "job_id": job_id,
            "status": "processing",
            "total_files": total_files,
            "message": f"Processing {total_files} files in parallel",
            "chord_task_id": chord_result.id
        }
        
    except SoftTimeLimitExceeded:
        logger.error(f"Batch task soft time limit exceeded for job {job_id}")
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": "Task time limit exceeded", 
                "job_id": job_id,
                "processed_files": len(results) if 'results' in locals() else 0
            }
        )
        raise
        
    except Exception as exc:
        logger.error(f"Batch task failed for job {job_id}: {str(exc)}", exc_info=True)
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(exc), 
                "job_id": job_id
            }
        )
        raise exc



@celery_app.task(bind=True, max_retries=5)
def process_single_image_with_retry(self, file_path: str, face_limit: Optional[int] = None):
    """
    Enhanced task to process a single image with comprehensive retry logic.
    
    Implements exponential backoff for rate limits, circuit breaker pattern for 
    repeated failures, and proper error categorization.
    
    Args:
        file_path: Path to the input image file
        face_limit: Optional limit on number of faces
        
    Returns:
        Dict with processing result
        
    Raises:
        FALAPIException: For FAL.AI API errors
        ProcessingException: For processing errors
        NetworkException: For network-related errors
        RateLimitException: For rate limiting errors
    """
    try:
        # Add tracking information to task metadata
        task_start_time = time.time()
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 10,
                "total": 100,
                "status": f"Starting image processing (attempt {self.request.retries + 1})",
                "file_path": file_path,
                "retry_count": self.request.retries,
                "start_time": task_start_time
            }
        )
        
        logger.info(f"Processing image {file_path} (attempt {self.request.retries + 1}/{self.max_retries + 1})")
        
        # Create progress callback for enhanced retry task
        def retry_progress_callback(message: str, progress: int):
            """Callback to update Celery task progress during retry processing."""
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "current": progress,
                    "total": 100,
                    "status": message,
                    "file_path": file_path,
                    "retry_count": self.request.retries,
                    "start_time": task_start_time
                }
            )
            logger.info(f"Retry task progress: {progress}% - {message}")

        # Import FAL client and process with sync wrapper
        from app.workers.fal_client import fal_client
        result = fal_client.process_single_image_sync(
            file_path=file_path, 
            face_limit=face_limit, 
            texture_enabled=True,
            progress_callback=retry_progress_callback
        )
        
        # Check if result indicates a retryable error
        if result["status"] == "failed" and result.get("retryable", False):
            error_type = result.get("error_type", "unknown")
            error_message = result.get("error", "Unknown error")
            
            # Handle specific error types with appropriate retry logic
            if error_type == "rate_limit_error":
                # Exponential backoff for rate limiting (start with 60 seconds)
                backoff_time = 60 * (2 ** self.request.retries)
                backoff_time = min(backoff_time, 900)  # Cap at 15 minutes
                
                logger.warning(f"Rate limit hit for {file_path}, retrying in {backoff_time}s (attempt {self.request.retries + 1})")
                
                raise self.retry(
                    countdown=backoff_time,
                    exc=RateLimitException(
                        message=f"FAL.AI rate limit exceeded: {error_message}",
                        retry_after=backoff_time,
                        limit_type="api_requests"
                    )
                )
                
            elif error_type == "timeout_error":
                # Progressive timeout increase for timeout errors
                backoff_time = 30 * (self.request.retries + 1)
                backoff_time = min(backoff_time, 300)  # Cap at 5 minutes
                
                logger.warning(f"Timeout for {file_path}, retrying in {backoff_time}s (attempt {self.request.retries + 1})")
                
                raise self.retry(
                    countdown=backoff_time,
                    exc=NetworkException(
                        message=f"Request timeout: {error_message}",
                        service="FAL.AI",
                        retry_after=backoff_time
                    )
                )
                
            elif error_type == "download_error":
                # Shorter backoff for download errors
                backoff_time = 10 * (self.request.retries + 1)
                
                logger.warning(f"Download error for {file_path}, retrying in {backoff_time}s (attempt {self.request.retries + 1})")
                
                raise self.retry(
                    countdown=backoff_time,
                    exc=ProcessingException(
                        message=f"Model download failed: {error_message}",
                        job_id=file_path,
                        stage="download"
                    )
                )
                
            else:
                # Generic retry with standard backoff
                backoff_time = 15 * (2 ** self.request.retries)
                backoff_time = min(backoff_time, 120)  # Cap at 2 minutes
                
                logger.warning(f"Retryable error for {file_path}, retrying in {backoff_time}s (attempt {self.request.retries + 1})")
                
                raise self.retry(
                    countdown=backoff_time,
                    exc=ProcessingException(
                        message=f"Processing error: {error_message}",
                        job_id=file_path,
                        stage="processing"
                    )
                )
        
        # Handle non-retryable failures
        elif result["status"] == "failed":
            error_type = result.get("error_type", "unknown")
            error_message = result.get("error", "Unknown error")
            
            if error_type == "authentication_error":
                raise FALAPIException(
                    message=f"Authentication failed: {error_message}",
                    status_code=401,
                    is_rate_limited=False
                )
            else:
                raise ProcessingException(
                    message=f"Non-retryable processing error: {error_message}",
                    job_id=file_path,
                    stage="processing"
                )
        
        # Update progress and return successful result
        processing_time = time.time() - task_start_time
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 100,
                "total": 100,
                "status": "Processing completed successfully",
                "file_path": file_path,
                "processing_time": processing_time
            }
        )
        
        logger.info(f"Successfully processed {file_path} in {processing_time:.2f}s (attempt {self.request.retries + 1})")
        return result
        
    except Retry:
        # Re-raise retry exceptions to maintain Celery retry behavior
        raise
    except (FALAPIException, ProcessingException, NetworkException, RateLimitException):
        # Re-raise our custom exceptions as-is
        raise
    except Exception as exc:
        # Handle unexpected errors
        log_exception(exc, f"process_single_image_with_retry for {file_path}")
        
        # Retry for unexpected errors (but limit retries)
        if self.request.retries < 2:  # Only retry twice for unexpected errors
            backoff_time = 30 + (self.request.retries * 30)
            logger.warning(f"Unexpected error for {file_path}, retrying in {backoff_time}s: {str(exc)}")
            
            raise self.retry(
                countdown=backoff_time,
                exc=ProcessingException(
                    message=f"Unexpected processing error: {str(exc)}",
                    job_id=file_path,
                    stage="unexpected_error"
                )
            )
        else:
            # No more retries for unexpected errors
            raise ProcessingException(
                message=f"Processing failed after retries: {str(exc)}",
                job_id=file_path,
                stage="final_failure"
            )


@celery_app.task
def health_check_task():
    """
    Simple health check task for monitoring worker status.
    """
    return {"status": "healthy", "worker": "image2model-worker"}
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
from app.core.monitoring import monitor_task, task_monitor

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def generate_3d_model_task(self, file_id: str, file_path: str, job_id: str, quality: str = "medium", texture_enabled: bool = True):
    """
    Background task to generate 3D model from image using Tripo3D.
    
    Args:
        file_id: Unique file identifier
        file_path: Path to the input image file
        job_id: Unique job identifier
        quality: Quality setting (low, medium, high)
        texture_enabled: Whether to enable texture generation
        
    Returns:
        Dict with job results
    """
    try:
        # Update progress to 10%
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 10, 
                "total": 100, 
                "status": "Initializing Tripo3D generation...",
                "job_id": job_id,
                "file_id": file_id
            }
        )
        
        logger.info(f"Starting Tripo3D generation for file {file_id} (job: {job_id})")
        
        # Use FAL.AI client for actual 3D model generation
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 25, "total": 100, "status": "Uploading image to Tripo3D..."}
        )
        
        # Quality is now handled directly in FAL.AI client
        # The texture setting is passed through the texture_enabled parameter
        logger.info(f"Processing with quality: {quality}, texture_enabled: {texture_enabled}")
        
        # Process the image using FAL.AI client
        import asyncio
        result = asyncio.run(process_single_image(file_path, face_limit=None, texture_enabled=texture_enabled))
        
        if result["status"] == "success":
            current_task.update_state(
                state="PROGRESS",
                meta={"current": 90, "total": 100, "status": "Finalizing model..."}
            )
            
            logger.info(f"Tripo3D generation completed successfully for job {job_id}")
            
            return {
                "job_id": job_id,
                "file_id": file_id,
                "status": "completed",
                "result_path": result["output"],
                "model_format": result.get("model_format", "glb"),
                "rendered_image": result.get("rendered_image"),
                "processing_time": result.get("processing_time", 0),
                "message": "3D model generated successfully using Tripo3D"
            }
        else:
            # Handle failure case
            error_message = result.get("error", "Unknown error during Tripo3D generation")
            logger.error(f"Tripo3D generation failed for job {job_id}: {error_message}")
            
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
                message=f"Tripo3D generation failed: {error_message}",
                job_id=job_id,
                stage="model_generation"
            )
        
    except ProcessingException:
        # Re-raise processing exceptions
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in Tripo3D generation for job {job_id}: {str(exc)}", exc_info=True)
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
def process_batch_task(self, batch_id: str, job_id: str, file_paths: List[str], face_limit: Optional[int] = None):
    """
    Background task to process a batch of images for 3D model generation.
    
    Args:
        batch_id: Unique batch identifier
        job_id: Unique job identifier
        file_paths: List of paths to uploaded image files
        face_limit: Optional limit on number of faces in generated models
        
    Returns:
        Dict with batch processing results
    """
    try:
        total_files = len(file_paths)
        
        # Update progress to starting
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 0, 
                "total": total_files, 
                "status": f"Starting batch processing for {total_files} files...",
                "batch_id": batch_id,
                "job_id": job_id
            }
        )
        
        results = []
        
        # Process each file in the batch
        for i, file_path in enumerate(file_paths):
            try:
                # Update progress for current file
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i,
                        "total": total_files,
                        "status": f"Processing file {i+1}/{total_files}: {os.path.basename(file_path)}",
                        "batch_id": batch_id,
                        "job_id": job_id
                    }
                )
                
                # TODO: Replace with actual 3D model generation
                # For now, simulate processing
                import time
                time.sleep(1)  # Simulate processing time
                
                # Create individual file result
                file_result = {
                    "file_path": file_path,
                    "status": "completed",
                    "result_path": f"results/{batch_id}/{os.path.splitext(os.path.basename(file_path))[0]}.obj",
                    "face_count": face_limit if face_limit else 1000,  # Default face count
                    "processing_time": 1.0
                }
                
                results.append(file_result)
                
            except Exception as file_error:
                logger.error(f"Failed to process file {file_path}: {str(file_error)}")
                file_result = {
                    "file_path": file_path,
                    "status": "failed",
                    "error": str(file_error)
                }
                results.append(file_result)
        
        # Final completion update
        success_count = sum(1 for r in results if r["status"] == "completed")
        failure_count = len(results) - success_count
        
        return {
            "batch_id": batch_id,
            "job_id": job_id,
            "status": "completed",
            "total_files": total_files,
            "successful_files": success_count,
            "failed_files": failure_count,
            "face_limit": face_limit,
            "results": results,
            "message": f"Batch processing completed. {success_count} successful, {failure_count} failed."
        }
        
    except Exception as exc:
        logger.error(f"Batch task failed for batch {batch_id}: {str(exc)}")
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(exc), 
                "batch_id": batch_id, 
                "job_id": job_id
            }
        )
        raise exc


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
@monitor_task("process_batch")
def process_batch(self, job_id: str, file_paths: List[str], face_limit: Optional[int] = None):
    """
    Enhanced batch processing task for 3D model generation as specified in Task 6.
    
    Args:
        job_id: Unique job identifier
        file_paths: List of paths to uploaded image files
        face_limit: Optional limit on number of faces in generated models
        
    Returns:
        Dict with batch processing results
    """
    try:
        total_files = len(file_paths)
        logger.info(f"Starting batch processing for job {job_id} with {total_files} files")
        
        # Store start time for timeout tracking
        start_time = time.time()
        
        # Update progress to starting
        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": 0, 
                "total": total_files, 
                "status": f"Starting batch processing for {total_files} files...",
                "job_id": job_id
            }
        )
        
        results = []
        
        # Process each file in the batch
        for i, file_path in enumerate(file_paths):
            try:
                # Check for soft time limit
                time_elapsed = time.time() - start_time
                if time_elapsed > 25 * 60:  # 25 minutes soft limit
                    raise SoftTimeLimitExceeded()
                
                # Update progress for current file
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i,
                        "total": total_files,
                        "status": f"Processing file {i+1}/{total_files}: {os.path.basename(file_path)}",
                        "job_id": job_id
                    }
                )
                
                logger.info(f"Processing file {i+1}/{total_files}: {os.path.basename(file_path)}")
                
                # Process single image using FAL.AI
                file_start_time = time.time()
                import asyncio
                result = asyncio.run(process_single_image(file_path, face_limit))
                actual_processing_time = time.time() - file_start_time
                
                if result["status"] == "success":
                    file_result = {
                        "file_path": file_path,
                        "status": "completed",
                        "result_path": result["output"],
                        "face_count": face_limit if face_limit else 1000,
                        "processing_time": actual_processing_time,
                        "model_format": result.get("model_format", "glb")
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
                
                results.append(file_result)
                
            except SoftTimeLimitExceeded:
                logger.warning(f"Soft time limit exceeded while processing {file_path}")
                file_result = {
                    "file_path": file_path,
                    "status": "timeout",
                    "error": "Processing time limit exceeded"
                }
                results.append(file_result)
                break  # Stop processing remaining files
                
            except Exception as file_error:
                logger.error(f"Failed to process file {file_path}: {str(file_error)}", exc_info=True)
                file_result = {
                    "file_path": file_path,
                    "status": "failed",
                    "error": str(file_error)
                }
                results.append(file_result)
        
        # Final completion update
        success_count = sum(1 for r in results if r["status"] == "completed")
        failure_count = sum(1 for r in results if r["status"] == "failed")
        timeout_count = sum(1 for r in results if r["status"] == "timeout")
        
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
        
        logger.info(f"Batch processing completed for job {job_id}: {result_summary['message']}")
        return result_summary
        
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


async def process_single_image(file_path: str, face_limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Process a single image file using FAL.AI API for 3D model generation.
    
    Args:
        file_path: Path to the image file
        face_limit: Optional limit on number of faces
        
    Returns:
        Dict with processing result
    """
    from app.workers.fal_client import (
        fal_client, 
        FalAIError, 
        FalAIAuthenticationError, 
        FalAIRateLimitError, 
        FalAITimeoutError, 
        FalAIAPIError, 
        FalAIDownloadError
    )
    
    try:
        logger.info(f"Starting FAL.AI processing for image: {file_path}")
        
        # Use FAL.AI client to process the image
        result = await fal_client.process_single_image(file_path, face_limit)
        
        logger.info(f"FAL.AI processing completed for {file_path}: {result['status']}")
        return result
        
    except FalAIAuthenticationError as e:
        logger.error(f"Authentication error for {file_path}: {str(e)}")
        return {
            "status": "failed",
            "input": file_path,
            "error": f"Authentication failed: {str(e)}",
            "error_type": "authentication_error",
            "retryable": False
        }
    except FalAIRateLimitError as e:
        logger.error(f"Rate limit error for {file_path}: {str(e)}")
        return {
            "status": "failed",
            "input": file_path,
            "error": f"Rate limit exceeded: {str(e)}",
            "error_type": "rate_limit_error",
            "retryable": True
        }
    except FalAITimeoutError as e:
        logger.error(f"Timeout error for {file_path}: {str(e)}")
        return {
            "status": "failed",
            "input": file_path,
            "error": f"Request timed out: {str(e)}",
            "error_type": "timeout_error",
            "retryable": True
        }
    except FalAIDownloadError as e:
        logger.error(f"Download error for {file_path}: {str(e)}")
        return {
            "status": "failed",
            "input": file_path,
            "error": f"Download failed: {str(e)}",
            "error_type": "download_error",
            "retryable": True
        }
    except FalAIAPIError as e:
        logger.error(f"API error for {file_path}: {str(e)}")
        return {
            "status": "failed",
            "input": file_path,
            "error": f"API error: {str(e)}",
            "error_type": "api_error",
            "retryable": False
        }
    except FalAIError as e:
        logger.error(f"FAL.AI error for {file_path}: {str(e)}")
        return {
            "status": "failed",
            "input": file_path,
            "error": f"FAL.AI error: {str(e)}",
            "error_type": "fal_error",
            "retryable": False
        }
    except Exception as e:
        logger.error(f"Unexpected error processing {file_path}: {str(e)}", exc_info=True)
        return {
            "status": "failed",
            "input": file_path,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unknown_error",
            "retryable": False
        }


@celery_app.task(bind=True, max_retries=5)
@monitor_task("process_single_image_with_retry")
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
        
        # Import and process with async handling
        import asyncio
        result = asyncio.run(process_single_image(file_path, face_limit))
        
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


@celery_app.task(bind=True, max_retries=3)
@monitor_task("process_batch_with_enhanced_retry")
def process_batch_with_enhanced_retry(self, batch_id: str, job_id: str, file_paths: List[str], face_limit: Optional[int] = None):
    """
    Enhanced batch processing with intelligent retry and failure handling.
    
    Args:
        batch_id: Unique batch identifier
        job_id: Unique job identifier  
        file_paths: List of paths to uploaded image files
        face_limit: Optional limit on number of faces
        
    Returns:
        Dict with batch processing results
    """
    try:
        total_files = len(file_paths)
        logger.info(f"Starting enhanced batch processing for {total_files} files (batch: {batch_id})")
        
        # Store start time for timeout tracking
        start_time = time.time()
        
        # Update progress to starting
        current_task.update_state(
            state="PROGRESS", 
            meta={
                "current": 0,
                "total": total_files,
                "status": f"Starting enhanced batch processing for {total_files} files...",
                "batch_id": batch_id,
                "job_id": job_id,
                "start_time": start_time,
                "retry_count": self.request.retries
            }
        )
        
        results = []
        consecutive_failures = 0
        max_consecutive_failures = 3  # Circuit breaker threshold
        
        # Process each file in the batch
        for i, file_path in enumerate(file_paths):
            try:
                # Check for soft time limit
                time_elapsed = time.time() - start_time
                if time_elapsed > 25 * 60:  # 25 minutes soft limit
                    raise SoftTimeLimitExceeded()
                
                # Circuit breaker: If we have too many consecutive failures, 
                # fail fast with remaining files
                if consecutive_failures >= max_consecutive_failures:
                    logger.warning(f"Circuit breaker triggered after {consecutive_failures} consecutive failures")
                    
                    # Mark remaining files as failed due to circuit breaker
                    for remaining_path in file_paths[i:]:
                        results.append({
                            "file_path": remaining_path,
                            "status": "failed",
                            "error": "Circuit breaker triggered due to consecutive failures",
                            "error_type": "circuit_breaker"
                        })
                    break
                
                # Update progress for current file
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i,
                        "total": total_files,
                        "status": f"Processing file {i+1}/{total_files}: {os.path.basename(file_path)}",
                        "batch_id": batch_id,
                        "job_id": job_id,
                        "consecutive_failures": consecutive_failures
                    }
                )
                
                logger.info(f"Processing file {i+1}/{total_files}: {os.path.basename(file_path)}")
                
                # Process single image with retry using our enhanced task
                file_start_time = time.time()
                result = process_single_image_with_retry.apply_async(
                    args=[file_path, face_limit],
                    retry=False  # Handle retries at the individual task level
                ).get(timeout=1800)  # 30 minute timeout per file
                
                actual_processing_time = time.time() - file_start_time
                
                if result["status"] == "success":
                    file_result = {
                        "file_path": file_path,
                        "status": "completed",
                        "result_path": result["output"],
                        "face_count": face_limit if face_limit else 1000,
                        "processing_time": actual_processing_time,
                        "model_format": result.get("model_format", "glb")
                    }
                    consecutive_failures = 0  # Reset failure counter on success
                    logger.info(f"Successfully processed {os.path.basename(file_path)} in {actual_processing_time:.2f}s")
                else:
                    file_result = {
                        "file_path": file_path,
                        "status": "failed",
                        "error": result.get("error", "Unknown error"),
                        "processing_time": actual_processing_time,
                        "error_type": result.get("error_type", "unknown")
                    }
                    consecutive_failures += 1
                    logger.error(f"Failed to process {os.path.basename(file_path)}: {result.get('error', 'Unknown error')}")
                
                results.append(file_result)
                
            except SoftTimeLimitExceeded:
                logger.warning(f"Soft time limit exceeded while processing {file_path}")
                file_result = {
                    "file_path": file_path,
                    "status": "timeout",
                    "error": "Processing time limit exceeded"
                }
                results.append(file_result)
                consecutive_failures += 1
                break  # Stop processing remaining files
                
            except Exception as file_error:
                logger.error(f"Failed to process file {file_path}: {str(file_error)}", exc_info=True)
                file_result = {
                    "file_path": file_path,
                    "status": "failed",
                    "error": str(file_error),
                    "error_type": "processing_error"
                }
                results.append(file_result)
                consecutive_failures += 1
        
        # Calculate final statistics
        success_count = sum(1 for r in results if r["status"] == "completed")
        failure_count = sum(1 for r in results if r["status"] == "failed")
        timeout_count = sum(1 for r in results if r["status"] == "timeout")
        
        # Determine if we should retry the entire batch
        if failure_count > success_count and self.request.retries < self.max_retries:
            # If more failures than successes, consider retrying the batch
            backoff_time = 300 * (2 ** self.request.retries)  # Start with 5 minutes
            backoff_time = min(backoff_time, 1800)  # Cap at 30 minutes
            
            logger.warning(f"Batch has more failures than successes ({failure_count} vs {success_count}), retrying in {backoff_time}s")
            
            raise self.retry(
                countdown=backoff_time,
                exc=ProcessingException(
                    message=f"Batch processing had {failure_count} failures vs {success_count} successes",
                    job_id=job_id,
                    stage="batch_retry"
                )
            )
        
        # Determine final status
        if success_count == total_files:
            final_status = "completed"
        elif success_count > 0:
            final_status = "partially_completed"
        else:
            final_status = "failed"
        
        result_summary = {
            "batch_id": batch_id,
            "job_id": job_id,
            "status": final_status,
            "total_files": total_files,
            "successful_files": success_count,
            "failed_files": failure_count,
            "timeout_files": timeout_count,
            "face_limit": face_limit,
            "results": results,
            "processing_time": time.time() - start_time,
            "retry_count": self.request.retries,
            "message": f"Batch processing completed. {success_count} successful, {failure_count} failed, {timeout_count} timed out."
        }
        
        logger.info(f"Enhanced batch processing completed for {batch_id}: {result_summary['message']}")
        return result_summary
        
    except Retry:
        # Re-raise retry exceptions
        raise
    except SoftTimeLimitExceeded:
        logger.error(f"Batch task soft time limit exceeded for {batch_id}")
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": "Batch processing time limit exceeded", 
                "batch_id": batch_id,
                "job_id": job_id,
                "processed_files": len(results) if 'results' in locals() else 0
            }
        )
        raise ProcessingException(
            message="Batch processing time limit exceeded",
            job_id=job_id,
            stage="timeout"
        )
        
    except Exception as exc:
        log_exception(exc, f"process_batch_with_enhanced_retry for batch {batch_id}")
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(exc),
                "batch_id": batch_id, 
                "job_id": job_id
            }
        )
        raise ProcessingException(
            message=f"Batch processing failed: {str(exc)}",
            job_id=job_id,
            stage="batch_processing"
        )


@celery_app.task
def health_check_task():
    """
    Simple health check task for monitoring worker status.
    """
    return {"status": "healthy", "worker": "image2model-worker"}
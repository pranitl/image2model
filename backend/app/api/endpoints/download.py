"""
Download endpoints for generated 3D model files.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

from app.core.config import settings
from app.middleware.auth import RequireAuth, OptionalAuth

logger = logging.getLogger(__name__)

router = APIRouter()


class FileInfo(BaseModel):
    """Model file information."""
    filename: str
    size: int
    mime_type: str
    created_time: float
    rendered_image: Optional[Dict[str, Any]] = None  # Optional rendered image data


class JobFilesResponse(BaseModel):
    """Response model for job files listing."""
    job_id: str
    files: List[FileInfo]
    download_urls: List[str]
    total_files: int
    model_type: Optional[str] = None  # Optional model type for client rendering


def _validate_job_id(job_id: str) -> None:
    """
    Validate job ID format for security.
    
    Args:
        job_id: Job identifier to validate
        
    Raises:
        HTTPException: If job_id format is invalid
    """
    if not job_id or len(job_id) > 100:  # Reasonable length limit
        raise HTTPException(status_code=400, detail="Invalid job ID length")
    
    # Allow alphanumeric, hyphens, and underscores only
    if not job_id.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(status_code=400, detail="Invalid job ID format")


def _validate_filename(filename: str) -> None:
    """
    Validate filename for security.
    
    Args:
        filename: Filename to validate
        
    Raises:
        HTTPException: If filename is invalid
    """
    if not filename or len(filename) > 255:  # Filesystem limit
        raise HTTPException(status_code=400, detail="Invalid filename length")
    
    # Check for directory traversal attempts
    dangerous_patterns = ['..', '/', '\\', '\0', '\r', '\n']
    if any(pattern in filename for pattern in dangerous_patterns):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Check file extension - allow common 3D formats
    file_extension = os.path.splitext(filename)[1].lower()
    allowed_extensions = ['.glb', '.obj', '.ply', '.stl', '.fbx', '.usdz']
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file format. Supported formats: {', '.join(allowed_extensions)}"
        )


def _validate_file_path(file_path: str, base_dir: str) -> None:
    """
    Validate file path is within allowed directory.
    
    Args:
        file_path: File path to validate
        base_dir: Base directory that path must be within
        
    Raises:
        HTTPException: If path is outside base directory
    """
    abs_file_path = os.path.abspath(file_path)
    abs_base_dir = os.path.abspath(base_dir)
    
    if not abs_file_path.startswith(abs_base_dir):
        logger.warning(f"Path traversal attempt: {file_path}")
        raise HTTPException(status_code=403, detail="Access denied")


@router.get("/download/direct/{filename}")
async def download_file_direct(filename: str, request: Request):
    """
    Download a file directly by filename from the results directory.
    
    Args:
        filename: Name of the file to download
        request: FastAPI request object for logging
        
    Returns:
        FileResponse with the requested file
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Log download attempt
        logger.info(f"Direct download request from {client_ip} for file {filename}")
        
        # Validate filename using existing security helper
        _validate_filename(filename)
        
        # Construct file path - look directly in results directory
        results_dir = settings.RESULTS_DIR if hasattr(settings, 'RESULTS_DIR') else 'results'
        file_path = os.path.join(results_dir, filename)
        
        # Validate file path security
        _validate_file_path(file_path, results_dir)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path} (requested by {client_ip})")
            raise HTTPException(status_code=404, detail="File not found")
        
        # Log successful access
        file_size = os.path.getsize(file_path)
        logger.info(f"Serving file {filename} ({file_size} bytes) to {client_ip}")
        
        # Determine MIME type
        file_extension = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.glb': 'model/gltf-binary',
            '.obj': 'model/obj',
            '.ply': 'model/ply',
            '.stl': 'model/stl',
            '.fbx': 'model/fbx',
            '.usdz': 'model/vnd.usdz+zip'
        }
        mime_type = mime_types.get(file_extension, "application/octet-stream")
        
        # Security headers
        security_headers = {
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Cache-Control": "public, max-age=3600",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'none'",
            "X-Download-Options": "noopen",
            "Referrer-Policy": "no-referrer"
        }
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=mime_type,
            headers=security_headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error serving file {filename} to {client_ip}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# IMPORTANT: This route must come BEFORE the generic /{filename} route
@router.get("/download/{job_id}/all", response_model=JobFilesResponse)
async def list_job_files(job_id: str, request: Request):
    """
    List all available files for a specific job.
    
    Args:
        job_id: Unique job identifier
        request: FastAPI request object for logging
        
    Returns:
        List of available files with metadata and download URLs
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Log listing request
        logger.info(f"File listing request from {client_ip} for job {job_id}")
        
        # Validate job ID using security helper
        _validate_job_id(job_id)
        
        # First, try to get job result from job store (FAL.AI results)
        from app.core.job_store import job_store
        job_result = job_store.get_job_result(job_id)
        
        logger.info(f"Job store result for {job_id}: {job_result is not None}")
        
        # If not in job store, try to get from Celery task result
        if not job_result:
            try:
                from app.core.celery_app import celery_app
                # Look for any recent task with this job_id in the result
                # This is a bit hacky but works for now
                inspect = celery_app.control.inspect()
                active_tasks = inspect.active()
                
                # Also check Redis directly for completed tasks
                from celery.result import AsyncResult
                # We need to find the task ID for this job
                # For now, check if we stored it in upload response
                # As a fallback, scan recent results
                
                # Try Redis backend directly
                import redis
                r = redis.Redis(host='redis', port=6379, db=0)
                
                # Look for keys matching celery-task-meta-*
                for key in r.scan_iter(match="celery-task-meta-*", count=100):
                    try:
                        task_data = r.get(key)
                        if task_data:
                            import json
                            result = json.loads(task_data)
                            if result.get('status') == 'SUCCESS':
                                task_result = result.get('result', {})
                                if task_result.get('job_id') == job_id and 'job_result' in task_result:
                                    job_result = task_result['job_result']
                                    logger.info(f"Found job result in Celery backend for {job_id}")
                                    break
                    except Exception as e:
                        continue
                        
            except Exception as e:
                logger.warning(f"Failed to check Celery results: {e}")
        
        if job_result:
            # We have FAL.AI results - return them directly
            logger.info(f"Found FAL.AI results for job {job_id}")
            
            files = []
            download_urls = []
            
            for file_data in job_result.get("files", []):
                file_info = FileInfo(
                    filename=file_data.get("filename", "model.glb"),
                    size=file_data.get("file_size", 0),
                    mime_type=file_data.get("content_type", "model/gltf-binary"),
                    created_time=0,  # FAL.AI doesn't provide creation time
                    rendered_image=file_data.get("rendered_image")  # Include preview image
                )
                files.append(file_info)
                
                # Use the direct FAL.AI URL
                download_urls.append(file_data.get("model_url", ""))
            
            # Log successful listing
            logger.info(f"Listed {len(files)} FAL.AI files for job {job_id} to {client_ip}")
            
            return JobFilesResponse(
                job_id=job_id,
                files=files,
                download_urls=download_urls,
                total_files=len(files),
                model_type=job_result.get("model_type")  # Include model type if available
            )
        
        # Fallback to local file system (for backward compatibility)
        # Check if job directory exists
        job_dir = os.path.join(settings.OUTPUT_DIR, job_id)
        if not os.path.exists(job_dir):
            logger.warning(f"Job not found in store or filesystem: {job_id} (requested by {client_ip})")
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Validate job directory path security
        _validate_file_path(job_dir, settings.OUTPUT_DIR)
    
        # Get all supported model files in the job directory
        files = []
        download_urls = []
        
        for filename in os.listdir(job_dir):
            try:
                # Validate filename before processing
                _validate_filename(filename)
                
                file_path = os.path.join(job_dir, filename)
                
                # Only include supported file types
                allowed_extensions = ('.glb', '.obj', '.ply', '.stl', '.fbx', '.usdz')
                if filename.lower().endswith(allowed_extensions):
                    file_stat = os.stat(file_path)
                    
                    # Determine MIME type
                    file_extension = os.path.splitext(filename)[1].lower()
                    mime_types = {
                        '.glb': 'model/gltf-binary',
                        '.obj': 'model/obj',
                        '.ply': 'model/ply',
                        '.stl': 'model/stl',
                        '.fbx': 'model/fbx',
                        '.usdz': 'model/vnd.usdz+zip'
                    }
                    mime_type = mime_types.get(file_extension, "application/octet-stream")
                    
                    file_info = FileInfo(
                        filename=filename,
                        size=file_stat.st_size,
                        mime_type=mime_type,
                        created_time=file_stat.st_mtime
                    )
                    
                    files.append(file_info)
                    download_urls.append(f"/api/v1/download/{job_id}/{filename}")
                    
            except (OSError, IOError, HTTPException):
                # Skip files that can't be accessed or have invalid names
                continue
        
        # Log successful listing
        logger.info(f"Listed {len(files)} local files for job {job_id} to {client_ip}")
        
        return JobFilesResponse(
            job_id=job_id,
            files=files,
            download_urls=download_urls,
            total_files=len(files)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (already logged)
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error listing files for job {job_id} to {client_ip}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error"
        )


@router.get("/download/{job_id}/model")
async def download_model_direct(job_id: str, request: Request, api_key: str = OptionalAuth):
    """
    Download the primary 3D model file from a completed job via redirect.
    
    This endpoint is optimized for FAL.AI URLs and will redirect to the
    model URL directly, avoiding local file storage.
    
    Args:
        job_id: Unique job identifier
        request: FastAPI request object for logging
        
    Returns:
        RedirectResponse to the FAL.AI model URL
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Log download attempt
        logger.info(f"Direct model download request from {client_ip} for job {job_id}")
        
        # Validate job ID
        _validate_job_id(job_id)
        
        # Check job ownership if API key is provided
        if api_key and settings.ENVIRONMENT == "production":
            from app.core.session_store import session_store
            if not session_store.verify_job_access(job_id, api_key):
                logger.warning(f"Unauthorized access attempt for job {job_id} by {client_ip}")
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Get job result from job store
        from app.core.job_store import job_store
        
        job_result = job_store.get_job_result(job_id)
        if not job_result:
            logger.warning(f"Job result not found for {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get the first file's model URL
        files = job_result.get("files", [])
        if not files:
            logger.warning(f"No files found for job {job_id}")
            raise HTTPException(status_code=404, detail="No model files found")
        
        # Get the primary model file (first one)
        primary_file = files[0]
        model_url = primary_file.get("model_url")
        
        if not model_url:
            logger.warning(f"No model URL found for job {job_id}")
            raise HTTPException(status_code=404, detail="Model URL not available")
        
        logger.info(f"Redirecting to FAL.AI URL for job {job_id}")
        
        # Return a redirect response to the FAL.AI URL
        return RedirectResponse(
            url=model_url, 
            status_code=302,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in direct download for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/download/{job_id}/{filename}")
async def download_model(job_id: str, filename: str, request: Request, api_key: str = OptionalAuth):
    """
    Download a single 3D model file from a completed job.
    
    Args:
        job_id: Unique job identifier
        filename: Name of the file to download
        request: FastAPI request object for logging
        
    Returns:
        FileResponse with the requested model file
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Log download attempt
        logger.info(f"Download request from {client_ip} for job {job_id}, file {filename}")
        
        # Validate inputs using security helpers
        _validate_job_id(job_id)
        _validate_filename(filename)
        
        # Check job ownership if API key is provided
        if api_key and settings.ENVIRONMENT == "production":
            from app.core.session_store import session_store
            if not session_store.verify_job_access(job_id, api_key):
                logger.warning(f"Unauthorized access attempt for job {job_id} by {client_ip}")
                raise HTTPException(status_code=403, detail="Access denied")
        
        # First, check if we have a FAL.AI URL for this job
        from app.core.job_store import job_store
        
        job_result = job_store.get_job_result(job_id)
        if job_result:
            # Look for the file in FAL.AI results
            for file_data in job_result.get("files", []):
                if file_data.get("filename") == filename and file_data.get("model_url"):
                    # Found FAL.AI URL - redirect to it
                    fal_url = file_data["model_url"]
                    logger.info(f"Redirecting to FAL.AI URL for {filename}")
                    
                    # Return a redirect response to the FAL.AI URL
                    # Using 302 (temporary redirect) as the URL might expire
                    return RedirectResponse(
                        url=fal_url, 
                        status_code=302,
                        headers={
                            "Cache-Control": "no-cache, no-store, must-revalidate",
                            "Pragma": "no-cache",
                            "Expires": "0"
                        }
                    )
        
        # Fallback to local file system (for backward compatibility)
        # Construct file path
        file_path = os.path.join(settings.OUTPUT_DIR, job_id, filename)
        
        # Validate file path security
        _validate_file_path(file_path, settings.OUTPUT_DIR)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path} (requested by {client_ip})")
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check file size for large file handling
        file_stat = os.stat(file_path)
        file_size = file_stat.st_size
        
        # Log successful access
        logger.info(f"Serving file {filename} ({file_size} bytes) to {client_ip}")
        
        # Determine MIME type based on file extension
        file_extension = os.path.splitext(filename)[1].lower()
        mime_types = {
            '.glb': 'model/gltf-binary',
            '.obj': 'model/obj',
            '.ply': 'model/ply',
            '.stl': 'model/stl',
            '.fbx': 'model/fbx',
            '.usdz': 'model/vnd.usdz+zip'
        }
        mime_type = mime_types.get(file_extension, "application/octet-stream")
        
        # Enhanced security headers
        security_headers = {
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "X-Content-Type-Options": "nosniff",  # Prevent MIME sniffing
            "X-Frame-Options": "DENY",  # Prevent embedding in frames
            "Content-Security-Policy": "default-src 'none'",  # Strict CSP
            "X-Download-Options": "noopen",  # IE-specific security
            "Referrer-Policy": "no-referrer"  # Privacy protection
        }
        
        # Return file with enhanced security headers
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=mime_type,
            headers=security_headers
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (already logged in validation functions)
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error serving file {filename} to {client_ip}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/debug/job/{job_id}")
async def debug_job_store(job_id: str):
    """Debug endpoint to check job store connectivity and data."""
    import redis
    from app.core.config import settings
    
    debug_info = {
        "job_id": job_id,
        "redis_url": settings.CELERY_RESULT_BACKEND,
        "job_store_result": None,
        "direct_redis_result": None,
        "redis_keys": [],
        "error": None
    }
    
    try:
        # Try job store
        from app.core.job_store import job_store
        job_result = job_store.get_job_result(job_id)
        debug_info["job_store_result"] = bool(job_result)
        
        # Try direct Redis connection
        r = redis.from_url(settings.CELERY_RESULT_BACKEND, decode_responses=True)
        key = f"job_result:{job_id}"
        direct_result = r.get(key)
        debug_info["direct_redis_result"] = bool(direct_result)
        
        # List some keys
        debug_info["redis_keys"] = list(r.scan_iter(match="job_result:*", count=5))[:5]
        
    except Exception as e:
        debug_info["error"] = str(e)
        logger.error(f"Debug endpoint error: {e}", exc_info=True)
    
    return debug_info
"""
Download endpoints for generated 3D model files.
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class FileInfo(BaseModel):
    """Model file information."""
    filename: str
    size: int
    mime_type: str
    created_time: float


class JobFilesResponse(BaseModel):
    """Response model for job files listing."""
    job_id: str
    files: List[FileInfo]
    download_urls: List[str]
    total_files: int


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
    
    # Check file extension
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in ['.glb', '.obj']:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file format. Only .glb and .obj files are supported"
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
        mime_type = "application/octet-stream"
        if file_extension == '.glb':
            mime_type = "model/gltf-binary"
        elif file_extension == '.obj':
            mime_type = "model/obj"
        
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


@router.get("/download/{job_id}/{filename}")
async def download_model(job_id: str, filename: str, request: Request):
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
        mime_type = "application/octet-stream"  # Default
        if file_extension == '.glb':
            mime_type = "model/gltf-binary"
        elif file_extension == '.obj':
            mime_type = "model/obj"
        
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
                    created_time=0  # FAL.AI doesn't provide creation time
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
                total_files=len(files)
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
                if filename.lower().endswith(('.glb', '.obj')):
                    file_stat = os.stat(file_path)
                    
                    # Determine MIME type
                    file_extension = os.path.splitext(filename)[1].lower()
                    mime_type = "application/octet-stream"
                    if file_extension == '.glb':
                        mime_type = "model/gltf-binary"
                    elif file_extension == '.obj':
                        mime_type = "model/obj"
                    
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
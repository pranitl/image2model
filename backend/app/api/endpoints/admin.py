"""
Admin endpoints for file management and system monitoring.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from pydantic import BaseModel

from app.core.config import settings
from app.middleware.auth import RequireAdminAuth
from app.workers.cleanup import (
    cleanup_old_files,
    get_disk_usage,
    cleanup_job_files,
    get_directory_size,
    count_files_in_directory
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[RequireAdminAuth])


class CleanupRequest(BaseModel):
    """Request model for cleanup operations."""
    hours: int = 24
    dry_run: bool = False


class JobCleanupRequest(BaseModel):
    """Request model for job-specific cleanup."""
    job_id: str


class DiskUsageResponse(BaseModel):
    """Response model for disk usage information."""
    upload_dir: Dict[str, Any]
    output_dir: Dict[str, Any]
    timestamp: str


class CleanupResponse(BaseModel):
    """Response model for cleanup operations."""
    freed_space_mb: float
    files_removed: int
    directories_removed: int
    errors: List[str]
    cleanup_hours: int
    timestamp: str


class FileInfo(BaseModel):
    """File information model."""
    path: str
    size_mb: float
    modified: str
    is_directory: bool
    file_count: Optional[int] = None


class DirectoryListResponse(BaseModel):
    """Response model for directory listing."""
    directory: str
    total_size_mb: float
    total_files: int
    items: List[FileInfo]


@router.get("/disk-usage", response_model=DiskUsageResponse)
async def get_disk_usage_endpoint():
    """
    Get current disk usage statistics for upload and output directories.
    """
    try:
        usage_info = get_disk_usage.delay().get()
        return DiskUsageResponse(**usage_info)
    except Exception as e:
        logger.error(f"Error getting disk usage: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get disk usage information")


@router.post("/cleanup", response_model=CleanupResponse)
async def trigger_cleanup(
    background_tasks: BackgroundTasks,
    request: CleanupRequest = CleanupRequest()
):
    """
    Trigger manual cleanup of old files.
    
    Args:
        request: Cleanup configuration including hours threshold and dry_run flag
    """
    if request.dry_run:
        # For dry run, we'll simulate the cleanup without actually removing files
        try:
            # This would need a separate dry_run implementation
            raise HTTPException(
                status_code=501, 
                detail="Dry run mode not yet implemented"
            )
        except Exception as e:
            logger.error(f"Error in dry run cleanup: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to perform dry run cleanup")
    else:
        try:
            # Run cleanup in background
            task = cleanup_old_files.delay(hours=request.hours)
            result = task.get()  # Wait for completion
            return CleanupResponse(**result)
        except Exception as e:
            logger.error(f"Error triggering cleanup: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to trigger cleanup")


@router.post("/cleanup-job", response_model=Dict[str, Any])
async def cleanup_specific_job(request: JobCleanupRequest):
    """
    Clean up files for a specific job ID.
    
    Args:
        request: Job cleanup request with job_id
    """
    try:
        task = cleanup_job_files.delay(request.job_id)
        result = task.get()
        return result
    except Exception as e:
        logger.error(f"Error cleaning up job {request.job_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to cleanup job {request.job_id}"
        )


@router.get("/list-files", response_model=DirectoryListResponse)
async def list_files(
    directory: str = Query(..., description="Directory to list (uploads or results)"),
    limit: int = Query(100, description="Maximum number of items to return")
):
    """
    List files in a specific directory with size and modification information.
    
    Args:
        directory: Directory to list ('uploads' or 'results')
        limit: Maximum number of items to return
    """
    # Validate directory parameter
    if directory not in ["uploads", "results"]:
        raise HTTPException(
            status_code=400, 
            detail="Directory must be 'uploads' or 'results'"
        )
    
    # Map to actual directory paths
    dir_map = {
        "uploads": settings.UPLOAD_DIR,
        "results": settings.OUTPUT_DIR
    }
    
    target_dir = dir_map[directory]
    
    if not os.path.exists(target_dir):
        raise HTTPException(
            status_code=404, 
            detail=f"Directory {directory} does not exist"
        )
    
    try:
        items = []
        total_size = 0
        total_files = 0
        
        # List items in directory
        for item_name in sorted(os.listdir(target_dir))[:limit]:
            item_path = os.path.join(target_dir, item_name)
            
            try:
                stat_info = os.stat(item_path)
                modified = str(stat_info.st_mtime)
                
                if os.path.isdir(item_path):
                    dir_size = get_directory_size(item_path)
                    file_count = count_files_in_directory(item_path)
                    
                    items.append(FileInfo(
                        path=item_name,
                        size_mb=dir_size / (1024 * 1024),
                        modified=modified,
                        is_directory=True,
                        file_count=file_count
                    ))
                    
                    total_size += dir_size
                    total_files += file_count
                else:
                    file_size = stat_info.st_size
                    
                    items.append(FileInfo(
                        path=item_name,
                        size_mb=file_size / (1024 * 1024),
                        modified=modified,
                        is_directory=False
                    ))
                    
                    total_size += file_size
                    total_files += 1
                    
            except (OSError, IOError) as e:
                logger.warning(f"Could not access {item_path}: {str(e)}")
                continue
        
        return DirectoryListResponse(
            directory=directory,
            total_size_mb=total_size / (1024 * 1024),
            total_files=total_files,
            items=items
        )
        
    except Exception as e:
        logger.error(f"Error listing files in {directory}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to list files in {directory}"
        )


@router.delete("/delete-job/{job_id}")
async def delete_job_files(job_id: str):
    """
    Delete all files associated with a specific job ID.
    
    Args:
        job_id: The job ID whose files should be deleted
    """
    try:
        task = cleanup_job_files.delay(job_id)
        result = task.get()
        
        if result["files_removed"] == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"No files found for job {job_id}"
            )
        
        return {
            "message": f"Successfully deleted files for job {job_id}",
            "freed_space_mb": result["freed_space_mb"],
            "files_removed": result["files_removed"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job files {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to delete files for job {job_id}"
        )


@router.get("/system-health")
async def get_system_health():
    """
    Get overall system health including disk usage and cleanup status.
    """
    try:
        # Get disk usage
        usage_info = get_disk_usage.delay().get()
        
        # Calculate health metrics
        health_status = "healthy"
        warnings = []
        
        for dir_name, dir_info in usage_info.items():
            if dir_name == "timestamp":
                continue
                
            if "disk_usage_percent" in dir_info:
                usage_percent = dir_info["disk_usage_percent"]
                
                if usage_percent > 90:
                    health_status = "critical"
                    warnings.append(f"{dir_name}: Disk usage critical ({usage_percent:.1f}%)")
                elif usage_percent > 80:
                    if health_status == "healthy":
                        health_status = "warning"
                    warnings.append(f"{dir_name}: Disk usage high ({usage_percent:.1f}%)")
        
        return {
            "status": health_status,
            "disk_usage": usage_info,
            "warnings": warnings,
            "timestamp": usage_info.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to get system health information"
        )
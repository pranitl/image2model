"""
File cleanup worker for removing old temporary files and managing disk space.
"""

import os
import shutil
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_old_files(hours: int = 24) -> Dict[str, Any]:
    """
    Remove files older than specified hours.
    
    Args:
        hours: Number of hours after which files should be removed (default: 24)
        
    Returns:
        Dict containing cleanup statistics
    """
    cutoff_time = time.time() - (hours * 60 * 60)
    
    directories_to_clean = [
        settings.UPLOAD_DIR,
        settings.OUTPUT_DIR
    ]
    
    total_freed = 0
    total_files_removed = 0
    total_dirs_removed = 0
    errors = []
    
    logger.info(f"Starting cleanup of files older than {hours} hours")
    
    for base_dir in directories_to_clean:
        if not os.path.exists(base_dir):
            logger.warning(f"Directory does not exist: {base_dir}")
            continue
            
        logger.info(f"Cleaning directory: {base_dir}")
        
        try:
            for item in os.listdir(base_dir):
                item_path = os.path.join(base_dir, item)
                
                # Check if item is old enough to be cleaned
                if os.path.getmtime(item_path) < cutoff_time:
                    try:
                        if os.path.isdir(item_path):
                            # Directory cleanup
                            dir_size = get_directory_size(item_path)
                            file_count = count_files_in_directory(item_path)
                            
                            shutil.rmtree(item_path)
                            total_freed += dir_size
                            total_files_removed += file_count
                            total_dirs_removed += 1
                            
                            logger.info(f"Removed old directory: {item_path} "
                                      f"({file_count} files, {dir_size / (1024*1024):.2f} MB)")
                                      
                        elif os.path.isfile(item_path):
                            # Single file cleanup
                            file_size = os.path.getsize(item_path)
                            os.remove(item_path)
                            total_freed += file_size
                            total_files_removed += 1
                            
                            logger.info(f"Removed old file: {item_path} "
                                      f"({file_size / (1024*1024):.2f} MB)")
                                      
                    except Exception as e:
                        error_msg = f"Error removing {item_path}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        
        except Exception as e:
            error_msg = f"Error processing directory {base_dir}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    # Log summary
    freed_mb = total_freed / (1024 * 1024)
    logger.info(f"Cleanup completed. Freed {freed_mb:.2f} MB, "
                f"removed {total_files_removed} files and {total_dirs_removed} directories")
    
    if errors:
        logger.warning(f"Cleanup completed with {len(errors)} errors")
    
    return {
        "freed_space_mb": freed_mb,
        "files_removed": total_files_removed,
        "directories_removed": total_dirs_removed,
        "errors": errors,
        "cleanup_hours": hours,
        "timestamp": datetime.now().isoformat()
    }


@celery_app.task
def get_disk_usage() -> Dict[str, Any]:
    """
    Get disk usage statistics for upload and output directories.
    
    Returns:
        Dict containing disk usage information
    """
    usage_info = {}
    
    directories = {
        "upload_dir": settings.UPLOAD_DIR,
        "output_dir": settings.OUTPUT_DIR
    }
    
    for name, path in directories.items():
        if os.path.exists(path):
            total_size = get_directory_size(path)
            file_count = count_files_in_directory(path)
            dir_count = count_directories_in_path(path)
            
            # Get disk space for the filesystem containing this directory
            statvfs = os.statvfs(path)
            disk_total = statvfs.f_frsize * statvfs.f_blocks
            disk_free = statvfs.f_frsize * statvfs.f_available
            disk_used = disk_total - disk_free
            
            usage_info[name] = {
                "path": path,
                "size_mb": total_size / (1024 * 1024),
                "file_count": file_count,
                "directory_count": dir_count,
                "disk_total_gb": disk_total / (1024 * 1024 * 1024),
                "disk_used_gb": disk_used / (1024 * 1024 * 1024),
                "disk_free_gb": disk_free / (1024 * 1024 * 1024),
                "disk_usage_percent": (disk_used / disk_total) * 100
            }
        else:
            usage_info[name] = {
                "path": path,
                "exists": False,
                "error": "Directory does not exist"
            }
    
    usage_info["timestamp"] = datetime.now().isoformat()
    
    return usage_info


@celery_app.task
def cleanup_job_files(job_id: str) -> Dict[str, Any]:
    """
    Remove files for a specific job ID.
    
    Args:
        job_id: The job ID whose files should be removed
        
    Returns:
        Dict containing cleanup statistics for the job
    """
    total_freed = 0
    total_files_removed = 0
    errors = []
    
    directories_to_check = [
        settings.UPLOAD_DIR,
        settings.OUTPUT_DIR
    ]
    
    logger.info(f"Cleaning up files for job: {job_id}")
    
    for base_dir in directories_to_check:
        job_path = os.path.join(base_dir, job_id)
        
        if os.path.exists(job_path):
            try:
                if os.path.isdir(job_path):
                    dir_size = get_directory_size(job_path)
                    file_count = count_files_in_directory(job_path)
                    
                    shutil.rmtree(job_path)
                    total_freed += dir_size
                    total_files_removed += file_count
                    
                    logger.info(f"Removed job directory: {job_path} "
                              f"({file_count} files, {dir_size / (1024*1024):.2f} MB)")
                              
                elif os.path.isfile(job_path):
                    file_size = os.path.getsize(job_path)
                    os.remove(job_path)
                    total_freed += file_size
                    total_files_removed += 1
                    
                    logger.info(f"Removed job file: {job_path} "
                              f"({file_size / (1024*1024):.2f} MB)")
                              
            except Exception as e:
                error_msg = f"Error removing {job_path}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
    
    freed_mb = total_freed / (1024 * 1024)
    logger.info(f"Job cleanup completed for {job_id}. "
                f"Freed {freed_mb:.2f} MB, removed {total_files_removed} files")
    
    return {
        "job_id": job_id,
        "freed_space_mb": freed_mb,
        "files_removed": total_files_removed,
        "errors": errors,
        "timestamp": datetime.now().isoformat()
    }


def get_directory_size(path: str) -> int:
    """
    Calculate the total size of a directory and all its contents.
    
    Args:
        path: Path to the directory
        
    Returns:
        Total size in bytes
    """
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(filepath)
                except (OSError, IOError):
                    # Skip files that can't be accessed
                    pass
    except (OSError, IOError):
        # Handle permission errors or other OS errors
        pass
    return total


def count_files_in_directory(path: str) -> int:
    """
    Count the number of files in a directory and all subdirectories.
    
    Args:
        path: Path to the directory
        
    Returns:
        Total number of files
    """
    count = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            count += len(filenames)
    except (OSError, IOError):
        # Handle permission errors or other OS errors
        pass
    return count


def count_directories_in_path(path: str) -> int:
    """
    Count the number of subdirectories in a path.
    
    Args:
        path: Path to count directories in
        
    Returns:
        Number of directories
    """
    count = 0
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                count += 1
    except (OSError, IOError):
        # Handle permission errors or other OS errors
        pass
    return count


def is_file_in_use(filepath: str) -> bool:
    """
    Check if a file is currently in use (basic check for Linux/Unix systems).
    
    Args:
        filepath: Path to the file to check
        
    Returns:
        True if file appears to be in use, False otherwise
    """
    try:
        # Try to rename the file to itself (this will fail if file is in use)
        os.rename(filepath, filepath)
        return False
    except OSError:
        return True
"""
Redis-based progress tracking for parallel file processing.

This module provides utilities to track progress of individual files
in a batch processing job using Redis for atomic updates.
"""

import json
import logging
from typing import Dict, Any, Optional, List
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Track progress of batch processing jobs in Redis.
    
    Uses Redis for atomic operations to ensure thread-safe updates
    from multiple parallel workers.
    """
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = redis.from_url(
            settings.CELERY_RESULT_BACKEND,
            decode_responses=True
        )
        self.key_prefix = "progress:"
        self.ttl = 3600  # 1 hour TTL for progress data
    
    def _get_key(self, job_id: str) -> str:
        """Get Redis key for a job."""
        return f"{self.key_prefix}{job_id}"
    
    def init_job(self, job_id: str, file_paths: List[str]) -> None:
        """
        Initialize progress tracking for a new job.
        
        Args:
            job_id: Unique job identifier
            file_paths: List of file paths being processed
        """
        key = self._get_key(job_id)
        
        # Initialize progress data
        progress_data = {
            "total_files": len(file_paths),
            "completed_files": 0,
            "failed_files": 0,
            "files": {
                path: {
                    "status": "pending",
                    "progress": 0,
                    "filename": path.split("/")[-1],
                    "error": None
                }
                for path in file_paths
            }
        }
        
        # Store in Redis with TTL
        self.redis_client.setex(
            key,
            self.ttl,
            json.dumps(progress_data)
        )
        logger.info(f"Initialized progress tracking for job {job_id} with {len(file_paths)} files")
    
    def update_file_progress(self, job_id: str, file_path: str, 
                           status: str, progress: int = 0, error: str = None) -> None:
        """
        Update progress for a specific file.
        
        Args:
            job_id: Job identifier
            file_path: Path of the file being updated
            status: Current status (pending, processing, completed, failed)
            progress: Progress percentage (0-100)
            error: Error message if failed
        """
        key = self._get_key(job_id)
        
        # Get current data
        data_str = self.redis_client.get(key)
        if not data_str:
            logger.warning(f"No progress data found for job {job_id}")
            return
        
        data = json.loads(data_str)
        
        # Update file status
        if file_path in data["files"]:
            old_status = data["files"][file_path]["status"]
            data["files"][file_path]["status"] = status
            data["files"][file_path]["progress"] = progress
            if error:
                data["files"][file_path]["error"] = error
            
            # Update counters
            if old_status != "completed" and status == "completed":
                data["completed_files"] += 1
            elif old_status != "failed" and status == "failed":
                data["failed_files"] += 1
        
        # Save back to Redis
        self.redis_client.setex(
            key,
            self.ttl,
            json.dumps(data)
        )
        logger.debug(f"Updated progress for {file_path}: {status} ({progress}%)")
    
    def get_job_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current progress for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Progress data or None if not found
        """
        key = self._get_key(job_id)
        data_str = self.redis_client.get(key)
        
        if not data_str:
            return None
        
        return json.loads(data_str)
    
    def get_overall_progress(self, job_id: str) -> int:
        """
        Calculate overall progress percentage for a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Overall progress percentage (0-100)
        """
        data = self.get_job_progress(job_id)
        if not data:
            return 0
        
        total_files = data["total_files"]
        if total_files == 0:
            return 100
        
        # Calculate weighted progress
        total_progress = 0
        for file_data in data["files"].values():
            if file_data["status"] == "completed":
                total_progress += 100
            elif file_data["status"] == "failed":
                total_progress += 100  # Count failed as complete
            elif file_data["status"] == "processing":
                total_progress += file_data["progress"]
        
        return int(total_progress / total_files)
    
    def cleanup_job(self, job_id: str) -> None:
        """
        Remove progress data for a completed job.
        
        Args:
            job_id: Job identifier
        """
        key = self._get_key(job_id)
        self.redis_client.delete(key)
        logger.info(f"Cleaned up progress data for job {job_id}")


# Global progress tracker instance
progress_tracker = ProgressTracker()
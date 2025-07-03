"""
Simple in-memory store for FAL.AI job results.
This stores the FAL.AI URLs and metadata for each job.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class JobStore:
    """Thread-safe in-memory store for job results."""
    
    def __init__(self, ttl_hours: int = 24):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._ttl = timedelta(hours=ttl_hours)
    
    def set_job_result(self, job_id: str, result_data: Dict[str, Any]) -> None:
        """Store job result data with timestamp."""
        with self._lock:
            self._store[job_id] = {
                'data': result_data,
                'timestamp': datetime.now()
            }
            logger.info(f"Stored result for job {job_id}: {result_data}")
    
    def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job result if exists and not expired."""
        with self._lock:
            if job_id not in self._store:
                return None
            
            entry = self._store[job_id]
            # Check if expired
            if datetime.now() - entry['timestamp'] > self._ttl:
                del self._store[job_id]
                logger.info(f"Job {job_id} result expired and removed")
                return None
            
            return entry['data']
    
    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count of removed entries."""
        with self._lock:
            now = datetime.now()
            expired_jobs = [
                job_id for job_id, entry in self._store.items()
                if now - entry['timestamp'] > self._ttl
            ]
            
            for job_id in expired_jobs:
                del self._store[job_id]
            
            if expired_jobs:
                logger.info(f"Cleaned up {len(expired_jobs)} expired job results")
            
            return len(expired_jobs)


# Global job store instance
job_store = JobStore()
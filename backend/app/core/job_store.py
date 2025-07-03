"""
Redis-based store for FAL.AI job results.
This stores the FAL.AI URLs and metadata for each job in Redis,
allowing sharing between worker and API processes.
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class JobStore:
    """Redis-based store for job results."""
    
    def __init__(self, ttl_hours: int = 24):
        """Initialize Redis connection for job storage."""
        self._redis_client = redis.from_url(
            settings.CELERY_RESULT_BACKEND,
            decode_responses=True
        )
        self._ttl = int(timedelta(hours=ttl_hours).total_seconds())
        self._key_prefix = "job_result:"
    
    def _get_key(self, job_id: str) -> str:
        """Get Redis key for a job."""
        return f"{self._key_prefix}{job_id}"
    
    def set_job_result(self, job_id: str, result_data: Dict[str, Any]) -> None:
        """Store job result data with TTL."""
        try:
            key = self._get_key(job_id)
            # Store as JSON with TTL
            self._redis_client.setex(
                key,
                self._ttl,
                json.dumps(result_data)
            )
            logger.info(f"Stored result for job {job_id} in Redis")
        except Exception as e:
            logger.error(f"Failed to store job result in Redis: {e}")
            raise
    
    def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job result if exists."""
        try:
            key = self._get_key(job_id)
            data = self._redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job result from Redis: {e}")
            return None
    
    def set_job_metadata(self, job_id: str, metadata: Dict[str, Any]) -> None:
        """Store job metadata separately from results."""
        try:
            key = f"job_metadata:{job_id}"
            # Store metadata with same TTL
            self._redis_client.setex(
                key,
                self._ttl,
                json.dumps(metadata)
            )
            logger.info(f"Stored metadata for job {job_id} in Redis")
        except Exception as e:
            logger.error(f"Failed to store job metadata in Redis: {e}")
    
    def get_job_metadata(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job metadata if exists."""
        try:
            key = f"job_metadata:{job_id}"
            data = self._redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job metadata from Redis: {e}")
            return None
    
    def cleanup_expired(self) -> int:
        """Redis handles expiration automatically via TTL."""
        # No manual cleanup needed with Redis TTL
        return 0


# Global job store instance
job_store = JobStore()
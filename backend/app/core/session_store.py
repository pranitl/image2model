"""
Simple session store for tracking job ownership.
"""

import json
import time
from typing import Optional, Dict, Any
import redis
from app.core.config import settings

class SessionStore:
    """Simple session store using Redis for job ownership tracking."""
    
    def __init__(self, redis_url: str):
        """Initialize session store with Redis connection."""
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.ttl = 86400  # 24 hours
    
    def set_job_owner(self, job_id: str, api_key: str) -> None:
        """
        Associate a job with an API key.
        
        Args:
            job_id: Job identifier
            api_key: API key that created the job
        """
        key = f"job_owner:{job_id}"
        self.redis_client.setex(key, self.ttl, api_key)
    
    def get_job_owner(self, job_id: str) -> Optional[str]:
        """
        Get the API key that owns a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            API key if found, None otherwise
        """
        key = f"job_owner:{job_id}"
        return self.redis_client.get(key)
    
    def verify_job_access(self, job_id: str, api_key: str) -> bool:
        """
        Verify if an API key has access to a job.
        
        Args:
            job_id: Job identifier
            api_key: API key to verify
            
        Returns:
            True if API key owns the job or no owner is set
        """
        owner = self.get_job_owner(job_id)
        
        # If no owner is set (legacy jobs), allow access
        if owner is None:
            return True
        
        # Check if the API key matches
        return owner == api_key
    
    def set_batch_owner(self, batch_id: str, api_key: str) -> None:
        """
        Associate a batch with an API key.
        
        Args:
            batch_id: Batch identifier
            api_key: API key that created the batch
        """
        key = f"batch_owner:{batch_id}"
        self.redis_client.setex(key, self.ttl, api_key)
    
    def get_batch_owner(self, batch_id: str) -> Optional[str]:
        """
        Get the API key that owns a batch.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            API key if found, None otherwise
        """
        key = f"batch_owner:{batch_id}"
        return self.redis_client.get(key)

# Initialize session store
session_store = SessionStore(settings.REDIS_URL)
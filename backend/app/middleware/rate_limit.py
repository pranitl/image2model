"""
Rate limiting middleware and decorators.
"""

from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from functools import wraps
from typing import Callable

from app.core.config import settings

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)


def rate_limit(limit_string: str):
    """
    Rate limiting decorator for endpoints.
    
    Args:
        limit_string: Rate limit string (e.g., "5/minute", "100/hour")
    """
    def decorator(func: Callable) -> Callable:
        # Apply the limiter decorator
        limited = limiter.limit(limit_string)(func)
        
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            return await limited(request, *args, **kwargs)
        
        return wrapper
    return decorator


# Pre-defined rate limits
upload_rate_limit = rate_limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
api_rate_limit = rate_limit(f"{settings.RATE_LIMIT_PER_HOUR}/hour")
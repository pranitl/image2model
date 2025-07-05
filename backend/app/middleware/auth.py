"""
Authentication middleware for API security.
"""

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.core.config import settings

# Security scheme
security = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """Verify API key from Bearer token."""
    if not settings.API_KEY:
        # If no API key is configured, allow access (for development)
        if settings.ENVIRONMENT == "production":
            raise HTTPException(
                status_code=500, 
                detail="API key not configured"
            )
        return "dev-mode"
    
    if credentials.credentials != settings.API_KEY:
        raise HTTPException(
            status_code=403, 
            detail="Invalid API key"
        )
    
    return credentials.credentials


async def verify_admin_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """Verify admin API key from Bearer token."""
    if not settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Admin API key not configured"
        )
    
    if credentials.credentials != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=403, 
            detail="Invalid admin API key"
        )
    
    return credentials.credentials


def get_optional_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[str]:
    """Get API key if provided, but don't require it."""
    if credentials:
        return credentials.credentials
    return None


# Dependency aliases for cleaner usage
RequireAuth = Depends(verify_api_key)
RequireAdminAuth = Depends(verify_admin_api_key)
OptionalAuth = Depends(get_optional_api_key)
"""
Custom exceptions for the Image2Model application.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BaseImageModelException(Exception):
    """Base exception for Image2Model application."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


# Alias for backwards compatibility
Image2ModelException = BaseImageModelException


class APIException(BaseImageModelException):
    """Exception raised for API-related errors."""
    pass


class FALAPIException(BaseImageModelException):
    """Exception raised for FAL.AI API errors."""
    pass


class AuthenticationException(BaseImageModelException):
    """Exception raised for authentication errors."""
    pass


class AuthorizationException(BaseImageModelException):
    """Exception raised for authorization errors."""
    pass


class FileValidationException(BaseImageModelException):
    """Exception raised when file validation fails."""
    pass


class DatabaseException(BaseImageModelException):
    """Exception raised when database operations fail."""
    pass


class ProcessingException(BaseImageModelException):
    """Exception raised when image processing fails."""
    pass


class NetworkException(BaseImageModelException):
    """Exception raised for network-related errors."""
    pass


class RateLimitException(BaseImageModelException):
    """Exception raised for rate limiting errors."""
    pass


class ModelException(BaseImageModelException):
    """Exception raised when model operations fail."""
    pass


class ConfigurationException(BaseImageModelException):
    """Exception raised when configuration is invalid."""
    pass


def log_exception(exception: Exception, context: Optional[str] = None) -> None:
    """Log an exception with optional context."""
    if context:
        logger.error(f"Exception in {context}: {str(exception)}", exc_info=True)
    else:
        logger.error(f"Exception: {str(exception)}", exc_info=True)


def create_error_response(
    error_code: str,
    message: str,
    details: Optional[str] = None,
    status_code: int = 500
) -> dict:
    """Create a standardized error response."""
    response = {
        "error": True,
        "error_code": error_code,
        "message": message
    }
    
    if details:
        response["details"] = details
    
    return response
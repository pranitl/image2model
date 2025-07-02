"""
FastAPI error handlers and middleware for comprehensive error handling.
"""

import logging
import traceback
from typing import Callable, Dict, Any

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    Image2ModelException,
    APIException,
    FALAPIException,
    FileValidationException,
    AuthenticationException,
    AuthorizationException,
    DatabaseException,
    ProcessingException,
    NetworkException,
    RateLimitException,
    log_exception,
    create_error_response
)

logger = logging.getLogger(__name__)


async def image2model_exception_handler(request: Request, exc: Image2ModelException) -> JSONResponse:
    """
    Handle custom Image2Model exceptions.
    
    Args:
        request: The FastAPI request object
        exc: The Image2Model exception
        
    Returns:
        JSON response with error details
    """
    log_exception(exc, f"endpoint {request.url.path}")
    
    response_data = create_error_response(
        error_code=exc.__class__.__name__.upper(),
        message=exc.message if hasattr(exc, 'message') else str(exc),
        details=exc.details if hasattr(exc, 'details') else None
    )
    status_code = getattr(exc, 'status_code', 500)
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handle API exceptions with proper status codes.
    
    Args:
        request: The FastAPI request object
        exc: The API exception
        
    Returns:
        JSON response with error details
    """
    log_exception(exc, f"API endpoint {request.url.path}")
    
    response_data = exc.to_dict()
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle standard HTTP exceptions.
    
    Args:
        request: The FastAPI request object
        exc: The HTTP exception
        
    Returns:
        JSON response with error details
    """
    logger.warning(f"HTTP exception at {request.url.path}: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
            "status_code": exc.status_code,
            "details": {}
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors.
    
    Args:
        request: The FastAPI request object
        exc: The validation error
        
    Returns:
        JSON response with validation error details
    """
    logger.warning(f"Validation error at {request.url.path}: {exc.errors()}")
    
    # Format validation errors for better user experience
    formatted_errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        error_type = error["type"]
        
        formatted_errors.append({
            "field": field,
            "message": message,
            "type": error_type
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "status_code": 422,
            "details": {
                "validation_errors": formatted_errors
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.
    
    Args:
        request: The FastAPI request object
        exc: The unexpected exception
        
    Returns:
        JSON response with generic error message
    """
    log_exception(exc, f"unexpected error at {request.url.path}")
    
    # Log full traceback for debugging
    logger.error(f"Unexpected error traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500,
            "details": {
                "request_path": str(request.url.path),
                "request_method": request.method
            }
        }
    )


def setup_error_handlers(app) -> None:
    """
    Setup all error handlers for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    # Custom exception handlers
    app.add_exception_handler(Image2ModelException, image2model_exception_handler)
    app.add_exception_handler(APIException, api_exception_handler)
    
    # Standard HTTP exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Validation error handler
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # General exception handler (catch-all)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers configured successfully")


# Utility functions for use in endpoints
def handle_file_validation_error(filename: str, error_message: str) -> FileValidationException:
    """
    Create a standardized file validation exception.
    
    Args:
        filename: The name of the file that failed validation
        error_message: The validation error message
        
    Returns:
        FileValidationException with proper details
    """
    return FileValidationException(
        message=f"File validation failed: {error_message}",
        filename=filename,
        details={"validation_error": error_message}
    )


def handle_fal_api_error(response_status: int, response_text: str, is_rate_limited: bool = False) -> FALAPIException:
    """
    Create a standardized FAL.AI API exception.
    
    Args:
        response_status: HTTP status code from FAL.AI API
        response_text: Response text from FAL.AI API
        is_rate_limited: Whether this is a rate limiting error
        
    Returns:
        FALAPIException with proper details
    """
    if is_rate_limited:
        message = "FAL.AI API rate limit exceeded. Please try again later."
    else:
        message = f"FAL.AI API error: {response_text}"
    
    return FALAPIException(
        message=message,
        status_code=response_status,
        is_rate_limited=is_rate_limited,
        details={
            "fal_response_status": response_status,
            "fal_response_text": response_text
        }
    )


def handle_processing_error(job_id: str, stage: str, error_message: str) -> ProcessingException:
    """
    Create a standardized processing exception.
    
    Args:
        job_id: The job ID that failed
        stage: The processing stage where the error occurred
        error_message: The error message
        
    Returns:
        ProcessingException with proper details
    """
    return ProcessingException(
        message=f"Processing failed at {stage}: {error_message}",
        job_id=job_id,
        stage=stage,
        details={"processing_error": error_message}
    )


def handle_network_error(service: str, error_message: str, retry_after: int = None) -> NetworkException:
    """
    Create a standardized network exception.
    
    Args:
        service: The service that had the network error
        error_message: The error message
        retry_after: Suggested retry delay in seconds
        
    Returns:
        NetworkException with proper details
    """
    return NetworkException(
        message=f"Network error communicating with {service}: {error_message}",
        service=service,
        retry_after=retry_after,
        details={"network_error": error_message}
    )


def safe_file_operation(operation: Callable, *args, **kwargs) -> Any:
    """
    Safely execute a file operation with proper error handling.
    
    Args:
        operation: The file operation function to execute
        *args: Positional arguments for the operation
        **kwargs: Keyword arguments for the operation
        
    Returns:
        Result of the operation
        
    Raises:
        DatabaseException: If file operation fails
    """
    try:
        return operation(*args, **kwargs)
    except PermissionError as e:
        raise DatabaseException(
            message="Permission denied for file operation",
            operation=operation.__name__,
            details={"permission_error": str(e)}
        )
    except FileNotFoundError as e:
        raise DatabaseException(
            message="File not found",
            operation=operation.__name__,
            details={"file_not_found": str(e)}
        )
    except OSError as e:
        raise DatabaseException(
            message="File system error",
            operation=operation.__name__,
            details={"os_error": str(e)}
        )
    except Exception as e:
        raise DatabaseException(
            message=f"Unexpected file operation error: {str(e)}",
            operation=operation.__name__,
            details={"unexpected_error": str(e)}
        )
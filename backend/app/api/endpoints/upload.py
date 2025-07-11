"""
File upload endpoints.
"""

import os
import uuid
import logging
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Form, Query, Depends, Request
from pydantic import BaseModel, Field

from app.core.config import settings
from app.middleware.auth import RequireAuth
from app.middleware.rate_limit import upload_rate_limit
from fastapi.security import HTTPAuthorizationCredentials
from app.core.session_store import session_store
from app.core.exceptions import (
    FileValidationException, 
    DatabaseException, 
    ProcessingException,
    log_exception
)
from app.core.error_handlers import (
    handle_file_validation_error,
    safe_file_operation
)
from app.workers.tasks import process_batch, generate_3d_model_task

logger = logging.getLogger(__name__)

router = APIRouter()


class UploadResponse(BaseModel):
    """Upload response model."""
    file_id: str
    filename: str
    file_size: int
    content_type: str
    status: str
    task_id: Optional[str] = None  # Added for automatic processing


class BatchUploadResponse(BaseModel):
    """Batch upload response model."""
    batch_id: str
    job_id: str
    task_id: Optional[str] = None  # Actual Celery task ID for status tracking
    uploaded_files: List[UploadResponse]
    face_limit: Optional[int] = None
    total_files: int
    status: str = "uploaded"
    message: str = "Files uploaded successfully, processing started"


class ValidationError(BaseModel):
    """File validation error model."""
    filename: str
    error: str


@router.post("/image", response_model=UploadResponse, dependencies=[RequireAuth])
@upload_rate_limit
async def upload_image(request: Request, file: UploadFile = File(...)):
    """
    Upload an image file for 3D model generation.
    
    Args:
        file: The image file to upload
        
    Returns:
        Upload response with file details
        
    Raises:
        FileValidationException: If file validation fails
        DatabaseException: If file saving fails
    """
    try:
        # Validate file presence
        if not file.filename:
            raise handle_file_validation_error("", "No filename provided")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise handle_file_validation_error(file.filename, "Only image files are allowed")
        
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise handle_file_validation_error(
                file.filename,
                f"File extension {file_extension} not allowed. "
                f"Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content and check size
        try:
            content = await file.read()
        except Exception as e:
            raise handle_file_validation_error(file.filename, f"Failed to read file: {str(e)}")
        
        if len(content) == 0:
            raise handle_file_validation_error(file.filename, "File is empty")
        
        if len(content) > settings.MAX_FILE_SIZE:
            raise handle_file_validation_error(
                file.filename,
                f"File too large ({len(content)} bytes). Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Generate unique file ID and prepare directories
        file_id = str(uuid.uuid4())
        upload_dir = settings.UPLOAD_DIR
        
        # Create upload directory with proper error handling
        def create_upload_dir():
            os.makedirs(upload_dir, exist_ok=True)
        
        safe_file_operation(create_upload_dir)
        
        file_path = os.path.join(upload_dir, f"{file_id}{file_extension}")
        
        # Save file with proper error handling
        def save_file():
            with open(file_path, "wb") as f:
                f.write(content)
        
        safe_file_operation(save_file)
        
        logger.info(f"Successfully uploaded file: {file.filename} (ID: {file_id})")
        
        # Automatically start 3D model generation for single file uploads
        task_id = None
        try:
            task_result = generate_3d_model_task.delay(
                file_id=file_id,
                file_path=file_path,
                job_id=str(uuid.uuid4()),
                quality="medium",
                texture_enabled=True
            )
            task_id = task_result.id
            logger.info(f"Started automatic 3D model generation task {task_id} for file {file_id}")
        except Exception as e:
            logger.error(f"Failed to start automatic processing for file {file_id}: {str(e)}")
            # Don't fail the upload if task creation fails
        
        return UploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=len(content),
            content_type=file.content_type,
            status="uploaded",
            task_id=task_id
        )
        
    except FileValidationException:
        # Re-raise file validation exceptions as-is
        raise
    except DatabaseException:
        # Re-raise database exceptions as-is
        raise
    except Exception as e:
        # Handle any unexpected errors
        log_exception(e, f"upload_image for {file.filename if file else 'unknown'}")
        raise DatabaseException(
            message=f"Unexpected error during file upload: {str(e)}",
            details=f"operation=upload_image, filename={file.filename if file else None}"
        )


@router.get("/status/{file_id}")
async def get_upload_status(file_id: str):
    """
    Get the status of an uploaded file.
    
    Args:
        file_id: The unique identifier of the uploaded file
        
    Returns:
        File status information
    """
    # This would typically check database for file status
    # For now, just return a basic response
    return {
        "file_id": file_id,
        "status": "uploaded",
        "processing_status": "pending"
    }


def validate_file(file: UploadFile) -> Optional[str]:
    """
    Validate a single uploaded file.
    
    Args:
        file: The uploaded file to validate
        
    Returns:
        Error message if validation fails, None if valid
    """
    try:
        # Check if file is present
        if not file.filename:
            return "No filename provided"
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            return "Only image files are allowed"
        
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = [".jpg", ".jpeg", ".png"]  # Restricted as per requirements
        if file_extension not in allowed_extensions:
            return f"File extension {file_extension} not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
        
        return None
        
    except Exception as e:
        logger.error(f"Error validating file {file.filename if file else 'unknown'}: {str(e)}")
        return f"Validation error: {str(e)}"


async def save_validated_file(file: UploadFile, batch_id: str) -> UploadResponse:
    """
    Save a validated file to temporary storage.
    
    Args:
        file: The validated uploaded file
        batch_id: The batch identifier for organizing files
        
    Returns:
        Upload response with file details
    """
    # Read file content and check size
    content = await file.read()
    max_size = 10 * 1024 * 1024  # 10MB as per requirements
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File {file.filename} too large. Maximum size: {max_size} bytes"
        )
    
    # Generate unique file ID and save file
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    # Create batch-specific directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, batch_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{file_id}{file_extension}")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        file_size=len(content),
        content_type=file.content_type,
        status="uploaded"
    )


@router.post("/", response_model=BatchUploadResponse)
@upload_rate_limit
async def upload(
    request: Request,
    files: List[UploadFile] = File(...),
    face_limit: Optional[int] = Form(None, description="Maximum number of faces for 3D model generation"),
    api_key: str = RequireAuth
):
    """
    Upload image files for 3D model generation.
    
    Args:
        files: List of image files to upload (max 25 files)
        face_limit: Optional parameter to limit the number of faces in generated 3D models
        
    Returns:
        Batch upload response with file details and job information
    """
    # Validate batch size
    max_files = 25  # As per requirements
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum allowed: {max_files}, received: {len(files)}"
        )
    
    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="No files provided"
        )
    
    # Validate face_limit parameter
    if face_limit is not None and face_limit <= 0:
        raise HTTPException(
            status_code=400,
            detail="face_limit must be a positive integer"
        )
    
    # Generate batch and job IDs
    batch_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    
    # Validate all files first
    validation_errors = []
    for file in files:
        error = validate_file(file)
        if error:
            validation_errors.append(ValidationError(filename=file.filename, error=error))
    
    if validation_errors:
        # Return detailed validation errors
        error_details = [f"{err.filename}: {err.error}" for err in validation_errors]
        raise HTTPException(
            status_code=400,
            detail={
                "message": "File validation failed",
                "errors": error_details
            }
        )
    
    # Save all files
    uploaded_files = []
    try:
        for file in files:
            # Reset file pointer for each file
            await file.seek(0)
            uploaded_file = await save_validated_file(file, batch_id)
            uploaded_files.append(uploaded_file)
    
    except Exception as e:
        # Clean up any uploaded files if there's an error
        try:
            upload_dir = os.path.join(settings.UPLOAD_DIR, batch_id)
            if os.path.exists(upload_dir):
                import shutil
                shutil.rmtree(upload_dir)
        except:
            pass  # Best effort cleanup
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save files: {str(e)}"
        )
    
    # Initiate Celery background job for batch processing
    try:
        file_paths = [
            os.path.join(settings.UPLOAD_DIR, batch_id, f"{file.file_id}{os.path.splitext(file.filename)[1].lower()}")
            for file in uploaded_files
        ]
        
        # Start background processing task
        # Always use process_batch for consistency (handles both single and multiple files)
        task_result = process_batch.delay(
            job_id=job_id,
            file_paths=file_paths,
            face_limit=face_limit
        )
        logger.info(f"Started batch processing for {len(file_paths)} files, task_id: {task_result.id}")
        
        actual_task_id = task_result.id
        
        # Ensure we have a task ID
        if not actual_task_id:
            logger.error("No task ID generated for job")
            raise Exception("Failed to generate task ID")
        
    except Exception as e:
        # Log error but don't fail the upload
        # The files are saved and can be processed manually if needed
        logger.error(f"Failed to start background task: {str(e)}")
        actual_task_id = None
    
    # Track job ownership for access control
    if api_key and settings.ENVIRONMENT == "production":
        session_store.set_job_owner(job_id, api_key)
        session_store.set_batch_owner(batch_id, api_key)
    
    return BatchUploadResponse(
        batch_id=batch_id,
        job_id=job_id,
        task_id=actual_task_id,
        uploaded_files=uploaded_files,
        face_limit=face_limit,
        total_files=len(uploaded_files),
        status="uploaded"
    )


@router.get("/batch/{batch_id}/status")
async def get_batch_status(batch_id: str):
    """
    Get the status of a batch upload job.
    
    Args:
        batch_id: The batch identifier
        
    Returns:
        Batch processing status information
    """
    # TODO: This would typically check database/Redis for batch status
    # For now, return a basic response
    return {
        "batch_id": batch_id,
        "status": "processing",
        "message": "Batch is being processed",
        "progress": {
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0
        }
    }
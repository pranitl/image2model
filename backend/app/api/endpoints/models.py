"""
3D model generation endpoints.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.workers.tasks import generate_3d_model_task
from app.workers.fal_client import get_model_client
from app.core.exceptions import FileValidationException, ProcessingException

logger = logging.getLogger(__name__)

router = APIRouter()


class ModelGenerationRequest(BaseModel):
    """
    Request model for 3D model generation.
    
    Attributes:
        file_id: ID of the uploaded image file
        model_type: Type of model to use ("tripo3d" or "trellis")
        quality: Quality setting (standard, low, high) - legacy field for compatibility
        texture_enabled: Whether to enable texture - legacy field for compatibility
        params: Model-specific parameters dictionary
            For tripo3d:
                - face_limit (int): Maximum number of faces in the mesh
                - texture_enabled (bool): Whether to generate texture
            For trellis:
                - ss_guidance_strength (float): 0-10, default 7.5
                - ss_sampling_steps (int): 1-50, default 12
                - slat_guidance_strength (float): 0-10, default 3
                - slat_sampling_steps (int): 1-50, default 12
                - mesh_simplify (float): 0.9-0.98, default 0.95
                - texture_size (str): "512", "1024", or "2048", default "1024"
    """
    file_id: str
    model_type: str = "tripo3d"
    quality: str = "standard"  # standard, low, high
    texture_enabled: bool = True
    params: Optional[Dict[str, Any]] = None  # Model-specific parameters


class ModelGenerationResponse(BaseModel):
    """Response model for 3D model generation."""
    job_id: str
    status: str
    estimated_time: int  # seconds


class ModelInfo(BaseModel):
    """Model information."""
    name: str
    description: str
    type: str
    supported_formats: List[str]


@router.post("/generate", response_model=ModelGenerationResponse)
async def generate_3d_model(request: ModelGenerationRequest, background_tasks: BackgroundTasks):
    """
    Start 3D model generation from uploaded image using Tripo3D.
    
    Args:
        request: Model generation request
        background_tasks: FastAPI background tasks
        
    Returns:
        Job information for tracking progress
        
    Raises:
        FileValidationException: If file validation fails
        ProcessingException: If model generation fails to start
    """
    try:
        # Validate the model type using the factory function
        try:
            # This will raise ValueError if model_type is not supported
            client = get_model_client(request.model_type)
        except ValueError as e:
            raise FileValidationException(
                message=str(e),
                filename=request.file_id
            )
        
        # Validate file_id exists
        import os
        from app.core.config import settings
        
        # Find the uploaded file
        upload_dir = settings.UPLOAD_DIR
        file_path = None
        
        # Search for file with the given ID
        for filename in os.listdir(upload_dir):
            if filename.startswith(request.file_id):
                file_path = os.path.join(upload_dir, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            raise FileValidationException(
                message=f"File with ID {request.file_id} not found",
                filename=request.file_id
            )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Prepare parameters for the task
        # Merge legacy parameters with new params for backward compatibility
        task_params = request.params or {}
        
        # Handle legacy texture_enabled parameter for tripo3d
        if request.model_type == "tripo3d" and "texture_enabled" not in task_params:
            task_params["texture_enabled"] = request.texture_enabled
        
        # Queue the 3D model generation task
        task_result = generate_3d_model_task.delay(
            file_id=request.file_id,
            file_path=file_path,
            job_id=job_id,
            model_type=request.model_type,
            params=task_params
        )
        
        logger.info(f"Started 3D model generation job {job_id} for file {request.file_id}")
        
        # Estimate processing time based on model type
        estimated_time = 180  # Default 3 minutes
        if request.model_type == "trellis":
            estimated_time = 240  # 4 minutes for Trellis (typically slower)
        
        return ModelGenerationResponse(
            job_id=job_id,
            status="queued",
            estimated_time=estimated_time
        )
        
    except (FileValidationException, ProcessingException):
        # Re-raise validation and processing exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in generate_3d_model: {str(e)}")
        raise ProcessingException(
            message=f"Failed to start 3D model generation: {str(e)}",
            operation="generate_3d_model",
            details={"file_id": request.file_id, "model_type": request.model_type}
        )


@router.get("/job/{job_id}")
async def get_generation_status(job_id: str):
    """
    Get the status of a 3D model generation job.
    
    Args:
        job_id: The unique identifier of the generation job
        
    Returns:
        Job status and progress information
    """
    # This would typically check the job queue/database
    return {
        "job_id": job_id,
        "status": "processing",  # queued, processing, completed, failed
        "progress": 45,  # percentage
        "estimated_remaining": 75,  # seconds
        "result_url": None
    }


@router.get("/available", response_model=List[ModelInfo])
async def get_available_models():
    """
    Get list of available 3D model generation models.
    
    Returns:
        List of available models with their information
    """
    return [
        ModelInfo(
            name="tripo3d",
            description="Tripo3D v2.5 - Advanced AI model for high-quality 3D mesh generation from single images",
            type="image_to_3d",
            supported_formats=["obj", "ply", "glb"]
        )
    ]


@router.get("/download/{job_id}")
async def download_model(job_id: str, format: str = "obj"):
    """
    Download the generated 3D model.
    
    Args:
        job_id: The job identifier
        format: The desired model format (obj, ply, stl)
        
    Returns:
        The 3D model file
    """
    # This would typically:
    # 1. Check if job is completed
    # 2. Return the file in requested format
    
    raise HTTPException(
        status_code=501,
        detail="Model download not yet implemented"
    )
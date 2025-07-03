"""
FAL.AI client for 3D model generation from images.

This module provides a FAL.AI client wrapper for the tripo3d/tripo/v2.5/image-to-3d
model with proper authentication, error handling, and result processing.
"""

import os
import logging
import time
from typing import Dict, Any, Optional
import requests
import fal_client as fal
from app.core.config import settings
from app.core.monitoring import monitor_fal_api_call

logger = logging.getLogger(__name__)


class FalAIError(Exception):
    """Base exception for FAL.AI related errors."""
    pass


class FalAIAuthenticationError(FalAIError):
    """Raised when authentication with FAL.AI fails."""
    pass


class FalAIRateLimitError(FalAIError):
    """Raised when FAL.AI rate limit is exceeded."""
    pass


class FalAITimeoutError(FalAIError):
    """Raised when FAL.AI request times out."""
    pass


class FalAIAPIError(FalAIError):
    """Raised when FAL.AI API returns an error response."""
    pass


class FalAIDownloadError(FalAIError):
    """Raised when downloading the generated model fails."""
    pass


class FalAIClient:
    """
    FAL.AI client wrapper for 3D model generation.
    
    This class handles authentication, API calls, and response processing
    for the tripo3d/tripo/v2.5/image-to-3d model.
    """
    
    def __init__(self):
        """Initialize the FAL.AI client with credentials."""
        self._setup_authentication()
        self.model_endpoint = "tripo3d/tripo/v2.5/image-to-3d"
        self.max_retries = 3
        self.base_timeout = 300  # 5 minutes
        self.max_wait_time = 1800  # 30 minutes max
        
    def _setup_authentication(self) -> None:
        """Set up FAL.AI authentication using API key from settings."""
        try:
            # Configure FAL credentials using the single API key
            if settings.FAL_API_KEY and settings.FAL_API_KEY != "your-fal-api-key-here":
                # Set the FAL_KEY environment variable which fal_client uses
                os.environ["FAL_KEY"] = settings.FAL_API_KEY
                logger.info("FAL.AI API key configured successfully")
            else:
                logger.error("FAL.AI API key not found or not set in settings")
                raise FalAIAuthenticationError("FAL.AI API key not properly configured")
        except Exception as e:
            logger.error(f"Failed to configure FAL.AI credentials: {str(e)}")
            raise FalAIAuthenticationError(f"Authentication setup failed: {str(e)}")
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        base_delay = 1.0  # 1 second base delay
        max_delay = 60.0  # 60 seconds max delay
        delay = min(base_delay * (2 ** attempt), max_delay)
        return delay
    
    def _handle_queue_update(self, update, progress_callback):
        """Handle FAL.AI queue updates and forward progress."""
        try:
            import fal_client
            if isinstance(update, fal_client.InProgress):
                # Extract progress information and forward to callback
                if hasattr(update, 'logs') and update.logs:
                    for log in update.logs:
                        if progress_callback and 'message' in log:
                            raw_message = log['message']
                            # Convert FAL.AI progress to user-friendly message
                            progress_percent = 50  # Default
                            user_message = "Generating 3D model..."  # Default user-friendly message
                            
                            if 'upload' in raw_message.lower():
                                progress_percent = 30
                                user_message = "Uploading to FAL.AI..."
                            elif 'generating' in raw_message.lower() or 'processing' in raw_message.lower():
                                progress_percent = 60
                                user_message = "Generating 3D model..."
                            elif 'download' in raw_message.lower() or 'saving' in raw_message.lower():
                                progress_percent = 90
                                user_message = "Finalizing model..."
                            elif 'progress:' in raw_message.lower():
                                # Try to extract percentage from FAL.AI progress message
                                import re
                                percent_match = re.search(r'(\d+)%', raw_message)
                                if percent_match:
                                    try:
                                        # Scale FAL.AI progress to our range (30-90%)
                                        fal_percent = int(percent_match.group(1))
                                        progress_percent = 30 + (fal_percent * 0.6)  # Scale to 30-90% range
                                        user_message = f"Processing 3D model... {fal_percent}%"
                                    except:
                                        pass
                            
                            progress_callback(user_message, progress_percent)
                elif progress_callback:
                    progress_callback("Generating 3D model...", 50)
        except Exception as e:
            logger.warning(f"Failed to handle queue update: {str(e)}")
    
    def _handle_fal_error(self, error: Exception, attempt: int) -> bool:
        """
        Handle FAL.AI errors and determine if retry is appropriate.
        
        Args:
            error: The exception that occurred
            attempt: Current attempt number
            
        Returns:
            True if retry should be attempted, False otherwise
        """
        error_message = str(error).lower()
        
        # Authentication errors - don't retry
        if "auth" in error_message or "unauthorized" in error_message or "forbidden" in error_message:
            raise FalAIAuthenticationError(f"Authentication failed: {str(error)}")
        
        # Rate limiting - retry with backoff
        if "rate limit" in error_message or "too many requests" in error_message or "429" in error_message:
            if attempt < self.max_retries:
                logger.warning(f"Rate limited, waiting before retry attempt {attempt + 1}")
                return True
            else:
                raise FalAIRateLimitError(f"Rate limit exceeded after {self.max_retries} attempts")
        
        # Timeout errors - retry
        if "timeout" in error_message or "timed out" in error_message:
            if attempt < self.max_retries:
                logger.warning(f"Timeout occurred, retrying attempt {attempt + 1}")
                return True
            else:
                raise FalAITimeoutError(f"Request timed out after {self.max_retries} attempts")
        
        # Server errors (5xx) - retry
        if any(code in error_message for code in ["500", "502", "503", "504"]):
            if attempt < self.max_retries:
                logger.warning(f"Server error occurred, retrying attempt {attempt + 1}")
                return True
            else:
                raise FalAIAPIError(f"Server error after {self.max_retries} attempts: {str(error)}")
        
        # Client errors (4xx except rate limiting) - don't retry
        if any(code in error_message for code in ["400", "401", "403", "404"]):
            raise FalAIAPIError(f"Client error (not retryable): {str(error)}")
        
        # Unknown errors - retry once
        if attempt < 1:
            logger.warning(f"Unknown error occurred, retrying once: {str(error)}")
            return True
        else:
            raise FalAIAPIError(f"Unknown error after retry: {str(error)}")
    
    async def process_single_image(
        self, 
        file_path: str, 
        face_limit: Optional[int] = None,
        texture_enabled: bool = True,
        progress_callback: Optional[callable] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single image to generate a 3D model using FAL.AI.
        
        Args:
            file_path: Path to the input image file
            face_limit: Optional face limit parameter for the model
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dictionary containing processing result with status, paths, and metadata
        """
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Starting FAL.AI processing for image: {file_path} (attempt {attempt + 1})")
                
                # Upload the local file to get a URL that FAL.AI can access
                logger.info("Uploading image file to FAL.AI...")
                if progress_callback:
                    progress_callback("Uploading image to FAL.AI...", 15)
                
                # Upload file and get URL using correct API
                file_url = fal.upload_file(file_path)
                logger.info(f"File uploaded to FAL.AI: {file_url}")
                
                # Prepare input data for FAL.AI API according to their documentation
                input_data = {
                    "image_url": file_url,
                    "texture": "standard" if texture_enabled else "no",
                    "texture_alignment": "original_image",  # Per documentation
                    "orientation": "default"  # Per documentation
                }
                
                # Add face_limit if specified (only works with quad=True)
                if face_limit is not None and face_limit > 0:
                    input_data["quad"] = True
                    input_data["face_limit"] = face_limit
                    logger.info(f"Using face_limit: {face_limit} with quad mesh")
                
                # Submit the job to FAL.AI using correct API method
                logger.info("Submitting job to FAL.AI API...")
                if progress_callback:
                    progress_callback("Submitting job to FAL.AI API...", 25)
                
                async with monitor_fal_api_call("submit_job") as monitor_logger:
                    # Use the correct fal_client.subscribe method for real-time execution
                    # This will handle the queue/progress automatically and provide real-time updates
                    result = fal.subscribe(
                        self.model_endpoint,
                        arguments=input_data,
                        with_logs=True,
                        on_queue_update=lambda update: self._handle_queue_update(update, progress_callback) if progress_callback else None
                    )
                    
                    monitor_logger.logger.info(
                        "FAL.AI job completed successfully",
                        model_endpoint=self.model_endpoint,
                        image_path=file_path,
                        face_limit=face_limit,
                        result_keys=list(result.keys()) if isinstance(result, dict) else None
                    )
                    
                    logger.info("FAL.AI processing completed")
                    if progress_callback:
                        progress_callback("FAL.AI processing completed", 80)
                
                if not result:
                    raise FalAIAPIError("No result received from FAL.AI API")
                
                logger.info(f"FAL.AI API response received: {result}")
                
                # Process the successful result
                return await self._process_result(result, file_path, progress_callback, job_id)
                
            except (FalAIAuthenticationError, FalAIRateLimitError, FalAITimeoutError, FalAIAPIError):
                # These are already properly handled exceptions
                raise
            except Exception as e:
                # Try to handle and potentially retry the error
                try:
                    should_retry = self._handle_fal_error(e, attempt)
                    if should_retry and attempt < self.max_retries:
                        delay = self._exponential_backoff(attempt)
                        logger.info(f"Waiting {delay:.2f} seconds before retry...")
                        time.sleep(delay)
                        continue
                    else:
                        # No more retries, convert to appropriate error type
                        raise FalAIAPIError(f"Processing failed after {attempt + 1} attempts: {str(e)}")
                except (FalAIAuthenticationError, FalAIRateLimitError, FalAITimeoutError, FalAIAPIError):
                    raise  # Re-raise properly typed errors
        
        # This should never be reached, but just in case
        return {
            'status': 'failed',
            'input': file_path,
            'error': f'Failed after {self.max_retries + 1} attempts'
        }
    
    async def _process_result(self, result: Dict[str, Any], file_path: str, progress_callback: Optional[callable] = None, job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process the FAL.AI API result and return direct URLs without downloading.
        
        Args:
            result: FAL.AI API response
            file_path: Original input file path
            progress_callback: Optional callback function for progress updates
            job_id: Job ID for tracking
            
        Returns:
            Processed result dictionary with FAL.AI URLs
        """
        try:
            # Extract model URL from result according to FAL.AI Tripo3D documentation
            # Response format: {"model_mesh": {"url": "...", "file_size": ..., "content_type": "..."}, "rendered_image": {...}, "task_id": "..."}
            model_mesh = result.get('model_mesh')
            rendered_image = result.get('rendered_image')
            task_id = result.get('task_id')
            
            if not model_mesh or not model_mesh.get('url'):
                logger.error(f"No model_mesh or model URL found in FAL.AI response: {result}")
                return {
                    'status': 'failed',
                    'input': file_path,
                    'error': 'No model_mesh.url in API response'
                }
            
            model_url = model_mesh['url']
            model_file_size = model_mesh.get('file_size', 0)
            model_content_type = model_mesh.get('content_type', 'application/octet-stream')
            
            logger.info(f"Model URL found: {model_url}")
            
            # No longer downloading files - just return FAL.AI URLs directly
            # Extract original filename for display purposes
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_filename = f"{base_name}.glb"
            
            if progress_callback:
                progress_callback("3D model generation complete!", 100)
            
            # Prepare result with direct FAL.AI URLs
            result_data = {
                'status': 'success',
                'input': file_path,
                'output': None,  # No local file path since we're not downloading
                'download_url': model_url,  # Direct FAL.AI URL for download
                'model_format': 'glb',
                'model_url': model_url,  # Original FAL.AI URL
                'file_size': model_file_size,  # FAL.AI reported file size
                'content_type': model_content_type,  # FAL.AI reported content type
                'output_directory': None,  # No local directory
                'original_file_size': model_file_size,  # FAL.AI response file size
                'original_content_type': model_content_type,  # FAL.AI response content type
                'task_id': task_id,  # FAL.AI task ID
                'filename': output_filename  # For display purposes
            }
            
            # Add rendered image information if available
            if rendered_image and rendered_image.get('url'):
                result_data['rendered_image'] = {
                    'url': rendered_image['url'],
                    'file_size': rendered_image.get('file_size', 0),
                    'content_type': rendered_image.get('content_type', 'image/webp')
                }
                logger.info(f"Rendered image available: {rendered_image['url']}")
            
            return result_data
            
        except FalAIDownloadError as e:
            logger.error(f"Failed to download model file: {str(e)}")
            return {
                'status': 'failed',
                'input': file_path,
                'error': f'Model download failed: {str(e)}',
                'error_type': 'download_error'
            }
        except Exception as e:
            logger.error(f"Failed to process FAL.AI result: {str(e)}")
            return {
                'status': 'failed',
                'input': file_path,
                'error': f'Result processing failed: {str(e)}',
                'error_type': 'processing_error'
            }


    # Storage management methods removed - no longer needed with direct FAL.AI URLs


# Global instance for use in tasks
fal_client = FalAIClient()
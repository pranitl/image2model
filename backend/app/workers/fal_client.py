"""
FAL.AI client for 3D model generation from images.

This module provides a FAL.AI client wrapper for multiple image-to-3D models
with proper authentication, error handling, and result processing.
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import requests
import fal_client as fal
from app.core.config import settings

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


class AbstractFalClient(ABC):
    """
    Abstract base class for FAL.AI client wrappers for 3D model generation.
    
    This class provides common functionality for authentication, API calls,
    and response processing that can be shared across different model implementations.
    """
    
    def __init__(self):
        """Initialize the FAL.AI client with credentials."""
        self._setup_authentication()
        self.max_retries = 3
        self.base_timeout = 300  # 5 minutes
        self.max_wait_time = 1800  # 30 minutes max
        self._processed_log_timestamps = set()  # Track processed logs to avoid duplicates
        self._last_progress = {}  # Track last progress per file to ensure monotonic updates
    
    @property
    @abstractmethod
    def model_endpoint(self) -> str:
        """Return the FAL.AI model endpoint for this client."""
        pass
    
    @abstractmethod
    def prepare_input(self, image_url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare input data for the specific model.
        
        Args:
            image_url: URL of the uploaded image
            params: Model-specific parameters
            
        Returns:
            Dictionary of input data for the FAL.AI API
        """
        pass
    
    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate model-specific parameters.
        
        Args:
            params: Parameters to validate
            
        Raises:
            ValueError: If parameters are invalid
        """
        pass
        
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
    
    def upload_file_to_fal(self, file_path: str) -> str:
        """
        Upload a file to FAL.AI and return the URL.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            URL of the uploaded file
        """
        logger.info(f"Uploading file to FAL.AI: {file_path}")
        file_url = fal.upload_file(file_path)
        logger.info(f"File uploaded to FAL.AI: {file_url}")
        return file_url
    
    def submit_job(self, input_data: Dict[str, Any], progress_callback: Optional[callable] = None, file_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Submit a job to FAL.AI and wait for the result.
        
        Args:
            input_data: Input data for the model
            progress_callback: Optional callback for progress updates
            file_id: Optional file ID for progress tracking
            
        Returns:
            Result from FAL.AI
        """
        logger.info(f"Submitting job to FAL.AI endpoint: {self.model_endpoint}")
        logger.info(f"Input data: {input_data}")
        
        # Track timing for monitoring
        submit_start_time = time.time()
        
        try:
            # Use the correct fal_client.subscribe method for real-time execution
            # This will handle the queue/progress automatically and provide real-time updates
            result = fal.subscribe(
                self.model_endpoint,
                arguments=input_data,
                with_logs=True,
                on_queue_update=lambda update: self._handle_queue_update(update, progress_callback, file_id=file_id) if progress_callback else None
            )
            
            # Log success metrics
            submit_duration_ms = (time.time() - submit_start_time) * 1000
            logger.info(
                f"FAL.AI job completed successfully in {submit_duration_ms:.2f}ms",
                extra={
                    "model_endpoint": self.model_endpoint,
                    "result_keys": list(result.keys()) if isinstance(result, dict) else None,
                    "duration_ms": submit_duration_ms
                }
            )
            
            return result
            
        except Exception as e:
            # Log failure metrics
            submit_duration_ms = (time.time() - submit_start_time) * 1000
            logger.error(
                f"FAL.AI job failed after {submit_duration_ms:.2f}ms: {str(e)}",
                extra={
                    "model_endpoint": self.model_endpoint,
                    "error": str(e),
                    "duration_ms": submit_duration_ms
                }
            )
            raise
    
    def process_result(self, result: Dict[str, Any], file_path: str, progress_callback: Optional[callable] = None, job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process the FAL.AI API result and return standardized output.
        
        This is a common method that can be overridden by subclasses if needed.
        
        Args:
            result: FAL.AI API response
            file_path: Original input file path
            progress_callback: Optional callback function for progress updates
            job_id: Job ID for tracking
            
        Returns:
            Processed result dictionary with standardized fields
        """
        return self._process_result(result, file_path, progress_callback, job_id)
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        base_delay = 1.0  # 1 second base delay
        max_delay = 60.0  # 60 seconds max delay
        delay = min(base_delay * (2 ** attempt), max_delay)
        return delay
    
    def _handle_queue_update(self, update, progress_callback, file_id=None):
        """Handle FAL.AI queue updates and forward progress with deduplication."""
        try:
            import fal_client
            logger.info(f"FAL.AI queue update received: {type(update).__name__}")
            
            if isinstance(update, fal_client.InProgress):
                # Log the update structure for debugging
                logger.info(f"InProgress update - has logs: {hasattr(update, 'logs')}")
                
                # Extract progress information and forward to callback
                if hasattr(update, 'logs') and update.logs:
                    logger.info(f"Processing {len(update.logs)} log entries")
                    for log in update.logs:
                        # Check if we've already processed this log entry
                        log_timestamp = log.get('timestamp') or log.get('logged_at')
                        if log_timestamp and log_timestamp in self._processed_log_timestamps:
                            logger.debug(f"Skipping duplicate log entry: {log_timestamp}")
                            continue
                        
                        # Mark as processed
                        if log_timestamp:
                            self._processed_log_timestamps.add(log_timestamp)
                        
                        logger.info(f"FAL.AI log entry: {log}")
                        if progress_callback and 'message' in log:
                            raw_message = log['message']
                            # Convert FAL.AI progress to user-friendly message
                            progress_percent = 0  # Default to 0 instead of arbitrary values
                            user_message = "Processing..."  # Default user-friendly message
                            
                            if 'upload' in raw_message.lower():
                                progress_percent = 5  # Small progress for upload
                                user_message = "Uploading to FAL.AI..."
                            elif 'generating' in raw_message.lower() or 'processing' in raw_message.lower():
                                progress_percent = 10  # Small default if no percentage found
                                user_message = "Generating 3D model..."
                            elif 'download' in raw_message.lower() or 'saving' in raw_message.lower():
                                progress_percent = 95  # Near complete
                                user_message = "Finalizing model..."
                            elif 'progress:' in raw_message.lower():
                                # Try to extract percentage from FAL.AI progress message
                                import re
                                percent_match = re.search(r'(\d+)%', raw_message)
                                if percent_match:
                                    try:
                                        # Use raw FAL.AI progress without scaling
                                        fal_percent = int(percent_match.group(1))
                                        progress_percent = fal_percent  # Use raw percentage
                                        user_message = f"Processing 3D model... {fal_percent}%"
                                    except:
                                        pass
                            
                            # Ensure monotonic progress (never decrease)
                            last_progress = self._last_progress.get(file_id, 0)
                            if progress_percent < last_progress:
                                logger.debug(f"Skipping progress update {progress_percent}% < {last_progress}%")
                                continue
                            
                            # Update last progress
                            self._last_progress[file_id] = progress_percent
                            
                            logger.info(f"Sending progress update: {user_message} ({progress_percent}%)")
                            progress_callback(user_message, progress_percent)
                elif progress_callback:
                    logger.info("No logs in update, sending default progress")
                    # Only send default if we haven't sent any progress yet
                    if file_id not in self._last_progress or self._last_progress[file_id] == 0:
                        progress_callback("Generating 3D model...", 10)
                        self._last_progress[file_id] = 10
            else:
                logger.info(f"Non-InProgress update type: {type(update)}")
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
        params: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single image to generate a 3D model using FAL.AI.
        
        Args:
            file_path: Path to the input image file
            params: Model-specific parameters
            progress_callback: Optional callback function for progress updates
            job_id: Optional job ID for tracking
            
        Returns:
            Dictionary containing processing result with status, paths, and metadata
        """
        if params is None:
            params = {}
        
        # Validate parameters
        self.validate_params(params)
        # Clear progress tracking for this file
        file_id = job_id or file_path
        if file_id in self._last_progress:
            del self._last_progress[file_id]
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Starting FAL.AI processing for image: {file_path} (attempt {attempt + 1})")
                
                # Upload the local file to get a URL that FAL.AI can access
                logger.info("Uploading image file to FAL.AI...")
                if progress_callback:
                    progress_callback("Uploading image to FAL.AI...", 15)
                
                # Upload file and get URL
                image_url = self.upload_file_to_fal(file_path)
                
                # Prepare input data using subclass-specific method
                input_data = self.prepare_input(image_url, params)
                
                # Submit the job to FAL.AI
                logger.info("Submitting job to FAL.AI API...")
                if progress_callback:
                    progress_callback("Submitting job to FAL.AI API...", 25)
                
                result = self.submit_job(input_data, progress_callback, file_id)
                
                logger.info("FAL.AI processing completed")
                if progress_callback:
                    progress_callback("3D model generation completed", 90)
                
                if not result:
                    raise FalAIAPIError("No result received from FAL.AI API")
                
                logger.info(f"FAL.AI API response received: {result}")
                
                # Process the successful result
                return self._process_result(result, file_path, progress_callback, job_id)
                
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
    
    def _process_result(self, result: Dict[str, Any], file_path: str, progress_callback: Optional[callable] = None, job_id: Optional[str] = None) -> Dict[str, Any]:
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
            # Use FAL.AI's filename if provided, otherwise generate one
            if model_mesh.get('file_name'):
                output_filename = model_mesh['file_name']
            else:
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

    def process_single_image_sync(
        self, 
        file_path: str, 
        params: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[callable] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for process_single_image to use in Celery tasks.
        
        This avoids the coroutine serialization issues when using async functions
        in Celery tasks.
        """
        import asyncio
        
        # Create a new event loop for this thread if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async function in the event loop
        return loop.run_until_complete(
            self.process_single_image(
                file_path=file_path,
                params=params,
                progress_callback=progress_callback,
                job_id=job_id
            )
        )


class TripoClient(AbstractFalClient):
    """
    FAL.AI client implementation for Tripo3D v2.5 model.
    """
    
    @property
    def model_endpoint(self) -> str:
        """Return the Tripo3D model endpoint."""
        return "tripo3d/tripo/v2.5/image-to-3d"
    
    def prepare_input(self, image_url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare input data for Tripo3D model.
        
        Args:
            image_url: URL of the uploaded image
            params: Model-specific parameters
                - texture_enabled (bool): Whether to enable texture generation
                - face_limit (int): Optional face limit for the model
            
        Returns:
            Dictionary of input data for the FAL.AI API
        """
        input_data = {
            "image_url": image_url,
            "texture": "standard" if params.get('texture_enabled', True) else "no",
            "texture_alignment": "original_image",
            "orientation": "default"
        }
        
        # Add face_limit if specified
        # Note: We do NOT set quad=True as it forces FBX output instead of GLB
        if 'face_limit' in params and params['face_limit'] is not None and params['face_limit'] > 0:
            input_data['face_limit'] = params['face_limit']
            logger.info(f"Using face_limit: {params['face_limit']} (GLB output)")
        
        return input_data
    
    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate Tripo3D-specific parameters.
        
        Args:
            params: Parameters to validate
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate texture_enabled
        if 'texture_enabled' in params and not isinstance(params['texture_enabled'], bool):
            raise ValueError("texture_enabled must be a boolean value")
        
        # Validate face_limit
        if 'face_limit' in params:
            face_limit = params['face_limit']
            if face_limit is not None:
                if not isinstance(face_limit, int) or face_limit <= 0:
                    raise ValueError("face_limit must be a positive integer")


class FalAIClient(TripoClient):
    """
    Legacy class name for backward compatibility.
    This is now just an alias for TripoClient.
    """
    pass


# Global instance for use in tasks - using TripoClient for backward compatibility
fal_client = FalAIClient()
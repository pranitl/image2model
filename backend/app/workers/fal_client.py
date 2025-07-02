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
        """Set up FAL.AI authentication using credentials from settings."""
        try:
            # Configure FAL credentials
            if settings.FAL_KEY_ID and settings.FAL_KEY_SECRET:
                fal.config.credentials = f"{settings.FAL_KEY_ID}:{settings.FAL_KEY_SECRET}"
                logger.info("FAL.AI credentials configured successfully")
            else:
                logger.error("FAL.AI credentials not found in settings")
                raise FalAIAuthenticationError("FAL.AI credentials not properly configured")
        except Exception as e:
            logger.error(f"Failed to configure FAL.AI credentials: {str(e)}")
            raise FalAIAuthenticationError(f"Authentication setup failed: {str(e)}")
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay."""
        base_delay = 1.0  # 1 second base delay
        max_delay = 60.0  # 60 seconds max delay
        delay = min(base_delay * (2 ** attempt), max_delay)
        return delay
    
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
        progress_callback: Optional[callable] = None
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
                
                # Prepare input data for FAL.AI API
                input_data = {
                    "image_url": file_path
                }
                
                # Add face_limit if specified
                if face_limit is not None:
                    input_data["face_limit"] = face_limit
                    logger.info(f"Using face_limit: {face_limit}")
                
                # Submit the job to FAL.AI
                logger.info("Submitting job to FAL.AI API...")
                if progress_callback:
                    progress_callback("Submitting job to FAL.AI API...", 10)
                
                async with monitor_fal_api_call("submit_job") as monitor_logger:
                    handler = fal.submit(
                        self.model_endpoint,
                        arguments=input_data
                    )
                    monitor_logger.logger.info(
                        "FAL.AI job submitted successfully",
                        model_endpoint=self.model_endpoint,
                        image_path=file_path,
                        face_limit=face_limit
                    )
                
                # Track progress with timeout
                logger.info("Tracking job progress...")
                if progress_callback:
                    progress_callback("Processing image with FAL.AI...", 30)
                
                progress_counter = 30
                start_time = time.time()
                
                for event in handler.iter_events():
                    # Check for overall timeout
                    elapsed = time.time() - start_time
                    if elapsed > self.max_wait_time:
                        raise FalAITimeoutError(f"Job exceeded maximum wait time of {self.max_wait_time} seconds")
                    
                    if isinstance(event, fal.InProgress):
                        if hasattr(event, 'logs') and event.logs:
                            logger.info(f"Processing progress: {event.logs}")
                            if progress_callback:
                                progress_counter = min(80, progress_counter + 10)
                                progress_callback(f"FAL.AI Progress: {event.logs}", progress_counter)
                        else:
                            logger.info("Processing in progress...")
                            if progress_callback:
                                progress_counter = min(80, progress_counter + 5)
                                progress_callback("FAL.AI processing in progress...", progress_counter)
                
                # Get the final result
                logger.info("Retrieving job result...")
                if progress_callback:
                    progress_callback("Retrieving generated model...", 85)
                
                async with monitor_fal_api_call("get_result") as monitor_logger:
                    result = handler.get()
                    monitor_logger.logger.info(
                        "FAL.AI job result retrieved successfully",
                        result_keys=list(result.keys()) if isinstance(result, dict) else None
                    )
                
                if not result:
                    raise FalAIAPIError("No result received from FAL.AI API")
                
                logger.info(f"FAL.AI API response received: {result}")
                
                # Process the successful result
                return await self._process_result(result, file_path, progress_callback)
                
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
    
    async def _process_result(self, result: Dict[str, Any], file_path: str, progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Process the FAL.AI API result and download the 3D model.
        
        Args:
            result: FAL.AI API response
            file_path: Original input file path
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Processed result dictionary
        """
        try:
            # Extract model URL from result
            # Note: The exact key may vary based on FAL.AI response format
            model_url = result.get('model_url') or result.get('model') or result.get('output_url')
            
            if not model_url:
                logger.error(f"No model URL found in FAL.AI response: {result}")
                return {
                    'status': 'failed',
                    'input': file_path,
                    'error': 'No model URL in API response'
                }
            
            logger.info(f"Model URL found: {model_url}")
            
            # Create output directory structure
            # Use 'results' directory instead of 'outputs' to match existing structure
            output_dir = os.path.dirname(file_path).replace('uploads', 'results')
            if not output_dir or output_dir == os.path.dirname(file_path):
                # Fallback if replace didn't work
                output_dir = os.path.join(os.path.dirname(file_path), '..', 'results')
            
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")
            
            # Generate output file path with timestamp for uniqueness
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            import time
            timestamp = int(time.time())
            output_filename = f"{base_name}_{timestamp}.glb"
            output_path = os.path.join(output_dir, output_filename)
            
            # Download the 3D model file
            logger.info(f"Downloading model from: {model_url}")
            if progress_callback:
                progress_callback("Downloading 3D model...", 90)
            
            # Download with streaming and retry logic
            download_attempts = 3
            for download_attempt in range(download_attempts):
                try:
                    async with monitor_fal_api_call("download_model") as monitor_logger:
                        response = requests.get(model_url, timeout=300, stream=True)  # 5 minute timeout
                        response.raise_for_status()
                        
                        monitor_logger.logger.info(
                            "Model download initiated",
                            model_url=model_url,
                            output_path=output_path,
                            attempt=download_attempt + 1
                        )
                    
                    # Validate content type if possible
                    content_type = response.headers.get('content-type', '')
                    logger.info(f"Downloaded file content type: {content_type}")
                    
                    # Get content length for progress tracking
                    content_length = response.headers.get('content-length')
                    total_size = int(content_length) if content_length else None
                    
                    # Save the model file with progress tracking
                    if progress_callback:
                        progress_callback("Saving model file...", 95)
                    
                    downloaded_size = 0
                    chunk_size = 8192  # 8KB chunks
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:  # Filter out keep-alive chunks
                                f.write(chunk)
                                downloaded_size += len(chunk)
                    
                    # Validate the downloaded file
                    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                        raise FalAIDownloadError("Downloaded file is empty or does not exist")
                    
                    file_size = os.path.getsize(output_path)
                    logger.info(f"3D model saved successfully to: {output_path} (Size: {file_size} bytes)")
                    
                    if progress_callback:
                        progress_callback("3D model generation complete!", 100)
                    
                    break  # Success, exit retry loop
                    
                except requests.RequestException as e:
                    if download_attempt < download_attempts - 1:
                        logger.warning(f"Download attempt {download_attempt + 1} failed, retrying: {str(e)}")
                        time.sleep(2 ** download_attempt)  # Exponential backoff
                        continue
                    else:
                        raise FalAIDownloadError(f"Failed to download model after {download_attempts} attempts: {str(e)}")
                except Exception as e:
                    if download_attempt < download_attempts - 1:
                        logger.warning(f"Download attempt {download_attempt + 1} failed, retrying: {str(e)}")
                        time.sleep(2 ** download_attempt)
                        continue
                    else:
                        raise FalAIDownloadError(f"Failed to save model after {download_attempts} attempts: {str(e)}")
            
            return {
                'status': 'success',
                'input': file_path,
                'output': output_path,
                'model_format': 'glb',
                'model_url': model_url,
                'file_size': file_size,
                'content_type': content_type,
                'output_directory': output_dir
            }
            
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


    @staticmethod
    def cleanup_old_results(max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Clean up old result files to manage disk space.
        
        Args:
            max_age_hours: Maximum age in hours before files are considered for cleanup
            
        Returns:
            Dictionary with cleanup statistics
        """
        import time
        
        try:
            results_dir = os.path.abspath("results")
            if not os.path.exists(results_dir):
                return {"status": "success", "message": "No results directory found", "files_removed": 0}
            
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            files_removed = 0
            total_size_removed = 0
            
            for root, dirs, files in os.walk(results_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_age = current_time - os.path.getctime(file_path)
                        if file_age > max_age_seconds:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            files_removed += 1
                            total_size_removed += file_size
                            logger.info(f"Removed old result file: {file_path}")
                    except OSError as e:
                        logger.warning(f"Could not remove file {file_path}: {str(e)}")
            
            return {
                "status": "success",
                "files_removed": files_removed,
                "total_size_removed": total_size_removed,
                "message": f"Cleanup completed: {files_removed} files removed ({total_size_removed} bytes)"
            }
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "files_removed": 0
            }
    
    @staticmethod
    def get_storage_stats() -> Dict[str, Any]:
        """
        Get storage statistics for the results directory.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            results_dir = os.path.abspath("results")
            if not os.path.exists(results_dir):
                return {"status": "success", "total_files": 0, "total_size": 0}
            
            total_files = 0
            total_size = 0
            
            for root, dirs, files in os.walk(results_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_files += 1
                        total_size += os.path.getsize(file_path)
                    except OSError:
                        pass  # Skip files that can't be accessed
            
            return {
                "status": "success",
                "total_files": total_files,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "results_directory": results_dir
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }


# Global instance for use in tasks
fal_client = FalAIClient()
"""
Mock for FAL.AI API to avoid actual API calls during testing.

This mock simulates the FAL.AI Tripo3D API behavior based on the official documentation:
https://fal.ai/models/tripo3d/tripo/v2.5/image-to-3d/api
"""

import time
import uuid
from typing import Dict, Any, Optional, Callable
from unittest.mock import MagicMock


class MockFalAIResponse:
    """Mock FAL.AI response based on official documentation."""
    
    @staticmethod
    def generate_success_response() -> Dict[str, Any]:
        """Generate a successful response matching FAL.AI Tripo3D format."""
        task_id = str(uuid.uuid4())
        return {
            "task_id": task_id,
            "model_mesh": {
                "url": f"https://v3.fal.media/files/zebra/mock_{task_id}_model.glb",
                "file_size": 6744644,
                "content_type": "application/octet-stream"
            },
            "base_model": {
                "url": f"https://v3.fal.media/files/zebra/mock_{task_id}_base.glb",
                "file_size": 5234567,
                "content_type": "model/gltf-binary"
            },
            "pbr_model": {
                "url": f"https://v3.fal.media/files/zebra/mock_{task_id}_pbr.glb",
                "file_size": 7123456,
                "content_type": "model/gltf-binary"
            },
            "rendered_image": {
                "url": f"https://v3.fal.media/files/panda/mock_{task_id}_render.webp",
                "file_size": 13718,
                "content_type": "image/webp"
            }
        }
    
    @staticmethod
    def generate_error_response(error_type: str = "validation") -> Dict[str, Any]:
        """Generate an error response matching FAL.AI format."""
        if error_type == "validation":
            return {
                "detail": [{
                    "loc": ["body", "image_url"],
                    "msg": "Invalid image URL format",
                    "type": "value_error"
                }]
            }
        elif error_type == "rate_limit":
            return {
                "error": "Rate limit exceeded",
                "code": 429,
                "message": "Too many requests. Please try again later."
            }
        elif error_type == "auth":
            return {
                "error": "Authentication failed",
                "code": 401,
                "message": "Invalid API key"
            }
        else:
            return {
                "error": "Internal server error",
                "code": 500,
                "message": "An unexpected error occurred"
            }


class MockInProgressUpdate:
    """Mock FAL.AI InProgress update with logs."""
    
    def __init__(self, progress: int = 0, message: str = "Processing..."):
        self.logs = [
            {
                "message": message,
                "timestamp": int(time.time() * 1000),
                "level": "info"
            }
        ]
        self.progress = progress


def create_fal_mock(
    success: bool = True,
    progress_updates: bool = True,
    error_type: Optional[str] = None,
    custom_response: Optional[Dict[str, Any]] = None
):
    """
    Create a comprehensive FAL.AI mock for testing.
    
    Args:
        success: Whether the mock should simulate success or failure
        progress_updates: Whether to simulate progress updates
        error_type: Type of error to simulate if success=False
        custom_response: Custom response to return instead of default
    
    Returns:
        Dictionary of mock functions to patch
    """
    
    def mock_upload_file(file_path: str) -> str:
        """Mock file upload to FAL.AI."""
        # Simulate file upload and return a mock URL
        file_id = str(uuid.uuid4())[:8]
        return f"https://v3.fal.media/files/upload/mock_{file_id}_image.jpg"
    
    def mock_subscribe(
        endpoint: str,
        arguments: Dict[str, Any],
        with_logs: bool = False,
        on_queue_update: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Mock FAL.AI subscribe method with progress updates."""
        
        # Simulate progress updates if requested
        if progress_updates and on_queue_update and callable(on_queue_update):
            # Simulate upload progress
            update = MockInProgressUpdate(5, "Uploading image...")
            on_queue_update(update)
            
            # Simulate initial processing
            update = MockInProgressUpdate(10, "Starting 3D generation...")
            on_queue_update(update)
            
            # Simulate model generation progress
            for i in range(20, 90, 10):
                update = MockInProgressUpdate(i, f"Generating 3D model... Progress: {i}%")
                on_queue_update(update)
            
            # Simulate finalization
            update = MockInProgressUpdate(95, "Finalizing model...")
            on_queue_update(update)
        
        # Return result based on success flag
        if success:
            return custom_response or MockFalAIResponse.generate_success_response()
        else:
            error_response = MockFalAIResponse.generate_error_response(error_type or "validation")
            if error_type == "rate_limit":
                raise Exception(f"429 Too Many Requests: {error_response['message']}")
            elif error_type == "auth":
                raise Exception(f"401 Unauthorized: {error_response['message']}")
            elif error_type == "timeout":
                raise Exception("Request timed out")
            else:
                raise Exception(f"422 Validation Error: {error_response}")
    
    def mock_submit(endpoint: str, arguments: Dict[str, Any]) -> MagicMock:
        """Mock FAL.AI submit method (deprecated, but kept for compatibility)."""
        handler = MagicMock()
        handler.iter_events.return_value = []
        
        if success:
            handler.get.return_value = custom_response or MockFalAIResponse.generate_success_response()
        else:
            if error_type == "timeout":
                handler.get.side_effect = Exception("Request timed out")
            else:
                handler.get.side_effect = Exception(f"API Error: {error_type}")
        
        return handler
    
    return {
        'upload_file': mock_upload_file,
        'subscribe': mock_subscribe,
        'submit': mock_submit  # For backward compatibility
    }


def patch_fal_client(test_func):
    """
    Decorator to patch FAL.AI client for testing.
    
    Usage:
        @patch_fal_client
        def test_my_function(self, mock_fal):
            # mock_fal contains the mocked FAL.AI functions
            result = my_function_that_uses_fal()
            assert result['status'] == 'success'
    """
    from unittest.mock import patch
    
    def wrapper(*args, **kwargs):
        mocks = create_fal_mock()
        
        with patch('fal_client.upload_file', side_effect=mocks['upload_file']):
            with patch('fal_client.subscribe', side_effect=mocks['subscribe']):
                with patch('fal_client.submit', side_effect=mocks['submit']):
                    # Add the mocks as a parameter to the test function
                    return test_func(*args, mock_fal=mocks, **kwargs)
    
    return wrapper


def get_mock_fal_settings():
    """Get mock FAL.AI settings for testing."""
    return {
        'FAL_API_KEY': 'test-fal-api-key-12345',
        'FAL_API_URL': 'https://fal.run',
        'FAL_TIMEOUT': 300,
        'FAL_MAX_RETRIES': 3
    }
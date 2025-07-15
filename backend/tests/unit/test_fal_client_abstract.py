"""
Unit tests for AbstractFalClient base class.
"""

import pytest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from abc import ABC

from app.workers.fal_client import (
    AbstractFalClient,
    FalAIError,
    FalAIAuthenticationError,
    FalAIRateLimitError,
    FalAITimeoutError,
    FalAIAPIError
)
from tests.mocks.fal_responses import TRIPO_SUCCESS, ERROR_RESPONSES


class TestAbstractFalClient:
    """Test cases for AbstractFalClient abstract base class."""
    
    def test_abstract_base_class_enforcement(self):
        """Test that AbstractFalClient cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            AbstractFalClient()
        assert "Can't instantiate abstract class" in str(exc_info.value)
    
    def test_authentication_setup_success(self, monkeypatch):
        """Test successful authentication setup with valid API key."""
        # Create a concrete implementation for testing
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "test/endpoint"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        # Mock settings with valid API key
        monkeypatch.setenv("FAL_KEY", "test-api-key")
        monkeypatch.setattr("app.core.config.settings.FAL_API_KEY", "test-api-key")
        
        # Should initialize without error
        client = TestClient()
        assert client.max_retries == 3
        assert client.base_timeout == 300
        assert client.max_wait_time == 1800
    
    def test_authentication_setup_missing_key(self, monkeypatch):
        """Test authentication setup fails with missing API key."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "test/endpoint"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        # Mock settings with invalid API key
        monkeypatch.setattr("app.core.config.settings.FAL_API_KEY", "your-fal-api-key-here")
        
        with pytest.raises(FalAIAuthenticationError) as exc_info:
            TestClient()
        assert "FAL.AI API key not properly configured" in str(exc_info.value)
    
    def test_error_handling_retry_logic(self):
        """Test exponential backoff calculation for retries."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "test/endpoint"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = TestClient()
            
            # Test exponential backoff
            assert client._exponential_backoff(0) == 1.0
            assert client._exponential_backoff(1) == 2.0
            assert client._exponential_backoff(2) == 4.0
            assert client._exponential_backoff(3) == 8.0
            assert client._exponential_backoff(10) == 60.0  # Max delay
    
    def test_progress_callback_functionality(self, mock_fal_subscribe):
        """Test that progress callbacks are properly invoked."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "test/endpoint"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = TestClient()
            
            progress_updates = []
            def progress_callback(message, progress):
                progress_updates.append((message, progress))
            
            # Mock submit_job to trigger progress callbacks
            mock_fal_subscribe.response_type = "success"
            result = client.submit_job(
                {"image_url": "test.png"}, 
                progress_callback=progress_callback,
                file_id="test-file"
            )
            
            # Verify progress updates were captured
            assert len(progress_updates) > 0
            assert any("Uploading" in update[0] for update in progress_updates)
            assert any("Processing" in update[0] for update in progress_updates)
    
    def test_upload_file_to_fal(self, mock_fal_upload, temp_image_file):
        """Test file upload functionality."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "test/endpoint"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = TestClient()
            
            url = client.upload_file_to_fal(temp_image_file)
            assert url.startswith("https://fal.ai/uploads/")
            assert os.path.basename(temp_image_file) in url
    
    def test_submit_job_success(self, mock_fal_subscribe):
        """Test successful job submission."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "tripo3d/tripo/v2.5/image-to-3d"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = TestClient()
            
            mock_fal_subscribe.response_type = "success"
            result = client.submit_job({"image_url": "test.png"})
            
            assert result == TRIPO_SUCCESS
            assert mock_fal_subscribe.call_count == 1
    
    def test_process_result_common_logic(self):
        """Test URL extraction from FAL response."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "test/endpoint"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = TestClient()
            
            # Test successful result processing
            result = client.process_result(
                TRIPO_SUCCESS,
                "test.png",
                progress_callback=None,
                job_id="test-job"
            )
            
            assert result["status"] == "success"
            assert result["download_url"] == TRIPO_SUCCESS["model_mesh"]["url"]
            assert result["file_size"] == TRIPO_SUCCESS["model_mesh"]["file_size"]
            assert result["model_format"] == "glb"
    
    def test_handle_fal_error_authentication(self):
        """Test authentication error handling."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "test/endpoint"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = TestClient()
            
            error = Exception("Unauthorized access")
            with pytest.raises(FalAIAuthenticationError):
                client._handle_fal_error(error, 0)
    
    def test_handle_fal_error_rate_limit(self):
        """Test rate limit error handling with retry."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "test/endpoint"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = TestClient()
            
            error = Exception("Rate limit exceeded")
            # Should return True for retry on first attempts
            assert client._handle_fal_error(error, 0) == True
            assert client._handle_fal_error(error, 1) == True
            
            # Should raise after max retries
            with pytest.raises(FalAIRateLimitError):
                client._handle_fal_error(error, 3)
    
    def test_handle_fal_error_timeout(self):
        """Test timeout error handling."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "test/endpoint"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = TestClient()
            
            error = Exception("Request timed out")
            # Should retry on timeout
            assert client._handle_fal_error(error, 0) == True
            
            # Should raise after max retries
            with pytest.raises(FalAITimeoutError):
                client._handle_fal_error(error, 3)
    
    def test_handle_queue_update_deduplication(self):
        """Test that duplicate progress updates are filtered."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "test/endpoint"
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = TestClient()
            
            progress_updates = []
            def progress_callback(message, progress):
                progress_updates.append((message, progress))
            
            # Create mock update with timestamp
            import fal_client
            update = Mock(spec=fal_client.InProgress)
            update.logs = [{
                "message": "Test progress",
                "timestamp": "2024-01-10T10:00:00.000Z"
            }]
            
            # Process same update twice
            client._handle_queue_update(update, progress_callback, file_id="test")
            client._handle_queue_update(update, progress_callback, file_id="test")
            
            # Should only process once due to timestamp deduplication
            assert len(progress_updates) == 1
    
    def test_process_single_image_sync_wrapper(self, mock_fal_subscribe, mock_fal_upload, temp_image_file):
        """Test synchronous wrapper for async process_single_image."""
        class TestClient(AbstractFalClient):
            @property
            def model_endpoint(self):
                return "tripo3d/tripo/v2.5/image-to-3d"  # Use a known endpoint for proper mock response
            
            def prepare_input(self, image_url, params):
                return {"image_url": image_url}
            
            def validate_params(self, params):
                pass
        
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = TestClient()
            
            mock_fal_subscribe.response_type = "success"
            
            # Test sync wrapper
            result = client.process_single_image_sync(
                file_path=temp_image_file,
                params={},
                progress_callback=None,
                job_id="test-job"
            )
            
            assert result["status"] == "success"
            assert "download_url" in result
            assert result["download_url"] == TRIPO_SUCCESS["model_mesh"]["url"]
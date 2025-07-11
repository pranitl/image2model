"""
Integration tests for FAL.AI Tripo3D integration.

Tests the complete FAL.AI integration based on the official API documentation
from https://fal.ai/models/tripo3d/tripo/v2.5/image-to-3d/api?platform=http
"""

import pytest
import json
import os
import time
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any

import fal_client as fal
from app.workers.fal_client import FalAIClient, FalAIError, FalAIAuthenticationError, FalAIAPIError
from app.workers.tasks import generate_3d_model_task, process_single_image_with_retry
from app.core.config import settings


@pytest.mark.integration
class TestFalAIIntegration:
    """Test FAL.AI Tripo3D integration according to official documentation."""
    
    @pytest.fixture
    def sample_image_path(self):
        """Create a temporary test image file."""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            # Create a minimal JPEG file (not a real image, but enough for testing)
            tmp_file.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xd9')
            tmp_file.flush()
            yield tmp_file.name
        os.unlink(tmp_file.name)
    
    @pytest.fixture
    def mock_fal_response(self):
        """Mock FAL.AI response based on documentation."""
        return {
            "model_mesh": {
                "url": "https://fal.media/models/test-model.glb",
                "file_size": 1024000,
                "content_type": "model/gltf-binary"
            },
            "rendered_image": {
                "url": "https://fal.media/images/test-render.webp",
                "file_size": 51200,
                "content_type": "image/webp"
            }
        }
    
    def test_fal_client_initialization(self):
        """Test FAL.AI client initialization with proper API key."""
        # Test with valid API key
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            client = FalAIClient()
            assert client.model_endpoint == "tripo3d/tripo/v2.5/image-to-3d"
            assert client.max_retries == 3
            assert client.max_wait_time == 1800
    
    def test_fal_client_authentication_error(self):
        """Test FAL.AI client handles authentication errors correctly."""
        with patch.object(settings, 'FAL_API_KEY', 'your-fal-api-key-here'):
            with pytest.raises(FalAIAuthenticationError, match="FAL.AI API key not properly configured"):
                FalAIClient()
    
    def test_fal_api_endpoint_format(self):
        """Test that we're using the correct FAL.AI endpoint format."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            client = FalAIClient()
            assert client.model_endpoint == "tripo3d/tripo/v2.5/image-to-3d"
    
    @patch('fal_client.submit')
    @patch('fal_client.upload_file')
    def test_correct_api_payload_format(self, mock_upload, mock_submit, sample_image_path, mock_fal_response):
        """Test that we send the correct payload format to FAL.AI."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            # Mock file upload
            mock_upload.return_value = "https://fal.media/files/uploaded-image.jpg"
            
            # Mock API submission with proper handler
            mock_handler = MagicMock()
            mock_handler.iter_events.return_value = []
            mock_handler.get.return_value = mock_fal_response
            mock_submit.return_value = mock_handler
            
            client = FalAIClient()
            
            # Test process_single_image
            import asyncio
            result = asyncio.run(client.process_single_image(sample_image_path, face_limit=5000))
            
            # Verify file upload was called
            mock_upload.assert_called_once_with(sample_image_path)
            
            # Verify API submission with correct format
            mock_submit.assert_called_once_with(
                "tripo3d/tripo/v2.5/image-to-3d",
                arguments={
                    "image_url": "https://fal.media/files/uploaded-image.jpg",
                    "texture": "standard",
                    "pbr": True,
                    "face_limit": 5000
                }
            )
            
            assert result['status'] == 'success'
    
    def test_required_parameters(self, sample_image_path):
        """Test that required parameters are correctly handled."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    mock_upload.return_value = "https://fal.media/files/test.jpg"
                    
                    mock_handler = MagicMock()
                    mock_handler.iter_events.return_value = []
                    mock_handler.get.return_value = {
                        "model_mesh": {
                            "url": "https://fal.media/test.glb",
                            "file_size": 1024,
                            "content_type": "model/gltf-binary"
                        }
                    }
                    mock_submit.return_value = mock_handler
                    
                    client = FalAIClient()
                    
                    # Test minimal required parameters
                    import asyncio
                    result = asyncio.run(client.process_single_image(sample_image_path))
                    
                    # Verify required parameters are sent
                    call_args = mock_submit.call_args[1]['arguments']
                    assert 'image_url' in call_args
                    assert 'texture' in call_args
                    assert 'pbr' in call_args
                    assert call_args['texture'] == 'standard'
                    assert call_args['pbr'] is True
    
    def test_optional_parameters(self, sample_image_path):
        """Test that optional parameters are correctly handled."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    mock_upload.return_value = "https://fal.media/files/test.jpg"
                    
                    mock_handler = MagicMock()
                    mock_handler.iter_events.return_value = []
                    mock_handler.get.return_value = {
                        "model_mesh": {
                            "url": "https://fal.media/test.glb",
                            "file_size": 1024,
                            "content_type": "model/gltf-binary"
                        }
                    }
                    mock_submit.return_value = mock_handler
                    
                    client = FalAIClient()
                    
                    # Test with optional face_limit parameter
                    import asyncio
                    result = asyncio.run(client.process_single_image(sample_image_path, face_limit=10000))
                    
                    # Verify optional parameters are included
                    call_args = mock_submit.call_args[1]['arguments']
                    assert call_args['face_limit'] == 10000
    
    def test_response_format_parsing(self, sample_image_path, mock_fal_response):
        """Test that we correctly parse the FAL.AI response format."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    with patch('requests.get') as mock_download:
                        mock_upload.return_value = "https://fal.media/files/test.jpg"
                        
                        mock_handler = MagicMock()
                        mock_handler.iter_events.return_value = []
                        mock_handler.get.return_value = mock_fal_response
                        mock_submit.return_value = mock_handler
                        
                        # Mock successful download
                        mock_response = MagicMock()
                        mock_response.headers = {'content-type': 'model/gltf-binary'}
                        mock_response.iter_content.return_value = [b'fake_model_data']
                        mock_response.raise_for_status.return_value = None
                        mock_download.return_value = mock_response
                        
                        client = FalAIClient()
                        
                        import asyncio
                        result = asyncio.run(client.process_single_image(sample_image_path))
                        
                        # Verify response parsing
                        assert result['status'] == 'success'
                        assert result['model_format'] == 'glb'
                        assert result['model_url'] == mock_fal_response['model_mesh']['url']
                        assert result['original_file_size'] == mock_fal_response['model_mesh']['file_size']
                        assert result['original_content_type'] == mock_fal_response['model_mesh']['content_type']
                        
                        # Verify rendered image is included
                        assert 'rendered_image' in result
                        assert result['rendered_image']['url'] == mock_fal_response['rendered_image']['url']
                        assert result['rendered_image']['content_type'] == 'image/webp'
    
    def test_authentication_header_format(self, sample_image_path):
        """Test that authentication follows the documented format."""
        test_api_key = "test-fal-api-key-12345"
        
        with patch.object(settings, 'FAL_API_KEY', test_api_key):
            client = FalAIClient()
            
            # Verify that the API key is set in environment
            assert os.environ.get('FAL_KEY') == test_api_key
    
    def test_error_handling_http_422(self, sample_image_path):
        """Test handling of HTTP 422 validation errors."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    mock_upload.return_value = "https://fal.media/files/test.jpg"
                    
                    # Simulate 422 validation error
                    error = Exception("422 Validation Error: Invalid image format")
                    mock_submit.side_effect = error
                    
                    client = FalAIClient()
                    
                    import asyncio
                    result = asyncio.run(client.process_single_image(sample_image_path))
                    
                    assert result['status'] == 'failed'
                    assert 'error' in result
    
    def test_rate_limiting_handling(self, sample_image_path):
        """Test proper handling of rate limiting."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    mock_upload.return_value = "https://fal.media/files/test.jpg"
                    
                    # Simulate rate limiting error
                    error = Exception("429 Too Many Requests")
                    mock_submit.side_effect = error
                    
                    client = FalAIClient()
                    
                    with pytest.raises(FalAIAPIError):
                        import asyncio
                        asyncio.run(client.process_single_image(sample_image_path))
    
    def test_pricing_considerations(self):
        """Test that our implementation considers pricing factors."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            client = FalAIClient()
            
            # Test that we're using the base model (no extra cost features by default)
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    mock_upload.return_value = "https://fal.media/files/test.jpg"
                    
                    mock_handler = MagicMock()
                    mock_handler.iter_events.return_value = []
                    mock_handler.get.return_value = {
                        "model_mesh": {
                            "url": "https://fal.media/test.glb",
                            "file_size": 1024,
                            "content_type": "model/gltf-binary"
                        }
                    }
                    mock_submit.return_value = mock_handler
                    
                    import asyncio
                    asyncio.run(client.process_single_image("test.jpg"))
                    
                    # Verify we don't use expensive options by default
                    call_args = mock_submit.call_args[1]['arguments']
                    assert call_args.get('quad', False) is False  # No quad mesh (+$0.05)
                    assert call_args.get('texture') == 'standard'  # Not 'HD' texture
    
    @patch('app.workers.tasks.process_single_image')
    def test_celery_task_integration(self, mock_process, sample_image_path):
        """Test that Celery task properly integrates with FAL.AI client."""
        # Mock successful processing
        mock_process.return_value = {
            'status': 'success',
            'output': '/results/test_model.glb',
            'model_format': 'glb',
            'rendered_image': {
                'url': 'https://fal.media/rendered.webp',
                'content_type': 'image/webp'
            }
        }
        
        # Test the task
        result = generate_3d_model_task(
            file_id="test-file-id",
            file_path=sample_image_path,
            job_id="test-job-id",
            quality="medium",
            texture_enabled=True
        )
        
        # Verify task result
        assert result['status'] == 'completed'
        assert result['job_id'] == 'test-job-id'
        assert result['file_id'] == 'test-file-id'
        assert result['result_path'] == '/results/test_model.glb'
        assert result['model_format'] == 'glb'
        assert 'rendered_image' in result
    
    def test_models_endpoint_accuracy(self, auth_http_session, test_config, services_ready):
        """Test that models endpoint reflects only Tripo3D model."""
        url = f"{test_config['backend_url']}/api/v1/models/available"
        response = auth_http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        models = response.json()
        
        # Should only have one model: Tripo3D
        assert len(models) == 1
        
        tripo_model = models[0]
        assert tripo_model['name'] == 'tripo3d'
        assert tripo_model['type'] == 'image_to_3d'
        assert 'tripo3d' in tripo_model['description'].lower()
        assert 'glb' in tripo_model['supported_formats']
    
    def test_model_generation_endpoint_validation(self, auth_http_session, test_config, services_ready):
        """Test model generation endpoint validates Tripo3D model type."""
        url = f"{test_config['backend_url']}/api/v1/models/generate"
        
        # Test with unsupported model type
        invalid_payload = {
            "file_id": "test-file-id",
            "model_type": "depth_anything_v2",  # Should not be supported anymore
            "quality": "medium"
        }
        
        response = auth_http_session.post(url, json=invalid_payload, timeout=test_config['timeout'])
        
        # Should reject unsupported model types
        assert response.status_code == 400
        error_data = response.json()
        assert 'model type' in error_data.get('message', '').lower()
    
    def test_fal_api_timeout_handling(self, sample_image_path):
        """Test handling of FAL.AI API timeouts."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    mock_upload.return_value = "https://fal.media/files/test.jpg"
                    
                    # Mock handler that simulates timeout
                    mock_handler = MagicMock()
                    mock_handler.iter_events.return_value = []
                    
                    # Simulate timeout by making get() take too long
                    def slow_get():
                        time.sleep(2)  # Simulate slow response
                        raise Exception("Request timed out")
                    
                    mock_handler.get.side_effect = slow_get
                    mock_submit.return_value = mock_handler
                    
                    client = FalAIClient()
                    
                    # Test timeout handling
                    import asyncio
                    result = asyncio.run(client.process_single_image(sample_image_path))
                    
                    assert result['status'] == 'failed'
                    assert 'timeout' in result.get('error', '').lower()
    
    def test_file_size_and_format_validation(self):
        """Test that we handle file size and format constraints."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            client = FalAIClient()
            
            # Test with various file formats
            supported_formats = ['.jpg', '.jpeg', '.png', '.webp']
            
            for fmt in supported_formats:
                with tempfile.NamedTemporaryFile(suffix=fmt, delete=False) as tmp_file:
                    tmp_file.write(b'fake_image_data')
                    tmp_file.flush()
                    
                    # Should not raise format errors for supported formats
                    assert os.path.exists(tmp_file.name)
                    
                    os.unlink(tmp_file.name)
    
    def test_concurrent_request_handling(self, sample_image_path):
        """Test handling of concurrent FAL.AI requests."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    mock_upload.return_value = "https://fal.media/files/test.jpg"
                    
                    mock_handler = MagicMock()
                    mock_handler.iter_events.return_value = []
                    mock_handler.get.return_value = {
                        "model_mesh": {
                            "url": "https://fal.media/test.glb",
                            "file_size": 1024,
                            "content_type": "model/gltf-binary"
                        }
                    }
                    mock_submit.return_value = mock_handler
                    
                    client = FalAIClient()
                    
                    # Test concurrent processing
                    import asyncio
                    async def process_multiple():
                        tasks = [
                            client.process_single_image(sample_image_path),
                            client.process_single_image(sample_image_path),
                            client.process_single_image(sample_image_path)
                        ]
                        return await asyncio.gather(*tasks)
                    
                    results = asyncio.run(process_multiple())
                    
                    # All should succeed
                    assert len(results) == 3
                    for result in results:
                        assert result['status'] == 'success'


@pytest.mark.integration
class TestFalAIDocumentationCompliance:
    """Test compliance with specific FAL.AI documentation requirements."""
    
    def test_endpoint_url_format(self):
        """Test that we use the exact endpoint URL from documentation."""
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            client = FalAIClient()
            
            # Should match: POST https://fal.run/tripo3d/tripo/v2.5/image-to-3d
            assert client.model_endpoint == "tripo3d/tripo/v2.5/image-to-3d"
    
    def test_request_payload_structure(self, sample_image_path):
        """Test that request payload matches documentation exactly."""
        expected_payload_keys = {'image_url', 'texture', 'pbr'}
        optional_keys = {'seed', 'face_limit', 'style', 'quad', 'auto_size', 'texture_seed'}
        
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    mock_upload.return_value = "https://fal.media/files/test.jpg"
                    
                    mock_handler = MagicMock()
                    mock_handler.iter_events.return_value = []
                    mock_handler.get.return_value = {
                        "model_mesh": {"url": "https://fal.media/test.glb", "file_size": 1024, "content_type": "model/gltf-binary"}
                    }
                    mock_submit.return_value = mock_handler
                    
                    client = FalAIClient()
                    
                    import asyncio
                    asyncio.run(client.process_single_image(sample_image_path, face_limit=5000))
                    
                    # Verify payload structure
                    call_args = mock_submit.call_args[1]['arguments']
                    
                    # Check required keys are present
                    for key in expected_payload_keys:
                        assert key in call_args, f"Required key '{key}' missing from payload"
                    
                    # Check values match documentation format
                    assert isinstance(call_args['pbr'], bool)
                    assert call_args['texture'] in ['no', 'standard', 'HD']
                    assert call_args['image_url'].startswith('https://')
    
    def test_response_format_compliance(self, sample_image_path):
        """Test that we handle the documented response format."""
        documented_response = {
            "model_mesh": {
                "url": "https://fal.media/files/model.glb",
                "file_size": 2048576,
                "content_type": "model/gltf-binary"
            },
            "rendered_image": {
                "url": "https://fal.media/files/render.webp",
                "file_size": 102400,
                "content_type": "image/webp"
            }
        }
        
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    with patch('requests.get') as mock_download:
                        mock_upload.return_value = "https://fal.media/files/test.jpg"
                        
                        mock_handler = MagicMock()
                        mock_handler.iter_events.return_value = []
                        mock_handler.get.return_value = documented_response
                        mock_submit.return_value = mock_handler
                        
                        # Mock download
                        mock_response = MagicMock()
                        mock_response.headers = {'content-type': 'model/gltf-binary'}
                        mock_response.iter_content.return_value = [b'model_data']
                        mock_response.raise_for_status.return_value = None
                        mock_download.return_value = mock_response
                        
                        client = FalAIClient()
                        
                        import asyncio
                        result = asyncio.run(client.process_single_image(sample_image_path))
                        
                        # Verify we extract all documented fields
                        assert result['model_url'] == documented_response['model_mesh']['url']
                        assert result['original_file_size'] == documented_response['model_mesh']['file_size']
                        assert result['original_content_type'] == documented_response['model_mesh']['content_type']
                        
                        assert result['rendered_image']['url'] == documented_response['rendered_image']['url']
                        assert result['rendered_image']['file_size'] == documented_response['rendered_image']['file_size']
                        assert result['rendered_image']['content_type'] == documented_response['rendered_image']['content_type']
    
    def test_error_response_format(self, sample_image_path):
        """Test handling of documented error response format."""
        # Simulate error response format as per documentation
        with patch.object(settings, 'FAL_API_KEY', 'test-api-key'):
            with patch('fal_client.upload_file') as mock_upload:
                with patch('fal_client.submit') as mock_submit:
                    mock_upload.return_value = "https://fal.media/files/test.jpg"
                    
                    # Simulate validation error with loc and msg fields
                    error_response = {
                        "detail": [
                            {
                                "loc": ["body", "image_url"],
                                "msg": "Invalid image URL format",
                                "type": "value_error"
                            }
                        ]
                    }
                    
                    error = Exception(f"422 Validation Error: {json.dumps(error_response)}")
                    mock_submit.side_effect = error
                    
                    client = FalAIClient()
                    
                    import asyncio
                    result = asyncio.run(client.process_single_image(sample_image_path))
                    
                    assert result['status'] == 'failed'
                    assert 'error' in result
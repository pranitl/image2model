"""
Integration tests for the models API endpoints.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, Mock

from fastapi.testclient import TestClient
from app.main import app
from tests.mocks.fal_responses import TRIPO_SUCCESS, TRELLIS_SUCCESS


class TestModelsEndpoint:
    """Integration tests for /api/v1/models endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_upload_dir(self, monkeypatch, tmp_path):
        """Mock upload directory with test files."""
        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()
        monkeypatch.setattr("app.core.config.settings.UPLOAD_DIR", str(upload_dir))
        return upload_dir
    
    @pytest.fixture
    def test_image_file(self, mock_upload_dir):
        """Create a test image file in upload directory."""
        file_id = "test-file-123"
        file_path = mock_upload_dir / f"{file_id}.png"
        # Write minimal PNG header
        file_path.write_bytes(b'\x89PNG\r\n\x1a\n')
        return file_id, str(file_path)
    
    def test_generate_endpoint_tripo_success(self, client, test_image_file, mock_celery_task):
        """Test successful Tripo3D model generation."""
        file_id, file_path = test_image_file
        
        response = client.post(
            "/api/v1/models/generate",
            json={
                "file_id": file_id,
                "model_type": "tripo3d",
                "texture_enabled": True,
                "params": {"face_limit": 5000}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
        assert data["estimated_time"] == 180  # 3 minutes for Tripo
    
    def test_generate_endpoint_trellis_success(self, client, test_image_file, mock_celery_task):
        """Test successful Trellis model generation."""
        file_id, file_path = test_image_file
        
        response = client.post(
            "/api/v1/models/generate",
            json={
                "file_id": file_id,
                "model_type": "trellis",
                "params": {
                    "ss_guidance_strength": 5.0,
                    "texture_size": "2048"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
        assert data["estimated_time"] == 240  # 4 minutes for Trellis
    
    def test_generate_invalid_model_type(self, client, test_image_file):
        """Test generation with invalid model type."""
        file_id, _ = test_image_file
        
        response = client.post(
            "/api/v1/models/generate",
            json={
                "file_id": file_id,
                "model_type": "invalid_model"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        # Check the custom error format from FileValidationException
        assert data["error"] is True
        assert data["error_code"] == "FILEVALIDATIONEXCEPTION"
        assert "Unsupported model type: invalid_model" in data["message"]
    
    def test_generate_missing_file_id(self, client):
        """Test generation without file_id."""
        response = client.post(
            "/api/v1/models/generate",
            json={
                "model_type": "tripo3d"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        # Custom validation error format
        assert data["error"] is True
        assert data["error_code"] == "VALIDATION_ERROR"
        assert data["message"] == "Request validation failed"
        # Check validation errors in details
        assert "validation_errors" in data["details"]
        errors = data["details"]["validation_errors"]
        assert any("field required" in error["message"].lower() or "missing" in error["message"].lower() for error in errors)
    
    def test_generate_nonexistent_file(self, client, mock_upload_dir):
        """Test generation with non-existent file."""
        response = client.post(
            "/api/v1/models/generate",
            json={
                "file_id": "nonexistent-file-id",
                "model_type": "tripo3d"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["error"] is True
        assert data["error_code"] == "FILEVALIDATIONEXCEPTION"
        assert "File with ID nonexistent-file-id not found" in data["message"]
    
    def test_generate_with_custom_params(self, client, test_image_file, mock_celery_task):
        """Test that custom parameters are passed to the task."""
        file_id, _ = test_image_file
        
        # Mock the task delay to capture arguments
        captured_args = {}
        def capture_delay(*args, **kwargs):
            captured_args.update(kwargs)
            return Mock(id="task-123")
        
        with patch("app.workers.tasks.generate_3d_model_task.delay", side_effect=capture_delay):
            response = client.post(
                "/api/v1/models/generate",
                json={
                    "file_id": file_id,
                    "model_type": "trellis",
                    "params": {
                        "ss_guidance_strength": 9.0,
                        "mesh_simplify": 0.92,
                        "texture_size": "2048"
                    }
                }
            )
        
        assert response.status_code == 200
        assert captured_args["model_type"] == "trellis"
        assert captured_args["params"]["ss_guidance_strength"] == 9.0
        assert captured_args["params"]["mesh_simplify"] == 0.92
        assert captured_args["params"]["texture_size"] == "2048"
    
    def test_generate_with_invalid_params(self, client, test_image_file, mock_celery_task):
        """Test generation with invalid parameters."""
        file_id, _ = test_image_file
        
        # The endpoint doesn't validate params - it passes them to the worker
        # So even invalid params will result in a successful queue
        response = client.post(
            "/api/v1/models/generate",
            json={
                "file_id": file_id,
                "model_type": "tripo3d",
                "params": {"face_limit": -100}
            }
        )
        
        # Should successfully queue the task - validation happens in worker
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
    
    def test_available_models_endpoint(self, client):
        """Test listing available models."""
        response = client.get("/api/v1/models/available")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Check model names
        model_names = [m["name"] for m in data]
        assert "tripo3d" in model_names
        assert "trellis" in model_names
        
        # Check structure
        for model in data:
            assert "name" in model
            assert "description" in model
            assert "type" in model
            assert "supported_formats" in model
            assert isinstance(model["supported_formats"], list)
    
    def test_model_params_endpoint_tripo(self, client):
        """Test getting Tripo model parameters."""
        response = client.get("/api/v1/models/models/tripo3d/params")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["model_name"] == "tripo3d"
        assert "texture_enabled" in data["default_params"]
        assert data["default_params"]["texture_enabled"] is True
        
        # Check param schema
        assert "texture_enabled" in data["param_schema"]
        assert data["param_schema"]["texture_enabled"]["type"] == "boolean"
        assert "face_limit" in data["param_schema"]
        assert data["param_schema"]["face_limit"]["type"] == "integer"
    
    def test_model_params_endpoint_trellis(self, client):
        """Test getting Trellis model parameters."""
        response = client.get("/api/v1/models/models/trellis/params")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["model_name"] == "trellis"
        
        # Check defaults
        defaults = data["default_params"]
        assert defaults["ss_guidance_strength"] == 7.5
        assert defaults["texture_size"] == "1024"
        
        # Check schema
        schema = data["param_schema"]
        assert schema["ss_guidance_strength"]["min"] == 0
        assert schema["ss_guidance_strength"]["max"] == 10
        assert schema["texture_size"]["enum"] == ["512", "1024", "2048"]
    
    def test_model_params_invalid_model(self, client):
        """Test params endpoint with invalid model name."""
        response = client.get("/api/v1/models/models/invalid_model/params")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] is True
        assert data["error_code"] == "HTTP_404"
        assert "Model 'invalid_model' not found" in data["message"]
        assert "Available models: ['tripo3d', 'trellis']" in data["message"]
    
    def test_generate_legacy_compatibility(self, client, test_image_file, mock_celery_task):
        """Test backward compatibility with legacy texture_enabled field."""
        file_id, _ = test_image_file
        
        # Old API format
        response = client.post(
            "/api/v1/models/generate",
            json={
                "file_id": file_id,
                "model_type": "tripo3d",
                "texture_enabled": False,  # Legacy field
                "quality": "high"  # Legacy field
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
    
    def test_generate_mixed_params_format(self, client, test_image_file, mock_celery_task):
        """Test mixing legacy and new parameter formats."""
        file_id, _ = test_image_file
        
        captured_args = {}
        def capture_delay(*args, **kwargs):
            captured_args.update(kwargs)
            return Mock(id="task-123")
        
        with patch("app.workers.tasks.generate_3d_model_task.delay", side_effect=capture_delay):
            response = client.post(
                "/api/v1/models/generate",
                json={
                    "file_id": file_id,
                    "model_type": "tripo3d",
                    "texture_enabled": False,  # Legacy
                    "params": {"face_limit": 5000}  # New format
                }
            )
        
        assert response.status_code == 200
        # Legacy texture_enabled should be included in params
        assert captured_args["params"]["texture_enabled"] is False
        assert captured_args["params"]["face_limit"] == 5000
    
    def test_job_status_endpoint(self, client):
        """Test job status endpoint (placeholder implementation)."""
        response = client.get("/api/v1/models/job/test-job-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-job-123"
        assert data["status"] == "processing"  # Hardcoded in implementation
        assert data["progress"] == 45  # Hardcoded in implementation
        assert data["estimated_remaining"] == 75  # Hardcoded in implementation
        assert data["result_url"] is None  # Hardcoded in implementation
    
    def test_download_model_endpoint(self, client):
        """Test download model endpoint (not implemented)."""
        response = client.get("/api/v1/models/download/test-job-123")
        
        assert response.status_code == 501
        data = response.json()
        assert data["error"] is True
        assert data["error_code"] == "HTTP_501"
        assert data["message"] == "Model download not yet implemented"
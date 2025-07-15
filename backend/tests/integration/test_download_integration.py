"""
Integration tests for download endpoints with FAL.AI URLs.
"""

import pytest
import json
from unittest.mock import patch, Mock

from fastapi.testclient import TestClient
from app.main import app


class TestDownloadIntegration:
    """Integration tests for download API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client with auth dependency override."""
        from app.middleware.auth import get_optional_api_key
        
        # Override the auth dependency
        async def override_get_optional_api_key():
            return None
        
        app.dependency_overrides[get_optional_api_key] = override_get_optional_api_key
        
        client = TestClient(app)
        yield client
        
        # Clean up
        app.dependency_overrides.clear()
    
    @pytest.fixture
    def mock_job_result(self, mock_job_store):
        """Create a mock job result in job store."""
        job_id = "test-download-job"
        job_result = {
            "job_id": job_id,
            "model_type": "tripo3d",
            "files": [
                {
                    "filename": "model.glb",
                    "model_url": "https://fal.media/files/elephant/test_model.glb",
                    "file_size": 4404019,
                    "content_type": "model/gltf-binary",
                    "rendered_image": {
                        "url": "https://fal.media/files/tiger/preview.webp",
                        "file_size": 123456,
                        "content_type": "image/webp"
                    },
                    "task_id": "fal-task-123"
                }
            ],
            "total_files": 1,
            "successful_files": 1,
            "failed_files": 0
        }
        
        mock_job_store.set_job_result(job_id, job_result)
        return job_id, job_result
    
    def test_download_list_files_fal_urls(self, client, mock_job_result):
        """Test listing files returns FAL.AI URLs correctly."""
        job_id, expected_result = mock_job_result
        
        response = client.get(f"/api/v1/download/{job_id}/all")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["job_id"] == job_id
        assert data["total_files"] == 1
        assert data["model_type"] == "tripo3d"
        
        # Verify file info
        assert len(data["files"]) == 1
        file_info = data["files"][0]
        assert file_info["filename"] == "model.glb"
        assert file_info["size"] == 4404019
        assert file_info["mime_type"] == "model/gltf-binary"
        assert file_info["rendered_image"] is not None
        
        # Verify download URLs
        assert len(data["download_urls"]) == 1
        assert data["download_urls"][0] == "https://fal.media/files/elephant/test_model.glb"
    
    def test_download_direct_model_redirect(self, client, mock_job_result):
        """Test direct model download redirects to FAL.AI URL."""
        job_id, _ = mock_job_result
        
        response = client.get(
            f"/api/v1/download/{job_id}/model",
            follow_redirects=False  # Don't follow redirect
        )
        
        assert response.status_code == 302  # Redirect
        assert response.headers["location"] == "https://fal.media/files/elephant/test_model.glb"
        
        # Check cache headers
        assert response.headers["cache-control"] == "no-cache, no-store, must-revalidate"
    
    def test_download_specific_file_redirect(self, client, mock_job_result):
        """Test downloading specific file by name redirects correctly."""
        job_id, _ = mock_job_result
        
        response = client.get(
            f"/api/v1/download/{job_id}/model.glb",
            follow_redirects=False
        )
        
        assert response.status_code == 302
        assert response.headers["location"] == "https://fal.media/files/elephant/test_model.glb"
    
    def test_download_job_not_found(self, client):
        """Test 404 error for non-existent job."""
        response = client.get("/api/v1/download/nonexistent-job/all")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] is True
        assert data["error_code"] == "HTTP_404"
        assert "Job not found" in data["message"]
    
    def test_download_model_type_in_response(self, client, mock_job_store):
        """Test model_type field is included in responses."""
        # Create Trellis job result
        job_id = "trellis-job"
        trellis_result = {
            "job_id": job_id,
            "model_type": "trellis",  # Important for client rendering
            "files": [
                {
                    "filename": "trellis_model.glb",
                    "model_url": "https://fal.media/files/zebra/trellis.glb",
                    "file_size": 5123456,
                    "content_type": "model/gltf-binary"
                }
            ],
            "total_files": 1,
            "successful_files": 1,
            "failed_files": 0
        }
        
        mock_job_store.set_job_result(job_id, trellis_result)
        
        response = client.get(f"/api/v1/download/{job_id}/all")
        
        assert response.status_code == 200
        data = response.json()
        assert data["model_type"] == "trellis"
    
    def test_download_fallback_to_celery(self, client, mock_job_store):
        """Test fallback to Celery results when not in job store."""
        job_id = "celery-job"
        
        # Mock Redis scan for Celery results
        with patch("redis.Redis") as mock_redis_class:
            mock_redis = Mock()
            mock_redis_class.return_value = mock_redis
            
            # Mock scanning keys
            mock_redis.scan_iter.return_value = [
                b"celery-task-meta-task1",
                b"celery-task-meta-task2"
            ]
            
            # Mock task result with our job
            task_result = {
                "status": "SUCCESS",
                "result": {
                    "job_id": job_id,
                    "job_result": {
                        "job_id": job_id,
                        "model_type": "tripo3d",
                        "files": [{
                            "filename": "celery_model.glb",
                            "model_url": "https://fal.media/files/celery.glb",
                            "file_size": 1000000,
                            "content_type": "model/gltf-binary"
                        }],
                        "total_files": 1,
                        "successful_files": 1,
                        "failed_files": 0
                    }
                }
            }
            
            mock_redis.get.return_value = json.dumps(task_result).encode()
            
            response = client.get(f"/api/v1/download/{job_id}/all")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["files"]) == 1
            assert data["files"][0]["filename"] == "celery_model.glb"
    
    def test_download_legacy_local_files(self, client, tmp_path, monkeypatch):
        """Test backward compatibility with local file storage."""
        # Setup local file structure
        job_id = "legacy-job"
        job_dir = tmp_path / job_id
        job_dir.mkdir()
        
        model_file = job_dir / "model.glb"
        model_file.write_bytes(b"GLB model data")
        
        monkeypatch.setattr("app.core.config.settings.OUTPUT_DIR", str(tmp_path))
        
        response = client.get(f"/api/v1/download/{job_id}/all")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find local file
        assert len(data["files"]) == 1
        assert data["files"][0]["filename"] == "model.glb"
        assert data["download_urls"][0] == f"/api/v1/download/{job_id}/model.glb"
    
    def test_download_multiple_files(self, client, mock_job_store):
        """Test job with multiple generated files."""
        job_id = "multi-file-job"
        job_result = {
            "job_id": job_id,
            "model_type": "tripo3d",
            "files": [
                {
                    "filename": "model1.glb",
                    "model_url": "https://fal.media/files/model1.glb",
                    "file_size": 1000000,
                    "content_type": "model/gltf-binary"
                },
                {
                    "filename": "model2.glb",
                    "model_url": "https://fal.media/files/model2.glb",
                    "file_size": 2000000,
                    "content_type": "model/gltf-binary"
                }
            ],
            "total_files": 2,
            "successful_files": 2,
            "failed_files": 0
        }
        
        mock_job_store.set_job_result(job_id, job_result)
        
        response = client.get(f"/api/v1/download/{job_id}/all")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["files"]) == 2
        assert len(data["download_urls"]) == 2
    
    def test_download_direct_model_no_files(self, client, mock_job_store):
        """Test direct model download when job has no files."""
        job_id = "empty-job"
        job_result = {
            "job_id": job_id,
            "model_type": "tripo3d",
            "files": [],
            "total_files": 0,
            "successful_files": 0,
            "failed_files": 0
        }
        
        mock_job_store.set_job_result(job_id, job_result)
        
        response = client.get(f"/api/v1/download/{job_id}/model")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] is True
        assert "No model files found" in data["message"]
    
    def test_download_invalid_job_id(self, client):
        """Test validation of job ID format."""
        # Very long job ID
        response = client.get("/api/v1/download/" + "x" * 200 + "/all")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] is True
        assert "Invalid job ID length" in data["message"]
        
        # Invalid characters - test with special characters
        response = client.get("/api/v1/download/job@id!invalid/all")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] is True
        assert "Invalid job ID format" in data["message"]
    
    def test_download_invalid_filename(self, client, mock_job_result):
        """Test validation of filename format."""
        job_id, _ = mock_job_result
        
        # Test filename with null byte (security risk)
        response = client.get(f"/api/v1/download/{job_id}/file%00.glb")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] is True
        assert "Invalid filename" in data["message"]
        
        # Invalid extension
        response = client.get(f"/api/v1/download/{job_id}/model.exe")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] is True
        assert "Invalid file format" in data["message"]
    
    def test_download_with_auth(self, client, mock_job_result, monkeypatch):
        """Test download with API key authentication."""
        job_id, _ = mock_job_result
        
        # We need to temporarily remove the dependency override for this test
        # to test the actual auth flow
        from app.middleware.auth import get_optional_api_key
        app.dependency_overrides.pop(get_optional_api_key, None)
        
        # Mock production environment
        monkeypatch.setattr("app.core.config.settings.ENVIRONMENT", "production")
        
        # Mock session store
        with patch("app.core.session_store.session_store.verify_job_access") as mock_verify:
            mock_verify.return_value = True
            
            # Provide a proper Bearer token
            response = client.get(
                f"/api/v1/download/{job_id}/model",
                headers={"Authorization": "Bearer test-api-key"},
                follow_redirects=False
            )
            
            assert response.status_code == 302
            mock_verify.assert_called_once_with(job_id, "test-api-key")
            
        # Restore the override for other tests
        async def override_get_optional_api_key():
            return None
        app.dependency_overrides[get_optional_api_key] = override_get_optional_api_key
    
    def test_download_unauthorized(self, client, mock_job_result, monkeypatch):
        """Test unauthorized access in production mode."""
        job_id, _ = mock_job_result
        
        # Remove the dependency override to test actual auth
        from app.middleware.auth import get_optional_api_key
        app.dependency_overrides.pop(get_optional_api_key, None)
        
        monkeypatch.setattr("app.core.config.settings.ENVIRONMENT", "production")
        
        with patch("app.core.session_store.session_store.verify_job_access") as mock_verify:
            mock_verify.return_value = False
            
            response = client.get(
                f"/api/v1/download/{job_id}/model",
                headers={"Authorization": "Bearer wrong-key"},
                follow_redirects=False  # Don't follow redirect
            )
            
            assert response.status_code == 403
            data = response.json()
            assert data["error"] is True
            assert "Access denied" in data["message"]
            
        # Restore the override
        async def override_get_optional_api_key():
            return None
        app.dependency_overrides[get_optional_api_key] = override_get_optional_api_key
    
    def test_debug_endpoint(self, client, mock_job_store):
        """Test debug endpoint for troubleshooting."""
        job_id = "debug-job"
        mock_job_store.set_job_result(job_id, {"test": "data"})
        
        # Mock redis.from_url to prevent live Redis connection
        with patch("redis.from_url") as mock_redis_from_url:
            mock_redis = Mock()
            mock_redis_from_url.return_value = mock_redis
            
            # Mock Redis operations
            mock_redis.get.return_value = '{"test": "data"}'
            mock_redis.scan_iter.return_value = [f"job_result:{job_id}", "job_result:other"]
            
            response = client.get(f"/api/v1/debug/job/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["job_store_result"] is True
        assert "redis_url" in data
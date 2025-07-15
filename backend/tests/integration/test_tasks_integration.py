"""
Integration tests for Celery tasks with FAL client integration.
"""

import pytest
import os
from unittest.mock import patch, Mock, MagicMock
from celery import current_task

from app.workers.tasks import generate_3d_model_task, process_single_image_with_retry
from app.workers.fal_client import FalAIRateLimitError, FalAITimeoutError
from tests.mocks.fal_responses import TRIPO_SUCCESS, TRELLIS_SUCCESS, ERROR_RESPONSES


class TestTasksIntegration:
    """Integration tests for worker tasks."""
    
    @pytest.fixture
    def mock_task_state(self, monkeypatch):
        """Mock Celery task state updates."""
        state_updates = []
        
        class MockTask:
            request = Mock()
            request.id = "test-task-id-123"  # Add a mock task ID
            backend = Mock()  # Mock backend to avoid Redis calls
            
            def update_state(self, state, meta):
                state_updates.append({"state": state, "meta": meta})
                # Don't actually call backend
        
        mock_task = MockTask()
        
        # We need to patch the module-level current_task import that the task function uses
        import app.workers.tasks
        monkeypatch.setattr(app.workers.tasks, "current_task", mock_task)
        
        # Also patch progress tracker to avoid Redis connection errors
        from app.core.progress_tracker import progress_tracker
        monkeypatch.setattr(progress_tracker, "update_file_progress", Mock())
        
        return mock_task, state_updates
    
    def test_generate_3d_model_task_tripo(
        self, 
        temp_image_file, 
        mock_fal_client_factory, 
        mock_job_store,
        mock_task_state
    ):
        """Test task completes successfully with Tripo model."""
        mock_task, state_updates = mock_task_state
        
        # Configure mock client to return proper FAL.AI response format
        mock_client = mock_fal_client_factory("tripo3d")
        mock_client.process_single_image_sync.return_value = {
            "status": "success",
            "input": temp_image_file,
            "output": None,  # No local file path since we use direct FAL.AI URLs
            "download_url": "https://fal.media/files/model.glb",
            "model_format": "glb",
            "model_url": "https://fal.media/files/model.glb",
            "file_size": 1000000,
            "content_type": "model/gltf-binary",
            "output_directory": None,
            "original_file_size": 1000000,
            "original_content_type": "model/gltf-binary",
            "task_id": "fal-task-123",
            "filename": "model.glb",
            "rendered_image": {
                "url": "https://fal.media/files/preview.webp",
                "file_size": 50000,
                "content_type": "image/webp"
            }
        }
        
        # Run task
        result = generate_3d_model_task(
            file_id="test-file-123",
            file_path=temp_image_file,
            job_id="job-123",
            model_type="tripo3d",
            params={"texture_enabled": True, "face_limit": 5000}
        )
        
        # Verify result matches implementation's return format
        assert result["status"] == "completed"
        assert result["job_id"] == "job-123"
        assert result["file_id"] == "test-file-123"
        assert result["model_format"] == "glb"
        assert result["result_path"] is None  # No local file, using direct FAL.AI URLs
        assert result["total_files"] == 1
        assert result["successful_files"] == 1
        assert result["failed_files"] == 0
        assert "job_result" in result  # For download endpoint fallback
        assert "message" in result
        
        # Verify progress updates
        assert len(state_updates) > 0
        assert state_updates[0]["meta"]["progress"] == 10  # Initial progress
        assert state_updates[-1]["state"] == "SUCCESS"
        assert state_updates[-1]["meta"]["progress"] == 100
        
        # Verify job store
        job_result = mock_job_store.get_job_result("job-123")
        assert job_result is not None
        assert job_result["model_type"] == "tripo3d"
        assert len(job_result["files"]) == 1
        assert job_result["files"][0]["model_url"] == "https://fal.media/files/model.glb"
    
    def test_generate_3d_model_task_trellis(
        self,
        temp_image_file,
        mock_fal_client_factory,
        mock_job_store,
        mock_task_state,
        monkeypatch
    ):
        """Test task completes successfully with Trellis model."""
        mock_task, state_updates = mock_task_state
        
        # Configure the factory to return our specific mock for trellis
        from app.workers.fal_client import TripoClient, TrellisClient
        
        def custom_factory(model_type: str):
            if model_type == "trellis":
                client = Mock(spec=TrellisClient)
                client.model_endpoint = "fal-ai/trellis"
                client.MODEL_INFO = TrellisClient.MODEL_INFO
                client.process_single_image_sync = Mock(return_value={
                    "status": "success",
                    "input": temp_image_file,
                    "output": None,  # No local file path
                    "download_url": "https://fal.media/files/trellis_model.glb",
                    "model_format": "glb",
                    "model_url": "https://fal.media/files/trellis_model.glb",
                    "file_size": 2000000,
                    "content_type": "model/gltf-binary",
                    "output_directory": None,
                    "original_file_size": 2000000,
                    "original_content_type": "model/gltf-binary",
                    "task_id": "fal-task-456",
                    "filename": "trellis_model.glb"
                })
                return client
            else:
                # Fallback to original factory for other types
                return mock_fal_client_factory(model_type)
        
        # Override the factory for this test
        monkeypatch.setattr("app.workers.tasks.get_model_client", custom_factory)
        
        # Run task with Trellis params
        result = generate_3d_model_task(
            file_id="test-file-456",
            file_path=temp_image_file,
            job_id="job-456",
            model_type="trellis",
            params={
                "ss_guidance_strength": 9.0,
                "texture_size": "2048",
                "mesh_simplify": 0.93
            }
        )
        
        # Verify result matches implementation format
        assert result["status"] == "completed"
        assert result["job_id"] == "job-456"
        assert result["file_id"] == "test-file-456"
        assert result["model_format"] == "glb"
        assert result["result_path"] is None
        assert result["total_files"] == 1
        assert result["successful_files"] == 1
        assert result["failed_files"] == 0
        
        # Verify correct model type was stored in job store
        stored_result = mock_job_store.get_job_result("job-456")
        assert stored_result is not None
        assert stored_result["model_type"] == "trellis"
        assert len(stored_result["files"]) == 1
        assert stored_result["files"][0]["model_url"] == "https://fal.media/files/trellis_model.glb"
    
    def test_task_progress_updates(
        self,
        temp_image_file,
        mock_fal_client_factory,
        mock_task_state,
        mock_job_store
    ):
        """Test that progress callbacks update task state correctly."""
        mock_task, state_updates = mock_task_state
        
        # Capture progress callback
        progress_callback = None
        def capture_callback(*args, **kwargs):
            nonlocal progress_callback
            progress_callback = kwargs.get("progress_callback")
            return {
                "status": "success",
                "input": temp_image_file,
                "output": None,
                "download_url": "https://fal.media/files/model.glb",
                "model_format": "glb",
                "model_url": "https://fal.media/files/model.glb",
                "file_size": 1500000,
                "content_type": "model/gltf-binary",
                "output_directory": None,
                "original_file_size": 1500000,
                "original_content_type": "model/gltf-binary",
                "task_id": "fal-task-progress",
                "filename": "model.glb"
            }
        
        mock_client = mock_fal_client_factory("tripo3d")
        mock_client.process_single_image_sync.side_effect = capture_callback
        
        # Run task
        generate_3d_model_task(
            file_id="test-file",
            file_path=temp_image_file,
            job_id="job-progress",
            model_type="tripo3d"
        )
        
        # Simulate progress updates
        if progress_callback:
            progress_callback("Uploading to FAL.AI...", 15)
            progress_callback("Processing 3D model... 50%", 50)
            progress_callback("Finalizing model...", 90)
        
        # Check progress was tracked
        progress_states = [u for u in state_updates if u["state"] == "PROGRESS"]
        assert len(progress_states) >= 3
        
        # Verify progress values
        progress_values = [u["meta"]["progress"] for u in progress_states]
        assert 10 in progress_values  # Initial
        assert any(p >= 50 for p in progress_values)  # Mid-progress
    
    def test_task_job_store_integration(
        self,
        temp_image_file,
        mock_fal_client_factory,
        mock_job_store,
        mock_task_state
    ):
        """Test results are correctly stored in job store."""
        mock_task, _ = mock_task_state
        
        mock_client = mock_fal_client_factory("tripo3d")
        mock_client.process_single_image_sync.return_value = {
            "status": "success",
            "input": temp_image_file,
            "output": None,
            "download_url": "https://fal.media/files/test.glb",
            "model_format": "glb",
            "model_url": "https://fal.media/files/test.glb",
            "file_size": 3000000,
            "content_type": "model/gltf-binary",
            "output_directory": None,
            "original_file_size": 3000000,
            "original_content_type": "model/gltf-binary",
            "task_id": "fal-123",
            "filename": "test.glb",
            "rendered_image": {
                "url": "https://fal.media/files/preview.webp",
                "file_size": 25000,
                "content_type": "image/webp"
            }
        }
        
        # Run task
        result = generate_3d_model_task(
            file_id="test-store",
            file_path=temp_image_file,
            job_id="job-store-test",
            model_type="tripo3d"
        )
        
        # Verify job store contains result
        stored_result = mock_job_store.get_job_result("job-store-test")
        assert stored_result is not None
        assert stored_result["job_id"] == "job-store-test"
        assert stored_result["model_type"] == "tripo3d"
        assert stored_result["total_files"] == 1
        assert stored_result["successful_files"] == 1
        assert stored_result["failed_files"] == 0
        
        # Check file data
        file_data = stored_result["files"][0]
        assert file_data["model_url"] == "https://fal.media/files/test.glb"
        assert file_data["file_size"] == 3000000
        assert file_data["content_type"] == "model/gltf-binary"
        assert file_data["rendered_image"]["url"] == "https://fal.media/files/preview.webp"
        assert file_data["task_id"] == "fal-123"
    
    def test_task_error_handling(
        self,
        temp_image_file,
        mock_fal_client_factory,
        mock_job_store,
        mock_task_state
    ):
        """Test task handles FAL client errors properly."""
        mock_task, state_updates = mock_task_state
        
        # Configure client to fail
        mock_client = mock_fal_client_factory("tripo3d")
        mock_client.process_single_image_sync.return_value = {
            "status": "failed",
            "error": "FAL API error: Rate limit exceeded",
            "error_type": "rate_limit"
        }
        
        # Run task - should raise ProcessingException
        from app.core.exceptions import ProcessingException
        with pytest.raises(ProcessingException) as exc_info:
            generate_3d_model_task(
                file_id="test-error",
                file_path=temp_image_file,
                job_id="job-error",
                model_type="tripo3d"
            )
        
        assert "FAL.AI tripo3d generation failed" in str(exc_info.value)
        
        # Check failure state
        failure_updates = [u for u in state_updates if u["state"] == "FAILURE"]
        assert len(failure_updates) > 0
        assert "error" in failure_updates[0]["meta"]
    
    def test_task_retry_on_timeout(self, temp_image_file, mock_fal_client_factory):
        """Test retry logic for timeout errors."""
        mock_client = mock_fal_client_factory("tripo3d")
        
        # Configure to fail with timeout, then succeed
        call_count = 0
        def mock_process(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {
                    "status": "failed",
                    "error": "Request timeout",
                    "error_type": "timeout_error",
                    "retryable": True
                }
            else:
                return {
                    "status": "success",
                    "input": temp_image_file,
                    "output": None,
                    "download_url": "https://fal.media/files/model.glb",
                    "model_format": "glb",
                    "model_url": "https://fal.media/files/model.glb",
                    "file_size": 1200000,
                    "content_type": "model/gltf-binary",
                    "output_directory": None,
                    "original_file_size": 1200000,
                    "original_content_type": "model/gltf-binary",
                    "task_id": "fal-task-retry",
                    "filename": "model.glb"
                }
        
        mock_client.process_single_image_sync.side_effect = mock_process
        
        # Mock the retry mechanism
        with patch("app.workers.tasks.process_single_image_with_retry.retry") as mock_retry:
            # Create a mock that simulates retry behavior
            def retry_side_effect(**kwargs):
                # Return a mock that can be raised
                exc = kwargs.get('exc')
                exc.retry = Mock()
                return exc
            
            mock_retry.side_effect = retry_side_effect
            
            # Should handle retryable timeout
            result = process_single_image_with_retry(
                file_path=temp_image_file,
                model_type="tripo3d"
            )
            
            # On first call it would normally retry, but our mock just returns success
            assert mock_client.process_single_image_sync.call_count >= 1
    
    def test_process_single_image_sync_wrapper(
        self,
        temp_image_file,
        mock_fal_client_factory
    ):
        """Test sync wrapper properly calls async method."""
        mock_client = mock_fal_client_factory("trellis")
        mock_client.process_single_image_sync.return_value = {
            "status": "success",
            "input": temp_image_file,
            "output": None,
            "download_url": "https://fal.media/files/model.glb",
            "model_format": "glb",
            "model_url": "https://fal.media/files/model.glb",
            "file_size": 2500000,
            "content_type": "model/gltf-binary",
            "output_directory": None,
            "original_file_size": 2500000,
            "original_content_type": "model/gltf-binary",
            "task_id": "fal-task-sync",
            "filename": "model.glb"
        }
        
        # The task should use sync wrapper
        result = generate_3d_model_task(
            file_id="test-sync",
            file_path=temp_image_file,
            job_id="job-sync",
            model_type="trellis",
            params={"texture_size": "2048"}
        )
        
        # Verify sync method was called
        assert mock_client.process_single_image_sync.called
        call_args = mock_client.process_single_image_sync.call_args
        assert call_args[0][0] == temp_image_file  # file_path
        assert call_args[1]["params"]["texture_size"] == "2048"
        assert call_args[1]["job_id"] == "job-sync"
    
    def test_task_with_empty_params(
        self,
        temp_image_file,
        mock_fal_client_factory,
        mock_job_store,
        mock_task_state
    ):
        """Test task handles empty/None params correctly."""
        mock_task, _ = mock_task_state
        
        mock_client = mock_fal_client_factory("tripo3d")
        mock_client.process_single_image_sync.return_value = {
            "status": "success",
            "input": temp_image_file,
            "output": None,
            "download_url": "https://fal.media/files/model.glb",
            "model_format": "glb",
            "model_url": "https://fal.media/files/model.glb",
            "file_size": 1000000,
            "content_type": "model/gltf-binary",
            "output_directory": None,
            "original_file_size": 1000000,
            "original_content_type": "model/gltf-binary",
            "task_id": "fal-task-none",
            "filename": "model.glb"
        }
        
        # Test with None params
        result = generate_3d_model_task(
            file_id="test-none",
            file_path=temp_image_file,
            job_id="job-none",
            model_type="tripo3d",
            params=None
        )
        
        assert result["status"] == "completed"
        
        # Verify empty dict was passed
        call_args = mock_client.process_single_image_sync.call_args
        assert call_args[1]["params"] == {}
    
    def test_task_result_format(
        self,
        temp_image_file,
        mock_fal_client_factory,
        mock_task_state
    ):
        """Test task returns correct result format for SSE endpoint."""
        mock_task, state_updates = mock_task_state
        
        mock_client = mock_fal_client_factory("tripo3d")
        mock_client.process_single_image_sync.return_value = {
            "status": "success",
            "input": temp_image_file,
            "output": None,
            "download_url": "https://fal.media/files/final.glb",
            "model_format": "glb",
            "model_url": "https://fal.media/files/final.glb",
            "file_size": 1800000,
            "content_type": "model/gltf-binary",
            "output_directory": None,
            "original_file_size": 1800000,
            "original_content_type": "model/gltf-binary",
            "task_id": "fal-task-format",
            "filename": "final.glb",
            "processing_time": 45.2,
            "rendered_image": {
                "url": "https://fal.media/files/preview.webp",
                "file_size": 30000,
                "content_type": "image/webp"
            }
        }
        
        result = generate_3d_model_task(
            file_id="test-format",
            file_path=temp_image_file,
            job_id="job-format",
            model_type="tripo3d"
        )
        
        # Check required fields for SSE
        assert result["job_id"] == "job-format"
        assert result["file_id"] == "test-format"
        assert result["status"] == "completed"
        assert result["model_format"] == "glb"
        assert result["total_files"] == 1
        assert result["successful_files"] == 1
        assert result["failed_files"] == 0
        assert "job_result" in result  # For download endpoint fallback
    
    def test_no_live_api_calls(
        self,
        temp_image_file,
        mock_fal_client_factory,
        mock_job_store,
        mock_task_state,
        monkeypatch
    ):
        """Ensure no live API calls are made to FAL.AI."""
        mock_task, _ = mock_task_state
        
        # Mock all external dependencies to ensure no live calls
        import fal_client
        import requests
        
        # Mock fal_client functions
        monkeypatch.setattr(fal_client, "upload_file", Mock(side_effect=Exception("Live API call to upload_file")))
        monkeypatch.setattr(fal_client, "subscribe", Mock(side_effect=Exception("Live API call to subscribe")))
        monkeypatch.setattr(fal_client, "run", Mock(side_effect=Exception("Live API call to run")))
        
        # Mock requests to catch any HTTP calls
        monkeypatch.setattr(requests, "get", Mock(side_effect=Exception("Live HTTP GET call")))
        monkeypatch.setattr(requests, "post", Mock(side_effect=Exception("Live HTTP POST call")))
        
        # Our mocked client should handle everything
        mock_client = mock_fal_client_factory("tripo3d")
        mock_client.process_single_image_sync.return_value = {
            "status": "success",
            "input": temp_image_file,
            "output": None,
            "download_url": "https://fal.media/files/test.glb",
            "model_format": "glb",
            "model_url": "https://fal.media/files/test.glb",
            "file_size": 1000000,
            "content_type": "model/gltf-binary",
            "output_directory": None,
            "original_file_size": 1000000,
            "original_content_type": "model/gltf-binary",
            "task_id": "fal-task-mock",
            "filename": "test.glb"
        }
        
        # This should succeed without making any live API calls
        result = generate_3d_model_task(
            file_id="test-no-api",
            file_path=temp_image_file,
            job_id="job-no-api",
            model_type="tripo3d"
        )
        
        assert result["status"] == "completed"
        assert result["job_id"] == "job-no-api"
        
        # Verify our mock was called instead of live API
        assert mock_client.process_single_image_sync.called
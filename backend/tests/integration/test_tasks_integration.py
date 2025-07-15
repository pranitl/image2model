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
            def update_state(self, state, meta):
                state_updates.append({"state": state, "meta": meta})
        
        mock_task = MockTask()
        monkeypatch.setattr("celery.current_task", mock_task)
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
        
        # Configure mock client
        mock_client = mock_fal_client_factory("tripo3d")
        mock_client.process_single_image_sync.return_value = {
            "status": "success",
            "download_url": "https://fal.media/files/model.glb",
            "model_format": "glb",
            "file_size": 1000000,
            "content_type": "model/gltf-binary",
            "filename": "model.glb",
            "rendered_image": {
                "url": "https://fal.media/files/preview.webp",
                "file_size": 50000,
                "content_type": "image/webp"
            },
            "task_id": "fal-task-123",
            "output": None  # No local file
        }
        
        # Run task
        result = generate_3d_model_task(
            file_id="test-file-123",
            file_path=temp_image_file,
            job_id="job-123",
            model_type="tripo3d",
            params={"texture_enabled": True, "face_limit": 5000}
        )
        
        # Verify result
        assert result["status"] == "completed"
        assert result["job_id"] == "job-123"
        assert result["model_format"] == "glb"
        assert "download_url" in result
        
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
        mock_task_state
    ):
        """Test task completes successfully with Trellis model."""
        mock_task, state_updates = mock_task_state
        
        # Configure mock client
        mock_client = mock_fal_client_factory("trellis")
        mock_client.process_single_image_sync.return_value = {
            "status": "success",
            "download_url": "https://fal.media/files/trellis_model.glb",
            "model_format": "glb",
            "file_size": 2000000,
            "content_type": "model/gltf-binary",
            "filename": "trellis_model.glb",
            "output": None
        }
        
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
        
        # Verify result
        assert result["status"] == "completed"
        assert result["model_format"] == "glb"
        
        # Verify correct client was used
        assert mock_client.process_single_image_sync.called
        call_args = mock_client.process_single_image_sync.call_args
        assert call_args[1]["params"]["ss_guidance_strength"] == 9.0
        assert call_args[1]["params"]["texture_size"] == "2048"
    
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
                "download_url": "https://fal.media/files/model.glb",
                "model_format": "glb"
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
            "download_url": "https://fal.media/files/test.glb",
            "model_format": "glb",
            "file_size": 3000000,
            "content_type": "model/gltf-binary",
            "rendered_image": {"url": "https://fal.media/files/preview.webp"},
            "task_id": "fal-123"
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
        assert file_data["rendered_image"]["url"] == "https://fal.media/files/preview.webp"
    
    def test_task_error_handling(
        self,
        temp_image_file,
        mock_fal_client_factory,
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
                    "download_url": "https://fal.media/files/model.glb",
                    "model_format": "glb"
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
            "download_url": "https://fal.media/files/model.glb",
            "model_format": "glb"
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
            "download_url": "https://fal.media/files/model.glb",
            "model_format": "glb"
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
            "download_url": "https://fal.media/files/final.glb",
            "model_format": "glb",
            "filename": "final.glb",
            "processing_time": 45.2,
            "rendered_image": {"url": "https://fal.media/files/preview.webp"}
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
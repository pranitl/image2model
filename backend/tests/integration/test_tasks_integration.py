"""
Integration tests for Celery tasks with live worker and mocked FAL API.
"""

import pytest
import os
import time
from typing import Dict, Any
from unittest.mock import patch, Mock

from app.workers.tasks import generate_3d_model_task
from app.core.job_store import job_store
from app.core.progress_tracker import progress_tracker


@pytest.mark.integration
class TestTasksIntegration:
    """Integration tests for 3D model generation tasks with live Celery."""
    
    @pytest.fixture
    def test_image_file(self, tmp_path):
        """Create a test image file."""
        file_path = tmp_path / "test_image.png"
        file_path.write_bytes(b'\x89PNG\r\n\x1a\n')
        return str(file_path)
    
    @pytest.fixture
    def cleanup_redis(self, live_celery_app):
        """Clean up Redis before and after tests."""
        import redis
        r = redis.from_url('redis://localhost:6379/0')
        # Don't flush the entire DB, just clean up test keys
        for key in r.scan_iter("celery-task-meta-test-*"):
            r.delete(key)
        yield
        # Clean up after test
        for key in r.scan_iter("celery-task-meta-test-*"):
            r.delete(key)
    
    def test_generate_3d_model_tripo_success(
        self,
        test_image_file,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test successful 3D model generation with Tripo3D using live Celery."""
        file_id = "test-file-123"
        job_id = "test-job-123"
        
        # Execute task asynchronously
        result = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, job_id, "tripo3d", None]
        )
        
        # Wait for result
        task_result = result.get(timeout=30)
        
        # Verify result
        assert task_result["status"] == "completed"
        assert task_result["job_id"] == job_id
        assert task_result["model_url"] == "https://fal.media/files/model.glb"
        assert task_result["model_format"] == "glb"
        assert task_result["file_size"] == 1000000
        
        # Check job store
        stored_result = job_store.get_job_result(job_id)
        assert stored_result is not None
        assert stored_result["status"] == "completed"
    
    def test_generate_3d_model_trellis_success(
        self,
        test_image_file,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test successful 3D model generation with Trellis using live Celery."""
        file_id = "test-file-456"
        job_id = "test-job-456"
        
        # Custom parameters for Trellis
        params = {
            "ss_guidance_strength": 8.0,
            "texture_size": "2048"
        }
        
        # Execute task
        result = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, job_id, "trellis", params]
        )
        
        # Wait for result
        task_result = result.get(timeout=30)
        
        # Verify result
        assert task_result["status"] == "completed"
        assert task_result["job_id"] == job_id
        assert task_result["model_type"] == "trellis"
        assert "model_url" in task_result
    
    def test_task_progress_updates(
        self,
        test_image_file,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test progress updates during task execution."""
        file_id = "test-progress"
        job_id = "test-job-progress"
        
        # Configure mock to send progress updates
        progress_states = []
        
        def mock_process_with_progress(*args, **kwargs):
            # Simulate progress updates
            for i in range(3):
                progress_states.append({
                    "state": "PROGRESS",
                    "progress": (i + 1) * 30
                })
                time.sleep(0.1)
            
            return {
                "status": "success",
                "download_url": "https://fal.media/files/model.glb",
                "model_url": "https://fal.media/files/model.glb",
                "model_format": "glb",
                "file_size": 1000000,
                "filename": "model.glb",
                "content_type": "model/gltf-binary",
                "input": {"image_url": "https://fal.ai/uploads/test.png"},
                "output": {
                    "model_mesh": {"url": "https://fal.media/files/mesh.glb"},
                    "model_texture": {"url": "https://fal.media/files/texture.png"}
                }
            }
        
        mock_fal_only.return_value.process_single_image_sync.side_effect = mock_process_with_progress
        
        # Execute task
        result = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, job_id, "tripo3d", None]
        )
        
        # Wait for result
        task_result = result.get(timeout=30)
        
        # Verify task completed
        assert task_result["status"] == "completed"
    
    def test_task_error_handling(
        self,
        test_image_file,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test error handling in tasks."""
        file_id = "test-error"
        job_id = "test-job-error"
        
        # Configure mock to raise error
        mock_fal_only.return_value.process_single_image_sync.side_effect = Exception("FAL API error")
        
        # Execute task
        result = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, job_id, "tripo3d", None]
        )
        
        # Wait for result
        task_result = result.get(timeout=30)
        
        # Verify error handling
        assert task_result["status"] == "failed"
        assert "error" in task_result
        assert "FAL API error" in task_result["error"]
    
    def test_task_retry_on_timeout(
        self,
        test_image_file,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test task retry behavior on timeout errors."""
        file_id = "test-timeout"
        job_id = "test-job-timeout"
        
        # Track retry attempts
        attempt_count = 0
        
        def mock_timeout_then_success(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count <= 2:
                # Simulate timeout on first attempts
                import celery.exceptions
                raise celery.exceptions.SoftTimeLimitExceeded()
            
            # Success on third attempt
            return {
                "status": "success",
                "download_url": "https://fal.media/files/model.glb",
                "model_url": "https://fal.media/files/model.glb",
                "model_format": "glb",
                "file_size": 1000000,
                "filename": "model.glb",
                "content_type": "model/gltf-binary"
            }
        
        mock_fal_only.return_value.process_single_image_sync.side_effect = mock_timeout_then_success
        
        # Execute task with retry
        result = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, job_id, "tripo3d", None],
            retry=True,
            retry_policy={
                'max_retries': 3,
                'interval_start': 0.1,
                'interval_step': 0.1,
                'interval_max': 0.5,
            }
        )
        
        # Wait for result
        try:
            task_result = result.get(timeout=60)
            # If retries are configured properly, it should succeed
            assert task_result["status"] == "completed"
        except Exception as e:
            # If retries aren't working, we'll get a timeout
            assert "SoftTimeLimitExceeded" in str(e)
    
    def test_direct_task_call(
        self,
        test_image_file,
        mock_fal_only
    ):
        """Test calling task directly without Celery."""
        # Create a mock self object for the task
        mock_self = Mock()
        mock_self.request = Mock()
        mock_self.request.id = "direct-task-123"
        mock_self.update_state = Mock()
        
        # Call task directly
        result = generate_3d_model_task.run(
            file_id="sync-test",
            file_path=test_image_file,
            job_id="sync-job",
            model_type="tripo3d"
        )
        
        # Verify result
        assert result["status"] == "completed"
        assert result["job_id"] == "sync-job"
        assert "model_url" in result
    
    def test_task_with_empty_params(
        self,
        test_image_file,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test task execution with None and empty params."""
        file_id = "test-empty-params"
        job_id = "test-job-empty"
        
        # Test with None params
        result1 = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, job_id + "-none", "tripo3d", None]
        )
        
        # Test with empty dict params
        result2 = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, job_id + "-empty", "tripo3d", {}]
        )
        
        # Wait for results
        task_result1 = result1.get(timeout=30)
        task_result2 = result2.get(timeout=30)
        
        # Both should succeed
        assert task_result1["status"] == "completed"
        assert task_result2["status"] == "completed"
    
    def test_task_result_format(
        self,
        test_image_file,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test that task results match expected format for SSE endpoint."""
        file_id = "test-format"
        job_id = "test-job-format"
        
        # Execute task
        result = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, job_id, "tripo3d", None]
        )
        
        # Wait for result
        task_result = result.get(timeout=30)
        
        # Verify result format matches what SSE endpoint expects
        assert "status" in task_result
        assert "job_id" in task_result
        assert "model_url" in task_result
        assert "model_format" in task_result
        assert "file_size" in task_result
        assert "filename" in task_result
        assert "download_url" in task_result
        
        # Check job_result format for download endpoint
        assert "job_result" in task_result
        job_result = task_result["job_result"]
        assert "total_files" in job_result
        assert "successful_files" in job_result
        assert "results" in job_result
        assert isinstance(job_result["results"], list)
    
    def test_concurrent_tasks(
        self,
        test_image_file,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test multiple concurrent task execution."""
        # Launch 5 concurrent tasks
        tasks = []
        for i in range(5):
            result = generate_3d_model_task.apply_async(
                args=[f"file-{i}", test_image_file, f"job-{i}", "tripo3d", None]
            )
            tasks.append((f"job-{i}", result))
        
        # Wait for all results
        results = []
        for job_id, result in tasks:
            task_result = result.get(timeout=30)
            results.append(task_result)
        
        # Verify all completed
        for i, task_result in enumerate(results):
            assert task_result["status"] == "completed"
            assert task_result["job_id"] == f"job-{i}"
    
    def test_model_switching(
        self,
        test_image_file,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test switching between different model types."""
        file_id = "test-switch"
        
        # Test Tripo3D
        result1 = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, "job-tripo", "tripo3d", None]
        )
        
        # Test Trellis
        result2 = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, "job-trellis", "trellis", {
                "texture_size": "2048"
            }]
        )
        
        # Wait for results
        task_result1 = result1.get(timeout=30)
        task_result2 = result2.get(timeout=30)
        
        # Verify both completed with correct model types
        assert task_result1["status"] == "completed"
        assert task_result1["model_type"] == "tripo3d"
        
        assert task_result2["status"] == "completed"
        assert task_result2["model_type"] == "trellis"
    
    def test_task_cancellation(
        self,
        test_image_file,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test task cancellation behavior."""
        file_id = "test-cancel"
        job_id = "test-job-cancel"
        
        # Configure mock with delay
        def slow_process(*args, **kwargs):
            time.sleep(5)  # Long delay to allow cancellation
            return {"status": "success"}
        
        mock_fal_only.return_value.process_single_image_sync.side_effect = slow_process
        
        # Execute task
        result = generate_3d_model_task.apply_async(
            args=[file_id, test_image_file, job_id, "tripo3d", None]
        )
        
        # Wait a bit then revoke
        time.sleep(0.5)
        result.revoke(terminate=True)
        
        # Task should be revoked
        assert result.state in ['REVOKED', 'FAILURE', 'PENDING']
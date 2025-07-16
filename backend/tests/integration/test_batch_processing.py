"""
Integration tests for batch processing with parallel execution using live Celery.
"""

import pytest
import os
import time
from typing import Dict, Any, List
from unittest.mock import patch, Mock

from app.workers.tasks import (
    process_batch,
    process_file_in_batch,
    finalize_batch_results
)
from app.core.job_store import job_store
from app.core.progress_tracker import progress_tracker


@pytest.mark.integration
class TestBatchProcessing:
    """Integration tests for parallel batch processing with live Celery."""
    
    @pytest.fixture
    def batch_files(self, tmp_path):
        """Create multiple test files for batch processing."""
        files = []
        for i in range(5):
            file_path = tmp_path / f"test_image_{i}.png"
            file_path.write_bytes(b'\x89PNG\r\n\x1a\n')
            files.append({
                "file_id": f"test-file-{i}",
                "file_path": str(file_path),
                "original_filename": f"test_image_{i}.png"
            })
        return files
    
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
    
    def test_batch_5_files_success(
        self,
        batch_files,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test successful batch processing of 5 files with live Celery."""
        job_id = "test-batch-5-success"
        
        # Execute batch processing
        result = process_batch.apply_async(
            args=[batch_files, job_id, "tripo3d", None]
        )
        
        # Wait for result with timeout
        batch_result = result.get(timeout=30)
        
        # Verify results
        assert batch_result["status"] == "completed"
        assert batch_result["total_files"] == 5
        assert batch_result["successful_files"] == 5
        assert batch_result["failed_files"] == 0
        assert len(batch_result["results"]) == 5
        
        # Check job store
        stored_result = job_store.get_job_result(job_id)
        assert stored_result is not None
        assert stored_result["download_url"] == f"/api/v1/download/{job_id}"
    
    def test_batch_10_files_parallel(
        self,
        tmp_path,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test parallel processing of 10 files."""
        # Create 10 files
        files = []
        for i in range(10):
            file_path = tmp_path / f"test_image_{i}.png"
            file_path.write_bytes(b'\x89PNG\r\n\x1a\n')
            files.append({
                "file_id": f"test-file-{i}",
                "file_path": str(file_path),
                "original_filename": f"test_image_{i}.png"
            })
        
        job_id = "test-batch-10-parallel"
        
        # Execute batch processing
        result = process_batch.apply_async(
            args=[files, job_id, "tripo3d", None]
        )
        
        # Wait for result
        batch_result = result.get(timeout=60)
        
        # Verify parallel execution
        assert batch_result["status"] == "completed"
        assert batch_result["total_files"] == 10
        assert batch_result["successful_files"] == 10
        assert len(batch_result["results"]) == 10
    
    def test_batch_mixed_models(
        self,
        batch_files,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test batch with different model types."""
        job_id = "test-batch-mixed"
        
        # Process first batch with Tripo
        result1 = process_batch.apply_async(
            args=[batch_files[:3], f"{job_id}-tripo", "tripo3d", None]
        )
        
        # Process second batch with Trellis
        result2 = process_batch.apply_async(
            args=[batch_files[3:], f"{job_id}-trellis", "trellis", None]
        )
        
        # Wait for both results
        batch_result1 = result1.get(timeout=30)
        batch_result2 = result2.get(timeout=30)
        
        # Verify both completed
        assert batch_result1["status"] == "completed"
        assert batch_result1["total_files"] == 3
        
        assert batch_result2["status"] == "completed"
        assert batch_result2["total_files"] == 2
    
    def test_batch_partial_success(
        self,
        batch_files,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test batch with some failures."""
        job_id = "test-batch-partial"
        
        # Configure mock to fail for specific files
        def custom_process(*args, **kwargs):
            file_path = args[0] if args else kwargs.get('file_path', '')
            if 'test_image_2' in file_path or 'test_image_3' in file_path:
                raise Exception("Simulated processing error")
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
        
        # Apply custom mock
        mock_fal_only.return_value.process_single_image_sync.side_effect = custom_process
        
        # Execute batch
        result = process_batch.apply_async(
            args=[batch_files, job_id, "tripo3d", None]
        )
        
        batch_result = result.get(timeout=30)
        
        # Verify partial success
        assert batch_result["status"] == "partially_completed"
        assert batch_result["total_files"] == 5
        assert batch_result["successful_files"] == 3
        assert batch_result["failed_files"] == 2
    
    def test_batch_with_timeout(
        self,
        batch_files,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test batch processing with timeout handling."""
        job_id = "test-batch-timeout"
        
        # Configure mock to simulate timeout
        def timeout_process(*args, **kwargs):
            file_path = args[0] if args else kwargs.get('file_path', '')
            if 'test_image_1' in file_path:
                # Simulate timeout
                import celery.exceptions
                raise celery.exceptions.SoftTimeLimitExceeded()
            time.sleep(0.1)  # Small delay
            return {
                "status": "success",
                "download_url": "https://fal.media/files/model.glb",
                "model_url": "https://fal.media/files/model.glb",
                "model_format": "glb",
                "file_size": 1000000,
                "filename": "model.glb",
                "content_type": "model/gltf-binary"
            }
        
        mock_fal_only.return_value.process_single_image_sync.side_effect = timeout_process
        
        # Execute batch
        result = process_batch.apply_async(
            args=[batch_files, job_id, "tripo3d", None]
        )
        
        batch_result = result.get(timeout=30)
        
        # Verify timeout handling
        assert batch_result["status"] == "partially_completed"
        assert batch_result["failed_files"] == 1
        
        # Check that timeout file is marked correctly
        timeout_results = [r for r in batch_result["results"] if r.get("error") == "Processing timeout"]
        assert len(timeout_results) == 1
    
    def test_finalize_batch_results_aggregation(self):
        """Test the finalize_batch_results function logic."""
        # Create sample results
        results = [
            {
                "file_id": "file1",
                "status": "completed",
                "model_url": "https://example.com/model1.glb",
                "file_size": 1000000
            },
            {
                "file_id": "file2",
                "status": "completed",
                "model_url": "https://example.com/model2.glb",
                "file_size": 2000000
            },
            {
                "file_id": "file3",
                "status": "failed",
                "error": "Processing failed"
            }
        ]
        
        job_id = "test-finalize"
        model_type = "tripo3d"
        
        # Mock job store
        with patch('app.core.job_store.job_store') as mock_store:
            # Call finalize
            final_result = finalize_batch_results(results, job_id, model_type)
            
            # Verify aggregation
            assert final_result["total_files"] == 3
            assert final_result["successful_files"] == 2
            assert final_result["failed_files"] == 1
            assert final_result["status"] == "partially_completed"
            assert final_result["job_id"] == job_id
            assert final_result["model_type"] == model_type
            
            # Verify job store was called
            mock_store.set_job_result.assert_called_once()
    
    def test_batch_progress_tracking(
        self,
        batch_files,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test progress tracking during batch processing."""
        job_id = "test-batch-progress"
        
        # Track progress updates
        progress_updates = []
        
        # Mock progress tracker to capture updates
        original_update = progress_tracker.update_batch_progress
        def capture_progress(*args, **kwargs):
            progress_updates.append(kwargs)
            return original_update(*args, **kwargs)
        
        with patch.object(progress_tracker, 'update_batch_progress', side_effect=capture_progress):
            # Execute batch
            result = process_batch.apply_async(
                args=[batch_files[:3], job_id, "tripo3d", None]
            )
            
            batch_result = result.get(timeout=30)
            
            # Verify progress was tracked
            assert len(progress_updates) > 0
            assert batch_result["status"] == "completed"
    
    def test_batch_empty_file_list(
        self,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test batch processing with empty file list."""
        job_id = "test-batch-empty"
        
        # Execute with empty list
        result = process_batch.apply_async(
            args=[[], job_id, "tripo3d", None]
        )
        
        batch_result = result.get(timeout=10)
        
        # Verify handling of empty batch
        assert batch_result["status"] == "completed"
        assert batch_result["total_files"] == 0
        assert batch_result["successful_files"] == 0
        assert batch_result["failed_files"] == 0
        assert batch_result["results"] == []
    
    def test_concurrent_batches(
        self,
        batch_files,
        mock_fal_only,
        live_celery_worker,
        cleanup_redis
    ):
        """Test multiple concurrent batch jobs."""
        # Launch 3 concurrent batches
        jobs = []
        for i in range(3):
            job_id = f"test-concurrent-{i}"
            result = process_batch.apply_async(
                args=[batch_files[:2], job_id, "tripo3d", None]
            )
            jobs.append((job_id, result))
        
        # Wait for all results
        results = []
        for job_id, result in jobs:
            batch_result = result.get(timeout=30)
            results.append(batch_result)
        
        # Verify all completed successfully
        for i, batch_result in enumerate(results):
            assert batch_result["status"] == "completed"
            assert batch_result["job_id"] == f"test-concurrent-{i}"
            assert batch_result["total_files"] == 2
            assert batch_result["successful_files"] == 2
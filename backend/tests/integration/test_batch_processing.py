"""
Integration tests for batch processing with parallel execution.
"""

import pytest
import os
import time
from unittest.mock import patch, Mock, MagicMock, call
from typing import Dict, Any, Optional

from app.workers.tasks import (
    process_batch,
    process_file_in_batch,
    finalize_batch_results
)
from app.core.progress_tracker import progress_tracker
from tests.mocks.fal_responses import TRIPO_SUCCESS, TRELLIS_SUCCESS


class TestBatchProcessing:
    """Integration tests for parallel batch processing."""
    
    @pytest.fixture
    def mock_task_state(self, monkeypatch):
        """Mock Celery task state updates."""
        state_updates = []
        
        class MockTask:
            def __init__(self):
                self.request = Mock()
                self.request.id = "test-task-123"
                self.request.retries = 0
                
            def update_state(self, state, meta):
                state_updates.append({"state": state, "meta": meta})
        
        mock_task = MockTask()
        monkeypatch.setattr("celery.current_task", mock_task)
        return mock_task, state_updates
    
    @pytest.fixture
    def mock_job_store(self, monkeypatch):
        """Simple mock job store without Redis dependency."""
        class MockJobStore:
            def __init__(self):
                self.data = {}
                
            def set_job_result(self, job_id: str, result: Dict[str, Any]):
                self.data[job_id] = result
                
            def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
                return self.data.get(job_id)
        
        mock_store = MockJobStore()
        monkeypatch.setattr("app.core.job_store.job_store", mock_store)
        return mock_store
    
    @pytest.fixture
    def batch_files(self, tmp_path):
        """Create multiple test files for batch processing."""
        files = []
        for i in range(5):
            file_path = tmp_path / f"test_image_{i}.png"
            file_path.write_bytes(b'\x89PNG\r\n\x1a\n')
            files.append(str(file_path))
        return files
    
    @pytest.fixture
    def mock_chord(self, monkeypatch):
        """Mock Celery chord for testing parallel execution."""
        chord_calls = []
        
        class MockChord:
            def __init__(self, tasks):
                self.tasks = tasks
                self.callback = None
                chord_calls.append(self)
                
            def __call__(self, callback):
                self.callback = callback
                # Create mock result
                result = Mock()
                result.id = "chord-task-123"
                return result
        
        # Mock at the celery module level since it's imported within the function
        import celery
        monkeypatch.setattr(celery, "chord", MockChord)
        return chord_calls
    
    def test_batch_5_files_success(
        self,
        batch_files,
        mock_fal_client_factory,
        mock_chord,
        mock_job_store,
        mock_task_state
    ):
        """Test successful batch processing of 5 files."""
        mock_task, state_updates = mock_task_state
        
        # Configure mock clients
        for model_type in ["tripo3d", "trellis"]:
            mock_client = mock_fal_client_factory(model_type)
            mock_client.process_single_image_sync.return_value = {
                "status": "success",
                "download_url": f"https://fal.media/files/{model_type}_model.glb",
                "model_format": "glb",
                "file_size": 1000000,
                "filename": "model.glb"
            }
        
        # Run batch process
        result = process_batch(
            job_id="batch-job-5",
            file_paths=batch_files,
            model_type="tripo3d",
            params={"texture_enabled": True}
        )
        
        # Verify chord was created with correct number of tasks
        assert len(mock_chord) == 1
        assert len(mock_chord[0].tasks) == 5  # One task per file
        
        # Verify result
        assert result["job_id"] == "batch-job-5"
        assert result["status"] == "processing"
        assert result["total_files"] == 5
        assert "chord_task_id" in result
    
    def test_batch_10_files_parallel(self, tmp_path, mock_chord, mock_task_state):
        """Test larger batch processes files in parallel."""
        mock_task, _ = mock_task_state
        
        # Create 10 files
        files = []
        for i in range(10):
            file_path = tmp_path / f"image_{i}.png"
            file_path.write_bytes(b'\x89PNG\r\n\x1a\n')
            files.append(str(file_path))
        
        # Run batch
        result = process_batch(
            job_id="batch-job-10",
            file_paths=files,
            model_type="trellis"
        )
        
        # Verify all files queued
        assert len(mock_chord[0].tasks) == 10
        assert result["total_files"] == 10
    
    def test_batch_mixed_models(
        self,
        batch_files,
        mock_fal_client_factory,
        mock_job_store
    ):
        """Test batch with different models (single model type per batch)."""
        # Test Tripo batch
        result_tripo = process_batch(
            job_id="batch-tripo",
            file_paths=batch_files[:3],
            model_type="tripo3d",
            params={"texture_enabled": True}
        )
        
        # Test Trellis batch
        result_trellis = process_batch(
            job_id="batch-trellis",
            file_paths=batch_files[3:],
            model_type="trellis",
            params={"texture_size": "2048"}
        )
        
        assert result_tripo["job_id"] == "batch-tripo"
        assert result_trellis["job_id"] == "batch-trellis"
    
    def test_batch_partial_success(self, mock_fal_client_factory, mock_job_store):
        """Test batch where some files succeed and others fail."""
        # Mock individual file processing
        success_result = {
            "file_path": "test1.png",
            "status": "completed",
            "download_url": "https://fal.media/files/success.glb",
            "model_url": "https://fal.media/files/success.glb",
            "model_format": "glb",
            "file_size": 1000000,
            "filename": "success.glb"
        }
        
        failure_result = {
            "file_path": "test2.png",
            "status": "failed",
            "error": "Processing failed",
            "processing_time": 10.0
        }
        
        # Test finalize with mixed results
        results = [success_result, failure_result, success_result]
        
        final_result = finalize_batch_results(
            results=results,
            job_id="batch-partial",
            total_files=3,
            model_type="tripo3d"
        )
        
        assert final_result["status"] == "completed"  # Has successes
        assert final_result["successful_files"] == 2
        assert final_result["failed_files"] == 1
        assert final_result["total_files"] == 3
        
        # Verify job store was updated
        stored = mock_job_store.get_job_result("batch-partial")
        assert stored is not None
        assert len(stored["files"]) == 2  # Only successful files
    
    def test_batch_all_fail(self, mock_job_store):
        """Test batch where all files fail processing."""
        failure_results = [
            {
                "file_path": f"test{i}.png",
                "status": "failed",
                "error": "FAL API error",
                "processing_time": 5.0
            }
            for i in range(3)
        ]
        
        final_result = finalize_batch_results(
            results=failure_results,
            job_id="batch-all-fail",
            total_files=3,
            model_type="tripo3d"
        )
        
        assert final_result["status"] == "failed"  # No successes
        assert final_result["successful_files"] == 0
        assert final_result["failed_files"] == 3
        
        # Verify job store not updated for all-fail case
        stored = mock_job_store.get_job_result("batch-all-fail")
        assert stored is None  # Should not store results when all fail
    
    def test_batch_with_timeout(self, mock_job_store):
        """Test batch processing with some files timing out."""
        results = [
            {
                "file_path": "test1.png",
                "status": "completed",
                "download_url": "https://fal.media/files/model1.glb",
                "model_url": "https://fal.media/files/model1.glb",
                "file_size": 1000000,
                "filename": "model1.glb"
            },
            {
                "file_path": "test2.png",
                "status": "timeout",
                "error": "Processing timeout",
                "processing_time": 300.0
            }
        ]
        
        final_result = finalize_batch_results(
            results=results,
            job_id="batch-timeout",
            total_files=2,
            model_type="trellis"
        )
        
        assert final_result["status"] == "partially_completed"
        assert final_result["timeout_files"] == 1
        assert final_result["successful_files"] == 1
        
        # Verify job store has only successful file
        stored = mock_job_store.get_job_result("batch-timeout")
        assert stored is not None
        assert len(stored["files"]) == 1
    
    def test_batch_empty_file_list(self, mock_task_state, mock_chord):
        """Test batch processing with empty file list."""
        mock_task, _ = mock_task_state
        
        # Should handle gracefully
        result = process_batch(
            job_id="batch-empty",
            file_paths=[],
            model_type="tripo3d"
        )
        
        assert result["total_files"] == 0
        # Verify chord was created even with empty list
        assert len(mock_chord) == 1
        assert len(mock_chord[0].tasks) == 0  # No tasks for empty file list
    
    def test_batch_single_file(self, temp_image_file, mock_chord, mock_task_state):
        """Test batch processing with just one file."""
        mock_task, _ = mock_task_state
        
        result = process_batch(
            job_id="batch-single",
            file_paths=[temp_image_file],
            model_type="tripo3d"
        )
        
        # Should still use chord for consistency
        assert len(mock_chord[0].tasks) == 1
        assert result["total_files"] == 1
    
    def test_batch_duplicate_files(self, temp_image_file, mock_chord, mock_task_state):
        """Test batch with same file multiple times."""
        mock_task, _ = mock_task_state
        
        # Same file 3 times
        files = [temp_image_file] * 3
        
        result = process_batch(
            job_id="batch-duplicate",
            file_paths=files,
            model_type="trellis"
        )
        
        # Should process each instance
        assert len(mock_chord[0].tasks) == 3
    
    def test_batch_invalid_file_paths(self, mock_chord, mock_task_state):
        """Test batch with non-existent files."""
        mock_task, _ = mock_task_state
        
        files = [
            "/nonexistent/file1.png",
            "/nonexistent/file2.png"
        ]
        
        # Should still create tasks (they'll fail individually)
        result = process_batch(
            job_id="batch-invalid",
            file_paths=files,
            model_type="tripo3d"
        )
        
        assert result["total_files"] == 2
    
    def test_concurrent_progress_updates(self, mock_job_store, mock_fal_client_factory, tmp_path):
        """Test multiple workers updating same job progress."""
        job_id = "concurrent-job"
        
        # Create test files
        test_files = []
        for i in range(3):
            file_path = tmp_path / f"test{i}.png"
            file_path.write_bytes(b'\x89PNG\r\n\x1a\n')
            test_files.append(str(file_path))
        
        # Configure mock client
        mock_client = mock_fal_client_factory("tripo3d")
        mock_client.process_single_image_sync.return_value = {
            "status": "success",
            "download_url": "https://fal.media/files/model.glb",
            "model_format": "glb",
            "file_size": 1000000,
            "filename": "model.glb"
        }
        
        # Simulate concurrent updates
        with patch.object(progress_tracker, 'update_file_progress') as mock_update:
            # Process multiple files "concurrently"
            for i, file_path in enumerate(test_files):
                process_file_in_batch(
                    file_path=file_path,
                    job_id=job_id,
                    model_type="tripo3d",
                    file_index=i,
                    total_files=3
                )
            
            # Verify progress updates were attempted
            assert mock_update.call_count >= 3
    
    def test_job_store_race_condition(self, mock_job_store):
        """Test concurrent result writes to job store."""
        results = [
            {
                "file_path": f"test{i}.png",
                "status": "completed",
                "download_url": f"https://fal.media/files/model{i}.glb",
                "file_size": 1000000 * (i + 1)
            }
            for i in range(5)
        ]
        
        # Finalize should handle concurrent writes safely
        final_result = finalize_batch_results(
            results=results,
            job_id="race-condition-job",
            total_files=5,
            model_type="tripo3d"
        )
        
        # Verify job store has complete data
        stored = mock_job_store.get_job_result("race-condition-job")
        assert stored is not None
        assert len(stored["files"]) == 5
        assert stored["successful_files"] == 5
    
    def test_parallel_file_processing(self, temp_image_file, mock_fal_client_factory, monkeypatch):
        """Test individual file processing in parallel context."""
        # Configure custom return value for this test
        custom_result = {
            "status": "success",
            "download_url": "https://fal.media/files/parallel.glb",
            "model_url": "https://fal.media/files/parallel.glb",
            "model_format": "glb",
            "file_size": 2000000,
            "filename": "parallel.glb",
            "content_type": "model/gltf-binary",
            "output": None,
            "task_id": "parallel-task-123"
        }
        
        # Create a persistent mock client that returns our custom result
        from unittest.mock import Mock
        from app.workers.fal_client import TrellisClient
        
        mock_client = Mock(spec=TrellisClient)
        mock_client.model_endpoint = "fal-ai/trellis"
        mock_client.process_single_image_sync.return_value = custom_result
        
        # Override the factory to always return our configured mock
        def custom_factory(model_type):
            if model_type == "trellis":
                return mock_client
            else:
                return mock_fal_client_factory(model_type)
        
        monkeypatch.setattr("app.workers.fal_client.get_model_client", custom_factory)
        monkeypatch.setattr("app.workers.tasks.get_model_client", custom_factory)
        
        # Process single file as part of batch
        result = process_file_in_batch(
            file_path=temp_image_file,
            job_id="parallel-job",
            model_type="trellis",
            params={"texture_size": "2048"},
            file_index=2,
            total_files=5
        )
        
        assert result["status"] == "completed"
        assert result["file_path"] == temp_image_file
        assert result["download_url"] == "https://fal.media/files/parallel.glb"
        assert "processing_time" in result  # Actual processing time from task execution
    
    def test_chord_callback_execution(self, mock_job_store):
        """Test finalize callback runs after all files complete."""
        # Test data from parallel processing
        parallel_results = [
            {
                "file_path": f"file{i}.png",
                "status": "completed",
                "download_url": f"https://fal.media/files/model{i}.glb",
                "model_url": f"https://fal.media/files/model{i}.glb",
                "file_size": 1000000,
                "filename": f"model{i}.glb"
            }
            for i in range(3)
        ]
        
        # Run finalize callback
        summary = finalize_batch_results(
            results=parallel_results,
            job_id="chord-test",
            total_files=3,
            model_type="tripo3d"
        )
        
        # Verify aggregation
        assert summary["job_id"] == "chord-test"
        assert summary["total_files"] == 3
        assert summary["successful_files"] == 3
        assert summary["status"] == "completed"
        assert "Batch processing completed" in summary["message"]
        
        # Verify job store updated
        stored = mock_job_store.get_job_result("chord-test")
        assert stored["model_type"] == "tripo3d"
        assert len(stored["files"]) == 3
    
    def test_batch_with_custom_params(self, batch_files, mock_chord, mock_task_state):
        """Test batch processing passes custom params to each file."""
        mock_task, _ = mock_task_state
        
        custom_params = {
            "ss_guidance_strength": 9.0,
            "texture_size": "2048",
            "mesh_simplify": 0.92
        }
        
        result = process_batch(
            job_id="batch-params",
            file_paths=batch_files[:2],
            model_type="trellis",
            params=custom_params
        )
        
        # Verify params passed to subtasks
        subtasks = mock_chord[0].tasks
        for task in subtasks:
            # Check task signature includes params
            # The signature is process_file_in_batch.s(file_path, job_id, model_type, params, file_index, total_files)
            assert len(task.args) == 6
            assert task.args[3] == custom_params  # 4th argument is params
    
    def test_batch_progress_state_updates(self, batch_files, mock_task_state, mock_chord):
        """Test batch updates overall progress during processing."""
        mock_task, state_updates = mock_task_state
        
        process_batch(
            job_id="batch-progress",
            file_paths=batch_files[:3],
            model_type="tripo3d"
        )
        
        # Check progress updates
        progress_updates = [u for u in state_updates if u["state"] == "PROGRESS"]
        assert len(progress_updates) >= 2
        
        # Initial update
        assert progress_updates[0]["meta"]["status"] == "Starting parallel batch processing for 3 files..."
        
        # Processing update
        assert any("Processing 3 files in parallel" in u["meta"]["status"] for u in progress_updates)
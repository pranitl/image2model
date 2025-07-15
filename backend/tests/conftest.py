"""
Pytest configuration and shared fixtures for testing.
"""

import os
import sys
import pytest
import tempfile
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, Optional

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.mocks.fal_responses import (
    TRIPO_SUCCESS,
    TRELLIS_SUCCESS,
    MALFORMED_RESPONSES,
    ERROR_RESPONSES,
    PROGRESS_UPDATES
)


@pytest.fixture
def temp_image_file():
    """Create a temporary image file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        # Write minimal PNG header
        f.write(b'\x89PNG\r\n\x1a\n')
        f.flush()
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.unlink(f.name)


@pytest.fixture
def mock_fal_upload(monkeypatch):
    """Mock FAL file upload to return a test URL."""
    def mock_upload(file_path):
        filename = os.path.basename(file_path)
        return f"https://fal.ai/uploads/test_{filename}"
    
    import fal_client
    monkeypatch.setattr(fal_client, "upload_file", mock_upload)
    return mock_upload


@pytest.fixture
def mock_fal_subscribe(monkeypatch):
    """Mock FAL subscribe function with configurable responses."""
    class MockSubscribe:
        def __init__(self):
            self.call_count = 0
            self.response_type = "success"
            self.model_type = "tripo"
            self.should_raise = False
            self.exception = None
            self.progress_callbacks = []
            
        def __call__(self, endpoint, arguments, with_logs=True, on_queue_update=None):
            self.call_count += 1
            
            # Store progress callback
            if on_queue_update:
                self.progress_callbacks.append(on_queue_update)
                
                # Simulate progress updates
                import fal_client
                for update_key in ["upload", "processing_25", "processing_50", "processing_75"]:
                    update = Mock(spec=fal_client.InProgress)
                    update.logs = PROGRESS_UPDATES[update_key]["logs"]
                    on_queue_update(update)
            
            if self.should_raise:
                raise self.exception or Exception("Mock FAL error")
            
            # Return appropriate response based on configuration
            if self.response_type == "success":
                if "tripo" in endpoint:
                    return TRIPO_SUCCESS
                elif "trellis" in endpoint:
                    return TRELLIS_SUCCESS
            elif self.response_type in MALFORMED_RESPONSES:
                return MALFORMED_RESPONSES[self.response_type]
            elif self.response_type in ERROR_RESPONSES:
                error_data = ERROR_RESPONSES[self.response_type]
                raise Exception(error_data["message"])
            
            return {"error": "Unknown response type"}
    
    mock_subscribe = MockSubscribe()
    import fal_client
    monkeypatch.setattr(fal_client, "subscribe", mock_subscribe)
    return mock_subscribe


@pytest.fixture
def mock_fal_client_factory(monkeypatch):
    """Mock the get_model_client factory function."""
    from app.workers.fal_client import TripoClient, TrellisClient
    
    def mock_factory(model_type: str):
        if model_type == "tripo3d":
            client = Mock(spec=TripoClient)
            client.model_endpoint = "tripo3d/tripo/v2.5/image-to-3d"
            client.MODEL_INFO = TripoClient.MODEL_INFO
        elif model_type == "trellis":
            client = Mock(spec=TrellisClient)
            client.model_endpoint = "fal-ai/trellis"
            client.MODEL_INFO = TrellisClient.MODEL_INFO
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Mock common methods
        client.upload_file_to_fal = Mock(return_value="https://fal.ai/uploads/test.png")
        client.submit_job = Mock(return_value=TRIPO_SUCCESS if model_type == "tripo3d" else TRELLIS_SUCCESS)
        client.process_single_image_sync = Mock(return_value={
            "status": "success",
            "download_url": "https://fal.media/files/model.glb",
            "model_format": "glb"
        })
        
        return client
    
    monkeypatch.setattr("app.workers.fal_client.get_model_client", mock_factory)
    monkeypatch.setattr("app.workers.tasks.get_model_client", mock_factory)
    return mock_factory


@pytest.fixture
def mock_celery_task(monkeypatch):
    """Mock Celery task execution."""
    class MockTask:
        def __init__(self):
            self.task_id = "test-task-123"
            self.state = "PENDING"
            self.info = {}
            
        def update_state(self, state, meta):
            self.state = state
            self.info = meta
            
    class MockTaskResult:
        def __init__(self):
            self.id = "test-task-123"
            
        def delay(self, *args, **kwargs):
            return self
            
    mock_task = MockTask()
    mock_result = MockTaskResult()
    
    # Mock current_task
    monkeypatch.setattr("celery.current_task", mock_task)
    
    # Mock task delay
    monkeypatch.setattr("app.workers.tasks.generate_3d_model_task.delay", 
                       lambda *args, **kwargs: mock_result)
    
    return mock_task


@pytest.fixture
def fake_redis():
    """Create a fake Redis instance for testing."""
    import fakeredis
    return fakeredis.FakeRedis()


@pytest.fixture
def mock_job_store(monkeypatch, fake_redis):
    """Mock the job store with fake Redis."""
    class MockJobStore:
        def __init__(self):
            self.redis = fake_redis
            self.data = {}
            
        def set_job_result(self, job_id: str, result: Dict[str, Any]):
            self.data[job_id] = result
            
        def get_job_result(self, job_id: str) -> Optional[Dict[str, Any]]:
            return self.data.get(job_id)
    
    mock_store = MockJobStore()
    monkeypatch.setattr("app.core.job_store.job_store", mock_store)
    return mock_store


@pytest.fixture
def test_client():
    """Create a test client for API testing."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    return TestClient(app)


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock application settings."""
    class MockSettings:
        FAL_API_KEY = "test-api-key"
        UPLOAD_DIR = "/tmp/uploads"
        OUTPUT_DIR = "/tmp/outputs"
        RESULTS_DIR = "/tmp/results"
        CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
        ENVIRONMENT = "test"
        
    mock_settings = MockSettings()
    monkeypatch.setattr("app.core.config.settings", mock_settings)
    return mock_settings


@pytest.fixture
def sample_model_params():
    """Sample parameters for different models."""
    return {
        "tripo3d": {
            "texture_enabled": True,
            "face_limit": 10000
        },
        "trellis": {
            "ss_guidance_strength": 7.5,
            "ss_sampling_steps": 12,
            "slat_guidance_strength": 3.0,
            "slat_sampling_steps": 12,
            "mesh_simplify": 0.95,
            "texture_size": "1024"
        }
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("FAL_KEY", "test-api-key")
    monkeypatch.setenv("ENVIRONMENT", "test")
    

# Utility functions for testing
def create_mock_progress_update(message: str, progress: int):
    """Create a mock progress update object."""
    import fal_client
    update = Mock(spec=fal_client.InProgress)
    update.logs = [{
        "message": message,
        "timestamp": "2024-01-10T10:00:00.000Z",
        "level": "info"
    }]
    return update
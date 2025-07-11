"""
Pytest configuration and fixtures for all tests.
"""

import pytest
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "load: mark test as a load/performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )


@pytest.fixture(scope="session")
def api_base_url():
    """Get API base URL from environment or use default."""
    return os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


@pytest.fixture(scope="session")
def api_key():
    """Get API key from environment or use default test key."""
    return os.getenv("API_KEY", "test-api-key")


@pytest.fixture(scope="session")
def admin_api_key():
    """Get admin API key from environment or use default test key."""
    return os.getenv("ADMIN_API_KEY", "admin-test-key")


@pytest.fixture
def skip_if_no_api():
    """Skip test if API is not available."""
    import requests
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        if response.status_code != 200:
            pytest.skip("API is not healthy")
    except:
        pytest.skip("API is not available")


@pytest.fixture
def skip_if_no_celery():
    """Skip test if Celery is not available."""
    try:
        from app.core.celery_app import celery_app
        # Try to inspect active queues
        inspector = celery_app.control.inspect()
        if not inspector.active_queues():
            pytest.skip("Celery workers not available")
    except:
        pytest.skip("Celery is not configured")


@pytest.fixture
def skip_if_no_redis():
    """Skip test if Redis is not available."""
    import redis
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        r = redis.from_url(redis_url)
        r.ping()
    except:
        pytest.skip("Redis is not available")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "load" in str(item.fspath):
            item.add_marker(pytest.mark.load)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark SSE tests
        if "sse" in item.name.lower() or "stream" in item.name.lower():
            item.add_marker(pytest.mark.integration)
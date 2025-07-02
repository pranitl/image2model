"""
Pytest configuration and shared fixtures for Image2Model tests.
"""

import os
import sys
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Configuration
BACKEND_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("TEST_MAX_RETRIES", "3"))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Test configuration settings."""
    return {
        "backend_url": BACKEND_URL,
        "frontend_url": FRONTEND_URL,
        "timeout": TEST_TIMEOUT,
        "max_retries": MAX_RETRIES,
        "test_files_dir": Path(__file__).parent / "fixtures" / "files",
        "temp_dir": Path(tempfile.gettempdir()) / "image2model_tests"
    }

@pytest.fixture(scope="session")
def http_session() -> Generator[requests.Session, None, None]:
    """Create HTTP session with retry strategy."""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=MAX_RETRIES,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        backoff_factor=0.3
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    yield session
    session.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(test_config):
    """Set up test environment before running tests."""
    # Create temp directory for test files
    test_config["temp_dir"].mkdir(parents=True, exist_ok=True)
    
    # Create test fixtures directory
    fixtures_dir = test_config["test_files_dir"]
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Cleanup temp directory after tests
    if test_config["temp_dir"].exists():
        shutil.rmtree(test_config["temp_dir"])

@pytest.fixture
def temp_dir(test_config) -> Path:
    """Get temporary directory for test files."""
    return test_config["temp_dir"]

@pytest.fixture
def sample_image_file(temp_dir) -> Path:
    """Create a sample image file for testing."""
    from PIL import Image
    import io
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_path = temp_dir / "test_image.jpg"
    img.save(img_path, "JPEG")
    
    return img_path

@pytest.fixture
def invalid_file(temp_dir) -> Path:
    """Create an invalid file for testing."""
    file_path = temp_dir / "invalid_file.txt"
    with open(file_path, 'w') as f:
        f.write("This is not an image file")
    
    return file_path

@pytest.fixture
def large_image_file(temp_dir) -> Path:
    """Create a large image file for testing size limits."""
    from PIL import Image
    
    # Create a large test image (approximately 15MB)
    img = Image.new('RGB', (3000, 3000), color='blue')
    img_path = temp_dir / "large_test_image.jpg"
    img.save(img_path, "JPEG", quality=95)
    
    return img_path

@pytest.fixture
def multiple_image_files(temp_dir) -> list[Path]:
    """Create multiple image files for batch testing."""
    from PIL import Image
    
    files = []
    colors = ['red', 'green', 'blue', 'yellow', 'purple']
    
    for i, color in enumerate(colors):
        img = Image.new('RGB', (150, 150), color=color)
        img_path = temp_dir / f"test_image_{i+1}_{color}.jpg"
        img.save(img_path, "JPEG")
        files.append(img_path)
    
    return files

@pytest.fixture
def service_health_checker(http_session, test_config):
    """Check if required services are running."""
    def check_service(url: str, timeout: int = 5) -> bool:
        try:
            response = http_session.get(f"{url}/health", timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    return check_service

@pytest.fixture(scope="session")
def backend_available(http_session, test_config) -> bool:
    """Check if backend service is available."""
    try:
        response = http_session.get(f"{test_config['backend_url']}/health", timeout=10)
        return response.status_code == 200
    except:
        return False

@pytest.fixture(scope="session")
def services_ready(backend_available) -> bool:
    """Check if all required services are ready."""
    if not backend_available:
        pytest.skip("Backend service is not available")
    return True

# Markers for test categories
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "integration: Integration tests requiring services")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "load: Load testing")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "docker: Tests requiring Docker")
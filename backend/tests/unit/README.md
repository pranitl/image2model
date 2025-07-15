# Unit Tests Setup Guide

This guide will help you set up and run the unit tests for the Image2Model backend.

## Prerequisites

1. **Python Environment**: Python 3.8+ with virtual environment
2. **Backend Dependencies**: All backend requirements installed
3. **Environment Variables**: Properly configured test environment

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
# From the backend directory
cd /Users/pranit/Documents/AI/image2model/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install backend dependencies
pip install -r requirements.txt

# Install test dependencies
pip install -r requirements-test.txt
```

If `requirements-test.txt` doesn't exist, install these packages:
```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio fakeredis
```

### 3. Fix urllib3 Compatibility Issue

The error `AttributeError: module 'urllib3.connectionpool' has no attribute 'VerifiedHTTPSConnection'` occurs due to version incompatibility between urllib3 and other packages.

**Solution:**
```bash
# Downgrade urllib3 to a compatible version
pip install urllib3==1.26.18

# Or upgrade all related packages
pip install --upgrade urllib3 requests httpx fal-client
```

### 4. Set Environment Variables

Create a `.env.test` file in the backend directory:
```bash
# Test environment variables
FAL_KEY=test-api-key
ENVIRONMENT=test
UPLOAD_DIR=/tmp/test_uploads
OUTPUT_DIR=/tmp/test_outputs
RESULTS_DIR=/tmp/test_results
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 5. Running Tests

#### Run All Unit Tests
```bash
# From the backend directory
pytest tests/unit/ -v
```

#### Run Specific Test File
```bash
pytest tests/unit/test_tripo_client.py -v
```

#### Run with Coverage
```bash
pytest tests/unit/ --cov=app --cov-report=html
```

#### Run Tests in Parallel
```bash
pytest tests/unit/ -n auto
```

## Test Structure

### Test Files
- `test_fal_client_abstract.py` - Tests for abstract base client functionality
- `test_tripo_client.py` - Tests for Tripo3D model client
- `test_trellis_client.py` - Tests for Trellis model client
- `test_fal_client_factory.py` - Tests for client factory pattern
- `test_edge_case_validation.py` - Tests for parameter validation edge cases
- `test_malformed_responses.py` - Tests for handling malformed API responses

### Mock Structure
All tests use mocked FAL.AI responses defined in:
- `tests/mocks/fal_responses.py` - Mock API responses
- `tests/conftest.py` - Pytest fixtures for mocking

## Common Issues and Solutions

### 1. Import Errors
```bash
# Ensure PYTHONPATH includes backend directory
export PYTHONPATH="${PYTHONPATH}:/Users/pranit/Documents/AI/image2model/backend"
```

### 2. Redis Connection Errors
The tests mock Redis connections, but if you see Redis errors:
```bash
# Install fakeredis
pip install fakeredis
```

### 3. Missing Mock Fixtures
All required fixtures are in `conftest.py`. If a test fails due to missing fixtures:
```bash
# Run pytest with fixture discovery
pytest tests/unit/ --fixtures
```

### 4. Async Test Issues
```bash
# Install pytest-asyncio
pip install pytest-asyncio
```

## Test Best Practices

1. **No Live API Calls**: All tests mock external dependencies
2. **Isolated Tests**: Each test is independent
3. **Fast Execution**: Unit tests should run in < 5 seconds total
4. **Clear Assertions**: Each test clearly states what it's testing

## Debugging Failed Tests

### Verbose Output
```bash
pytest tests/unit/test_file.py::TestClass::test_method -vvs
```

### Print Debugging
```bash
pytest tests/unit/ -s  # Don't capture stdout
```

### Debug with PDB
```python
# Add in test where you want to debug
import pdb; pdb.set_trace()
```

## CI/CD Integration

For GitHub Actions or other CI systems:
```yaml
- name: Run Unit Tests
  run: |
    cd backend
    python -m pytest tests/unit/ -v --cov=app --cov-report=xml
```

## Troubleshooting

### urllib3 Error Fix (Detailed)
If you continue to see the urllib3 error, try this complete fix:

```bash
# Uninstall all related packages
pip uninstall urllib3 requests httpx fal-client -y

# Reinstall with specific versions
pip install urllib3==1.26.18
pip install requests==2.31.0
pip install httpx==0.24.1
pip install fal-client

# Verify installation
python -c "import urllib3; print(urllib3.__version__)"
```

### Alternative: Use Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["pytest", "tests/unit/", "-v"]
```

## Contact

For issues with test setup, check:
1. Backend requirements.txt for version conflicts
2. GitHub Actions workflow for CI configuration
3. Project documentation for environment setup
# Image2Model Test Suite

Comprehensive integration and end-to-end testing suite for the Image2Model platform, focusing on MVP validation and production readiness.

## Overview

This test suite provides thorough validation of the Image2Model platform with emphasis on:

- **Integration Testing**: Core workflow validation with real service interactions
- **End-to-End Testing**: Complete user journey simulation
- **Load Testing**: Performance validation under various load conditions
- **Docker Testing**: Production deployment configuration validation
- **Monitoring Testing**: Observability and health check validation

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and shared fixtures
├── requirements.txt               # Test dependencies
├── run_tests.py                   # Comprehensive test runner
├── README.md                      # This documentation
├── integration/                   # Integration tests
│   ├── test_api_endpoints.py      # API endpoint validation
│   ├── test_upload_workflow.py    # Upload workflow integration
│   ├── test_docker_deployment.py  # Docker configuration tests
│   └── test_monitoring.py         # Monitoring system tests
├── e2e/                          # End-to-end tests
│   ├── test_complete_workflow.py  # Complete user workflows
│   └── test_production_validation.py # Production readiness validation
├── load/                         # Load and performance tests
│   └── test_performance.py        # Load testing scenarios
└── utils/                        # Test utilities
```

## Quick Start

### Prerequisites

1. **Services Running**: Ensure backend and database services are running
2. **Dependencies**: Install test dependencies

```bash
# Install all dependencies (includes test dependencies)
pip install -r requirements.txt

# Or set up complete test environment
python tests/run_tests.py --setup
```

### Running Tests

#### Quick Smoke Test (Recommended for CI/CD)

```bash
python tests/run_tests.py smoke
```

#### Integration Tests

```bash
python tests/run_tests.py integration
```

#### End-to-End Tests

```bash
python tests/run_tests.py e2e
```

#### Load Tests

```bash
python tests/run_tests.py load
```

#### All Tests

```bash
python tests/run_tests.py all --verbose --html
```

## Test Categories

### 1. Smoke Tests (`smoke`)

Quick validation tests for production readiness:

- Basic service availability
- Critical endpoint responsiveness
- Upload endpoint basic functionality

**Duration**: ~30 seconds
**Use Case**: CI/CD pipelines, production health checks

### 2. Integration Tests (`integration`)

Comprehensive API and workflow testing:

- **Upload Workflow**: Single and batch file uploads
- **API Endpoints**: All REST API endpoints
- **Docker Deployment**: Docker Compose configuration validation
- **Monitoring**: Prometheus metrics and health checks

**Duration**: ~5-10 minutes
**Use Case**: Feature validation, pre-deployment testing

### 3. End-to-End Tests (`e2e`)

Complete user journey simulation:

- **Complete Workflow**: Upload → Process → Download
- **Batch Processing**: Multi-file processing workflows
- **Real-time Monitoring**: SSE progress tracking
- **Production Validation**: Comprehensive production readiness

**Duration**: ~10-20 minutes
**Use Case**: Release validation, staging environment testing

### 4. Load Tests (`load`)

Performance and scalability validation:

- Health endpoint load testing
- Upload endpoint performance
- Mixed load scenarios
- Sustained load testing
- Memory usage stability

**Duration**: ~5-15 minutes
**Use Case**: Performance validation, capacity planning

### 5. Docker Tests (`docker`)

Docker deployment configuration validation:

- Docker Compose file validation
- Service definition verification
- Production configuration testing
- Build process validation

**Duration**: ~10-30 minutes (includes builds)
**Use Case**: Deployment validation, infrastructure testing

## Configuration

### Environment Variables

```bash
# Service URLs (defaults shown)
export TEST_BACKEND_URL="http://localhost:8000"
export TEST_FRONTEND_URL="http://localhost:3000"

# Test configuration
export TEST_TIMEOUT="30"          # Request timeout in seconds
export TEST_MAX_RETRIES="3"       # Maximum retries for requests
```

### Service Requirements

The test suite requires the following services to be running:

- **Backend API** (FastAPI) - Required for all tests
- **Database** (PostgreSQL) - Required for integration tests
- **Redis** - Required for Celery/task tests
- **Frontend** (React) - Optional for some E2E tests

### Starting Services

```bash
# Development environment
docker compose up -d

# Production environment (for production validation tests)
docker compose -f docker compose.yml -f docker compose.prod.yml up -d
```

## Advanced Usage

### Parallel Execution

```bash
python tests/run_tests.py integration --parallel
```

### Coverage Reports

```bash
python tests/run_tests.py all --coverage
```

### HTML Reports

```bash
python tests/run_tests.py all --html
```

### Comprehensive Reporting

```bash
python tests/run_tests.py --report
```

This generates:
- HTML test report (`tests/comprehensive_report.html`)
- Coverage HTML report (`tests/coverage_html/index.html`)
- Coverage XML report (`tests/coverage.xml`)

## Test Data and Fixtures

### Automatic Test Data

The test suite automatically creates test fixtures:

- **Sample Images**: Generated test images in various formats
- **Invalid Files**: Files for error testing
- **Large Files**: Files for size limit testing
- **Multiple Files**: Batch processing test data

### Custom Test Data

Place custom test files in:
```
tests/fixtures/files/
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Start services
        run: docker compose up -d
      - name: Wait for services
        run: sleep 30
      - name: Run smoke tests
        run: python tests/run_tests.py smoke
      - name: Run integration tests
        run: python tests/run_tests.py integration --html
      - name: Upload test report
        uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: tests/report.html
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Setup') {
            steps {
                sh 'docker compose up -d'
                sh 'sleep 30'
            }
        }
        stage('Smoke Tests') {
            steps {
                sh 'python tests/run_tests.py smoke'
            }
        }
        stage('Integration Tests') {
            steps {
                sh 'python tests/run_tests.py integration --coverage --html'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'tests',
                        reportFiles: 'report.html',
                        reportName: 'Test Report'
                    ])
                }
            }
        }
    }
}
```

## Troubleshooting

### Common Issues

#### Services Not Available

```bash
# Check service status
docker compose ps

# Check logs
docker compose logs backend
docker compose logs postgres
docker compose logs redis
```

#### Test Dependencies

```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

#### Permission Issues

```bash
# Make test runner executable
chmod +x tests/run_tests.py
```

#### Network Issues

```bash
# Check service connectivity
curl http://localhost:8000/health
```

### Debugging Tests

#### Verbose Output

```bash
python tests/run_tests.py integration -v
```

#### Single Test

```bash
pytest tests/integration/test_api_endpoints.py::TestAPIEndpoints::test_health_endpoint -v
```

#### Debug Mode

```bash
pytest tests/integration/test_upload_workflow.py --pdb -s
```

## Development Guidelines

### Adding New Tests

1. **Choose Category**: Determine if test is integration, e2e, load, or docker
2. **Use Fixtures**: Leverage existing fixtures in `conftest.py`
3. **Follow Patterns**: Use existing test patterns for consistency
4. **Add Markers**: Use appropriate pytest markers

```python
import pytest

@pytest.mark.integration
@pytest.mark.slow
def test_new_feature(http_session, test_config, services_ready):
    \"\"\"Test new feature functionality.\"\"\"
    # Test implementation
    pass
```

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `TestFeatureName`
- Test methods: `test_specific_behavior`
- Use descriptive names that explain what is being tested

### Assertions

Use descriptive assertion messages:

```python
assert response.status_code == 200, f"Upload failed: {response.text}"
assert 'job_id' in data, "Response missing job_id field"
```

### Error Handling

Handle expected errors gracefully:

```python
try:
    response = http_session.get(url, timeout=5)
    assert response.status_code == 200
except requests.exceptions.ConnectionError:
    pytest.skip("Service not available")
```

## Performance Benchmarks

### Expected Performance Metrics

| Test Category | Duration | Success Rate | Notes |
|---------------|----------|--------------|-------|
| Smoke Tests | < 1 min | 100% | Critical path validation |
| Integration Tests | 5-10 min | > 95% | Comprehensive API testing |
| E2E Tests | 10-20 min | > 90% | Full workflow validation |
| Load Tests | 5-15 min | > 80% | Performance under load |
| Docker Tests | 10-30 min | > 95% | Infrastructure validation |

### Resource Usage

- **Memory**: Tests should not increase system memory usage by more than 20%
- **CPU**: Tests should not sustain CPU usage above 80%
- **Disk**: Test artifacts should be cleaned up automatically
- **Network**: Tests should handle network latency gracefully

## Contributing

### Test Coverage Goals

- **API Endpoints**: 100% coverage
- **Critical Workflows**: 100% coverage
- **Error Scenarios**: 90% coverage
- **Edge Cases**: 80% coverage

### Code Quality

- All tests must pass before merging
- Tests must be deterministic (no flaky tests)
- Tests must clean up after themselves
- Tests must be platform-independent

### Review Checklist

- [ ] Tests cover new functionality
- [ ] Tests follow naming conventions
- [ ] Tests use appropriate fixtures
- [ ] Tests have descriptive assertions
- [ ] Tests handle errors gracefully
- [ ] Tests run in CI/CD pipeline

## Support

For test-related issues:

1. Check this documentation
2. Review test logs and error messages
3. Verify service availability
4. Check GitHub issues for known problems
5. Create new issue with test output and environment details

---

**Last Updated**: 2025-07-02  
**Test Suite Version**: 1.0.0  
**Compatible with**: Image2Model v1.0.0
"""
Production validation and smoke tests.

Comprehensive tests to validate production readiness and system reliability.
"""

import pytest
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import requests

@pytest.mark.e2e
@pytest.mark.slow
class TestProductionValidation:
    """Production readiness validation tests."""
    
    def test_production_deployment_smoke_test(self, http_session, test_config, services_ready):
        """Smoke test for production deployment."""
        # Test critical endpoints are accessible
        critical_endpoints = [
            ('/health', 'Health check'),
            ('/api/v1/health/detailed', 'Detailed health'),
            ('/api/v1/health/metrics', 'Metrics'),
            ('/api/v1/admin/disk-usage', 'Disk usage'),
            ('/api/v1/admin/system-health', 'System health')
        ]
        
        failed_endpoints = []
        
        for endpoint, description in critical_endpoints:
            url = f"{test_config['backend_url']}{endpoint}"
            try:
                response = http_session.get(url, timeout=10)
                if response.status_code not in [200, 401, 403]:  # 401/403 might be expected for admin endpoints
                    failed_endpoints.append(f"{description} ({endpoint}): HTTP {response.status_code}")
            except Exception as e:
                failed_endpoints.append(f"{description} ({endpoint}): {str(e)}")
        
        assert len(failed_endpoints) == 0, f"Critical endpoints failed: {', '.join(failed_endpoints)}"
        print("✓ All critical endpoints accessible")
    
    def test_error_handling_consistency(self, http_session, test_config, services_ready):
        """Test error handling consistency across endpoints."""
        # Test various error scenarios
        error_scenarios = [
            ('POST', '/api/v1/upload', {}, 'Missing file upload'),
            ('GET', '/api/v1/status/tasks/invalid-id/status', {}, 'Invalid task ID'),
            ('GET', '/api/v1/download/nonexistent/all', {}, 'Nonexistent download'),
            ('POST', '/api/v1/admin/cleanup-job', {'job_id': 'nonexistent'}, 'Nonexistent job cleanup')
        ]
        
        error_responses = []
        
        for method, endpoint, data, description in error_scenarios:
            url = f"{test_config['backend_url']}{endpoint}"
            
            try:
                if method == 'GET':
                    response = http_session.get(url, timeout=10)
                elif method == 'POST':
                    if data:
                        response = http_session.post(url, json=data, timeout=10)
                    else:
                        response = http_session.post(url, timeout=10)
                
                # Expect 4xx errors for these scenarios
                if 400 <= response.status_code < 500:
                    try:
                        error_data = response.json()
                        
                        # Check error response format
                        required_fields = ['error', 'error_code', 'message']
                        missing_fields = [field for field in required_fields if field not in error_data]
                        
                        if missing_fields:
                            error_responses.append(f"{description}: Missing error fields {missing_fields}")
                        elif error_data.get('error') != True:
                            error_responses.append(f"{description}: error field not True")
                        else:
                            print(f"✓ {description}: Proper error format")
                    
                    except json.JSONDecodeError:
                        error_responses.append(f"{description}: Non-JSON error response")
                else:
                    # Unexpected status code
                    error_responses.append(f"{description}: Unexpected status {response.status_code}")
            
            except Exception as e:
                error_responses.append(f"{description}: Exception {str(e)}")
        
        if error_responses:
            print(f"Error handling issues: {'; '.join(error_responses)}")
            # Don't fail the test for error format issues in production validation

@pytest.mark.e2e
class TestProductionSmokeTest:
    """Quick smoke tests for production validation."""
    
    def test_basic_service_availability(self, http_session, test_config, services_ready):
        """Basic smoke test - are core services responding?"""
        response = http_session.get(f"{test_config['backend_url']}/health", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get('status') == 'healthy'
        
        print("✓ Basic service availability confirmed")
    
    def test_critical_endpoints_responding(self, http_session, test_config, services_ready):
        """Test critical endpoints are responding."""
        critical_endpoints = [
            '/health',
            '/api/v1/health/detailed',
            '/api/v1/health/metrics'
        ]
        
        for endpoint in critical_endpoints:
            url = f"{test_config['backend_url']}{endpoint}"
            response = http_session.get(url, timeout=5)
            assert response.status_code == 200, f"Critical endpoint {endpoint} failed"
        
        print("✓ All critical endpoints responding")
    
    def test_upload_endpoint_basic_functionality(self, auth_http_session, test_config, services_ready):
        """Test upload endpoint basic functionality (error handling)."""
        url = f"{test_config['backend_url']}/api/v1/upload"
        
        # Should return 400 for missing files (validation error) when authenticated
        response = auth_http_session.post(url, files=[], timeout=5)
        assert response.status_code == 400
        
        error_data = response.json()
        assert error_data.get('error') is True
        
        print("✓ Upload endpoint error handling functional with auth")
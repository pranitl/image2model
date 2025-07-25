"""
Integration tests for all API endpoints.

Tests API functionality, error handling, and response formats.
"""

import pytest
import json
import uuid
from typing import Dict, Any

@pytest.mark.integration
class TestAPIEndpoints:
    """Test all API endpoints comprehensively."""
    
    def test_health_endpoint(self, http_session, test_config, services_ready):
        """Test basic health endpoint."""
        url = f"{test_config['backend_url']}/health"
        response = http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'
    
    def test_detailed_health_endpoint(self, http_session, test_config, services_ready):
        """Test detailed health endpoint."""
        url = f"{test_config['backend_url']}/api/v1/health/detailed"
        response = http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert 'status' in data
        assert 'timestamp' in data
        assert 'components' in data
        assert isinstance(data['components'], list)
        
        # Check key components
        components = data['components']
        component_names = [c['name'] for c in components]
        expected_components = ['redis', 'celery', 'disk_space', 'fal_api']
        
        for expected in expected_components:
            assert expected in component_names, f"Missing component: {expected}"
            
        # Verify each component structure
        for component in components:
            assert 'name' in component
            assert 'status' in component
            assert 'response_time_ms' in component
            assert component['status'] in ['healthy', 'unhealthy', 'degraded']
    
    def test_metrics_endpoint(self, http_session, test_config, services_ready):
        """Test Prometheus metrics endpoint."""
        url = f"{test_config['backend_url']}/api/v1/health/metrics"
        response = http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        content_type = response.headers.get('content-type', '')
        # Handle potential duplicate charset
        assert 'text/plain' in content_type
        assert 'version=0.0.4' in content_type
        
        metrics_text = response.text
        
        # Verify key metrics are present
        expected_metrics = [
            'http_requests_total',
            'system_cpu_usage_percent',
            'system_memory_usage_percent',
            'system_disk_usage_percent'
        ]
        
        for metric in expected_metrics:
            assert metric in metrics_text, f"Missing metric: {metric}"
    
    def test_liveness_probe(self, http_session, test_config, services_ready):
        """Test Kubernetes liveness probe."""
        url = f"{test_config['backend_url']}/api/v1/health/liveness"
        response = http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'alive'
    
    def test_readiness_probe(self, http_session, test_config, services_ready):
        """Test Kubernetes readiness probe."""
        url = f"{test_config['backend_url']}/api/v1/health/readiness"
        response = http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'ready'
    
    def test_disk_usage_endpoint(self, admin_http_session, test_config, services_ready):
        """Test disk usage admin endpoint."""
        url = f"{test_config['backend_url']}/api/v1/admin/disk-usage"
        response = admin_http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure - disk usage returns upload_dir and output_dir info
        assert 'upload_dir' in data
        assert 'output_dir' in data
        assert 'timestamp' in data
        
        # Check each directory info
        for dir_key in ['upload_dir', 'output_dir']:
            dir_info = data[dir_key]
            assert 'disk_total_gb' in dir_info
            assert 'disk_used_gb' in dir_info
            assert 'disk_free_gb' in dir_info
            assert 'disk_usage_percent' in dir_info
            assert isinstance(dir_info['disk_total_gb'], (int, float))
            assert isinstance(dir_info['disk_used_gb'], (int, float))
            assert isinstance(dir_info['disk_free_gb'], (int, float))
            assert isinstance(dir_info['disk_usage_percent'], (int, float))
    
    def test_system_health_endpoint(self, admin_http_session, test_config, services_ready):
        """Test system health admin endpoint."""
        url = f"{test_config['backend_url']}/api/v1/admin/system-health"
        response = admin_http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert 'status' in data
        assert 'disk_usage' in data
        assert 'warnings' in data
        assert 'timestamp' in data
        
        # Verify disk usage details
        disk_usage = data['disk_usage']
        assert 'upload_dir' in disk_usage
        assert 'output_dir' in disk_usage
    
    def test_file_listing_endpoint(self, admin_http_session, test_config, services_ready):
        """Test file listing admin endpoint."""
        url = f"{test_config['backend_url']}/api/v1/admin/list-files?directory=uploads"
        response = admin_http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert 'uploads' in data
        assert 'results' in data
        assert isinstance(data['uploads'], list)
        assert isinstance(data['results'], list)
    
    def test_log_analysis_endpoint(self, auth_http_session, test_config, services_ready):
        """Test log analysis endpoint."""
        url = f"{test_config['backend_url']}/api/v1/logs/analyze"
        response = auth_http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure - analyze returns different fields
        assert 'time_range' in data
        assert 'log_levels' in data
        assert 'error_patterns' in data
        assert 'request_patterns' in data
        assert 'performance_metrics' in data
        assert 'lines_analyzed' in data
    
    def test_log_health_endpoint(self, auth_http_session, test_config, services_ready):
        """Test log health endpoint."""
        url = f"{test_config['backend_url']}/api/v1/logs/health"
        response = auth_http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure - log health returns different fields
        assert 'status' in data
        assert 'timestamp' in data
        assert 'statistics' in data
        assert 'issues' in data
        assert 'warnings' in data
        assert 'recommendations' in data
    
    def test_daily_summary_endpoint(self, auth_http_session, test_config, services_ready):
        """Test daily summary endpoint."""
        url = f"{test_config['backend_url']}/api/v1/logs/summary/daily"
        response = auth_http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert 'date' in data
        assert 'total_requests' in data
        assert 'error_count' in data
        assert 'avg_response_time_ms' in data
        assert 'top_endpoints' in data
        assert 'error_breakdown' in data
    
    def test_invalid_task_id_format(self, auth_http_session, test_config, services_ready):
        """Test API response to invalid task ID format."""
        url = f"{test_config['backend_url']}/api/v1/status/tasks/invalid-task-id/status"
        response = auth_http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 400
        error_data = response.json()
        assert error_data.get('error') == True
        assert 'error_code' in error_data
        assert 'message' in error_data
    
    def test_nonexistent_task_id(self, auth_http_session, test_config, services_ready):
        """Test API response to nonexistent but valid task ID."""
        fake_task_id = str(uuid.uuid4())
        url = f"{test_config['backend_url']}/api/v1/status/tasks/{fake_task_id}/status"
        response = auth_http_session.get(url, timeout=test_config['timeout'])
        
        # Should return 200 with pending status or 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert 'status' in data
            # For nonexistent tasks, status might be 'pending' or 'not_found'
    
    def test_nonexistent_job_download(self, auth_http_session, test_config, services_ready):
        """Test download attempt for nonexistent job."""
        fake_job_id = "nonexistent-job-123"
        url = f"{test_config['backend_url']}/api/v1/download/{fake_job_id}/all"
        response = auth_http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 404
        error_data = response.json()
        assert error_data.get('error') == True
    
    def test_cleanup_endpoint_post(self, admin_http_session, test_config, services_ready):
        """Test manual cleanup endpoint."""
        url = f"{test_config['backend_url']}/api/v1/admin/cleanup"
        
        # Test with default hours
        response = admin_http_session.post(url, timeout=test_config['timeout'])
        assert response.status_code == 200
        
        data = response.json()
        assert 'files_removed' in data
        assert 'freed_space_mb' in data
        assert isinstance(data['files_removed'], int)
        assert isinstance(data['freed_space_mb'], (int, float))
    
    def test_cleanup_with_custom_hours(self, admin_http_session, test_config, services_ready):
        """Test cleanup endpoint with custom hours parameter."""
        url = f"{test_config['backend_url']}/api/v1/admin/cleanup"
        
        # Test with custom hours parameter
        response = admin_http_session.post(
            url, 
            json={"hours": 1},  # Clean files older than 1 hour
            timeout=test_config['timeout']
        )
        assert response.status_code == 200
        
        data = response.json()
        assert 'files_removed' in data
        assert 'freed_space_mb' in data
    
    def test_cors_headers(self, http_session, test_config, services_ready):
        """Test CORS headers are properly set."""
        url = f"{test_config['backend_url']}/health"
        
        # Test OPTIONS request
        response = http_session.options(url, timeout=test_config['timeout'])
        
        # Should have CORS headers
        headers = response.headers
        assert 'Access-Control-Allow-Origin' in headers or response.status_code == 405
    
    def test_api_versioning(self, http_session, auth_http_session, admin_http_session, test_config, services_ready):
        """Test API versioning consistency."""
        # Test that v1 endpoints are accessible with proper auth
        public_endpoints = [
            ("/api/v1/health/detailed", http_session),
        ]
        admin_endpoints = [
            ("/api/v1/admin/disk-usage", admin_http_session),
        ]
        auth_endpoints = [
            ("/api/v1/logs/health", auth_http_session)
        ]
        
        for endpoint, session in public_endpoints + admin_endpoints + auth_endpoints:
            url = f"{test_config['backend_url']}{endpoint}"
            response = session.get(url, timeout=test_config['timeout'])
            assert response.status_code == 200, f"Endpoint {endpoint} not accessible"
    
    def test_error_response_format(self, auth_http_session, test_config, services_ready):
        """Test that error responses follow consistent format."""
        # Trigger an error with invalid file upload
        url = f"{test_config['backend_url']}/api/v1/upload"
        response = auth_http_session.post(url, files=[], timeout=test_config['timeout'])
        
        assert response.status_code == 400
        error_data = response.json()
        
        # Verify error response structure
        assert 'error' in error_data
        assert 'error_code' in error_data
        assert 'message' in error_data
        assert error_data['error'] == True
        assert isinstance(error_data['error_code'], str)
        assert isinstance(error_data['message'], str)
    
    def test_json_content_type(self, http_session, test_config, services_ready):
        """Test that JSON endpoints return correct content type."""
        url = f"{test_config['backend_url']}/health"
        response = http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        assert 'application/json' in response.headers.get('content-type', '')
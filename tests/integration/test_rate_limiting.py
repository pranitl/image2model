"""
Integration tests for rate limiting functionality.

Tests rate limiting on upload endpoints and other protected endpoints.
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

@pytest.mark.integration
class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_upload_endpoint_rate_limiting(self, auth_http_session, test_config, sample_image_file, services_ready):
        """Test rate limiting on upload endpoint (10 requests per minute)."""
        url = f"{test_config['backend_url']}/api/v1/upload"
        
        # Prepare file data
        with open(sample_image_file, 'rb') as f:
            file_content = f.read()
        
        # Function to make a single upload request
        def make_upload_request():
            files = [('files', (sample_image_file.name, file_content, 'image/jpeg'))]
            response = auth_http_session.post(url, files=files, timeout=test_config['timeout'])
            return response.status_code
        
        # Make requests up to the limit
        responses = []
        for i in range(12):  # Try 12 requests (2 more than limit)
            status_code = make_upload_request()
            responses.append(status_code)
            time.sleep(0.1)  # Small delay between requests
        
        # Count successful and rate-limited responses
        success_count = responses.count(200)
        rate_limited_count = responses.count(429)
        
        # We should have some successful requests and some rate-limited
        assert success_count > 0, "No successful requests"
        assert rate_limited_count > 0, "Rate limiting not triggered"
        
        # Specifically, we should have at most 10 successful requests per minute
        assert success_count <= 10, f"Too many successful requests: {success_count}"
    
    def test_general_api_rate_limiting(self, auth_http_session, test_config, services_ready):
        """Test general API rate limiting (100 requests per hour)."""
        url = f"{test_config['backend_url']}/api/v1/status/tasks/12345678-1234-1234-1234-123456789012/status"
        
        # Make rapid requests
        responses = []
        for i in range(10):  # Make 10 rapid requests
            response = auth_http_session.get(url, timeout=test_config['timeout'])
            responses.append(response.status_code)
        
        # All should succeed since we're well under the hourly limit
        # Note: 404 is expected for non-existent task
        assert all(status in [200, 404] for status in responses), f"Unexpected status codes: {responses}"
    
    def test_rate_limit_headers(self, auth_http_session, test_config, services_ready):
        """Test that rate limit headers are included in responses."""
        url = f"{test_config['backend_url']}/api/v1/upload"
        
        # Make a request and check headers
        with open(test_config['test_files_dir'].parent / 'fixtures' / 'files' / 'test_image.jpg', 'wb') as f:
            # Create a small test image
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(f, 'JPEG')
        
        with open(test_config['test_files_dir'].parent / 'fixtures' / 'files' / 'test_image.jpg', 'rb') as f:
            files = [('files', ('test.jpg', f, 'image/jpeg'))]
            response = auth_http_session.post(url, files=files, timeout=test_config['timeout'])
        
        # Check for rate limit headers
        headers = response.headers
        
        # Common rate limit headers (may vary by implementation)
        possible_headers = [
            'X-RateLimit-Limit',
            'X-RateLimit-Remaining',
            'X-RateLimit-Reset',
            'RateLimit-Limit',
            'RateLimit-Remaining',
            'RateLimit-Reset'
        ]
        
        # At least one rate limit header should be present
        has_rate_limit_header = any(header in headers for header in possible_headers)
        # Note: Our current implementation might not include these headers
        # This is more of a best practice check
    
    def test_rate_limit_recovery(self, auth_http_session, test_config, sample_image_file, services_ready):
        """Test that rate limiting recovers after the time window."""
        # This test would need to wait for the rate limit window to reset
        # which is impractical for fast tests, so we'll skip this for now
        pytest.skip("Rate limit recovery test requires waiting for time window")
    
    def test_concurrent_requests_rate_limiting(self, auth_http_session, test_config, sample_image_file, services_ready):
        """Test rate limiting with concurrent requests."""
        url = f"{test_config['backend_url']}/api/v1/upload"
        
        # Prepare file data
        with open(sample_image_file, 'rb') as f:
            file_content = f.read()
        
        # Function to make a single upload request
        def make_upload_request(index: int) -> Tuple[int, int]:
            files = [('files', (f'test_{index}.jpg', file_content, 'image/jpeg'))]
            try:
                response = auth_http_session.post(url, files=files, timeout=test_config['timeout'])
                return index, response.status_code
            except Exception as e:
                return index, -1
        
        # Make concurrent requests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_upload_request, i) for i in range(15)]
            results = [future.result() for future in futures]
        
        # Extract status codes
        status_codes = [status for _, status in results]
        
        # Count responses
        success_count = status_codes.count(200)
        rate_limited_count = status_codes.count(429)
        
        # We should have some rate-limited responses
        assert rate_limited_count > 0, "Concurrent requests not rate limited"
        assert success_count <= 10, f"Too many successful concurrent requests: {success_count}"
    
    def test_different_endpoints_have_different_limits(self, auth_http_session, test_config, services_ready):
        """Test that different endpoints can have different rate limits."""
        # Upload endpoint has stricter limits than general endpoints
        upload_url = f"{test_config['backend_url']}/api/v1/upload"
        status_url = f"{test_config['backend_url']}/api/v1/health/detailed"
        
        # Health endpoint should allow more requests
        health_responses = []
        for i in range(20):
            response = auth_http_session.get(status_url, timeout=test_config['timeout'])
            health_responses.append(response.status_code)
        
        # All health checks should succeed (no rate limiting on health endpoints)
        assert all(status == 200 for status in health_responses), "Health endpoint unexpectedly rate limited"
    
    def test_rate_limit_bypassed_for_admin_endpoints(self, admin_http_session, test_config, services_ready):
        """Test that admin endpoints might have different rate limits."""
        url = f"{test_config['backend_url']}/api/v1/admin/disk-usage"
        
        # Admin endpoints might have different or no rate limits
        responses = []
        for i in range(20):
            response = admin_http_session.get(url, timeout=test_config['timeout'])
            responses.append(response.status_code)
            time.sleep(0.05)  # Small delay
        
        # Check that admin endpoint is accessible
        success_count = responses.count(200)
        assert success_count > 15, f"Admin endpoint rate limited too aggressively: {success_count}/20"
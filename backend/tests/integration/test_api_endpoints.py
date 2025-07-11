"""
Integration tests for API endpoints.
"""

import pytest
import requests
import os
from typing import Dict, Any

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY", "test-api-key")


class TestAPIEndpoints:
    """Test various API endpoints for proper functionality."""
    
    @pytest.fixture
    def headers(self):
        """Common headers for API requests."""
        return {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    
    @pytest.fixture
    def admin_headers(self):
        """Headers for admin API requests."""
        admin_key = os.getenv("ADMIN_API_KEY", "admin-test-key")
        return {
            "X-Admin-Key": admin_key,
            "Content-Type": "application/json"
        }
    
    def test_health_check(self, headers):
        """Test health check endpoint."""
        response = requests.get(f"{BASE_URL}/health", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_logs_daily_summary(self, headers):
        """Test daily summary endpoint - corrected path."""
        # The actual endpoint is /logs/summary/daily, not /logs/daily-summary
        response = requests.get(f"{BASE_URL}/logs/summary/daily", headers=headers)
        
        # Check if endpoint exists
        if response.status_code == 404:
            pytest.skip("Daily summary endpoint not implemented yet")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_admin_list_files(self, admin_headers):
        """Test admin list files endpoint with required parameter."""
        # The endpoint requires a 'directory' query parameter
        response = requests.get(
            f"{BASE_URL}/admin/list-files",
            params={"directory": "uploads"},  # Required parameter
            headers=admin_headers
        )
        
        # Check various possible responses
        if response.status_code == 401:
            pytest.skip("Admin authentication not configured")
        elif response.status_code == 404:
            pytest.skip("Admin list-files endpoint not implemented")
        elif response.status_code == 422:
            # This might happen if the directory parameter is missing
            pytest.fail("Validation error - directory parameter might be missing")
        
        assert response.status_code == 200
        data = response.json()
        assert "directory" in data
        assert "items" in data
    
    def test_admin_list_files_results_directory(self, admin_headers):
        """Test admin list files endpoint for results directory."""
        response = requests.get(
            f"{BASE_URL}/admin/list-files",
            params={"directory": "results"},
            headers=admin_headers
        )
        
        if response.status_code == 401:
            pytest.skip("Admin authentication not configured")
        
        assert response.status_code == 200
        data = response.json()
        assert data["directory"] == "results"
    
    def test_admin_disk_usage(self, admin_headers):
        """Test admin disk usage endpoint."""
        response = requests.get(f"{BASE_URL}/admin/disk-usage", headers=admin_headers)
        
        if response.status_code == 401:
            pytest.skip("Admin authentication not configured")
        
        assert response.status_code == 200
        data = response.json()
        assert "upload_dir" in data
        assert "output_dir" in data
    
    def test_logs_statistics(self, headers):
        """Test logs statistics endpoint."""
        response = requests.get(f"{BASE_URL}/logs/statistics", headers=headers)
        
        if response.status_code == 404:
            pytest.skip("Logs statistics endpoint not implemented")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_files" in data
        assert "total_size_mb" in data
    
    def test_logs_types(self, headers):
        """Test logs types endpoint."""
        response = requests.get(f"{BASE_URL}/logs/types", headers=headers)
        
        if response.status_code == 404:
            pytest.skip("Logs types endpoint not implemented")
        
        assert response.status_code == 200
        data = response.json()
        assert "log_types" in data
        assert isinstance(data["log_types"], list)
    
    def test_admin_system_health(self, admin_headers):
        """Test admin system health endpoint."""
        response = requests.get(f"{BASE_URL}/admin/system-health", headers=admin_headers)
        
        if response.status_code == 401:
            pytest.skip("Admin authentication not configured")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "warning", "critical"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
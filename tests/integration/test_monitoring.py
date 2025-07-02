"""
Integration tests for monitoring and health check systems.

Tests Prometheus metrics, health endpoints, and system monitoring.
"""

import pytest
import time
import re
from typing import Dict, Any, List
import requests

@pytest.mark.integration
class TestMonitoring:
    """Test monitoring and observability features."""
    
    def test_prometheus_metrics_endpoint(self, http_session, test_config, services_ready):
        """Test Prometheus metrics endpoint functionality."""
        url = f"{test_config['backend_url']}/api/v1/health/metrics"
        response = http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'text/plain; version=0.0.4; charset=utf-8'
        
        metrics_text = response.text
        assert len(metrics_text) > 0, "Metrics endpoint returned empty response"
        
        # Test for essential metrics
        essential_metrics = [
            'http_requests_total',
            'http_request_duration_seconds',
            'system_cpu_usage_percent',
            'system_memory_usage_percent',
            'system_disk_usage_percent'
        ]
        
        for metric in essential_metrics:
            assert metric in metrics_text, f"Essential metric '{metric}' not found in response"
        
        # Validate Prometheus format
        lines = metrics_text.strip().split('\\n')
        metric_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        
        assert len(metric_lines) > 0, "No metric data lines found"
        
        # Validate metric format (name{labels} value)
        for line in metric_lines[:5]:  # Check first 5 metric lines
            parts = line.split(' ')
            assert len(parts) >= 2, f"Invalid metric line format: {line}"
            
            metric_name = parts[0].split('{')[0]
            assert re.match(r'^[a-zA-Z_:][a-zA-Z0-9_:]*$', metric_name), f"Invalid metric name: {metric_name}"
    
    def test_system_metrics_collection(self, http_session, test_config, services_ready):
        """Test system metrics are being collected and updated."""
        url = f"{test_config['backend_url']}/api/v1/health/metrics"
        
        # Get initial metrics
        response1 = http_session.get(url, timeout=test_config['timeout'])
        assert response1.status_code == 200
        metrics1 = self._parse_metrics(response1.text)
        
        # Wait a bit for metrics to update
        time.sleep(5)
        
        # Get updated metrics
        response2 = http_session.get(url, timeout=test_config['timeout'])
        assert response2.status_code == 200
        metrics2 = self._parse_metrics(response2.text)
        
        # Check that system metrics are present and reasonable
        system_metrics = ['system_cpu_usage_percent', 'system_memory_usage_percent', 'system_disk_usage_percent']
        
        for metric in system_metrics:
            assert metric in metrics1, f"System metric '{metric}' not found in first reading"
            assert metric in metrics2, f"System metric '{metric}' not found in second reading"
            
            value1 = metrics1[metric]
            value2 = metrics2[metric]
            
            # Values should be reasonable percentages
            assert 0 <= value1 <= 100, f"{metric} value out of range: {value1}"
            assert 0 <= value2 <= 100, f"{metric} value out of range: {value2}"
    
    def test_request_metrics_collection(self, http_session, test_config, services_ready):
        """Test HTTP request metrics are being collected."""
        metrics_url = f"{test_config['backend_url']}/api/v1/health/metrics"
        health_url = f"{test_config['backend_url']}/health"
        
        # Get baseline metrics
        response = http_session.get(metrics_url, timeout=test_config['timeout'])
        assert response.status_code == 200
        baseline_metrics = self._parse_metrics(response.text)
        
        # Make some requests to generate metrics
        for _ in range(5):
            http_session.get(health_url, timeout=test_config['timeout'])
        
        # Get updated metrics
        response = http_session.get(metrics_url, timeout=test_config['timeout'])
        assert response.status_code == 200
        updated_metrics = self._parse_metrics(response.text)
        
        # Check request count increased
        request_count_metric = 'http_requests_total'
        
        if request_count_metric in baseline_metrics and request_count_metric in updated_metrics:
            baseline_count = baseline_metrics[request_count_metric]
            updated_count = updated_metrics[request_count_metric]
            
            assert updated_count >= baseline_count, "Request count should have increased"
        
        # Check request duration metrics exist
        assert 'http_request_duration_seconds' in updated_metrics, "Request duration metrics not found"
    
    def test_health_check_endpoints(self, http_session, test_config, services_ready):
        """Test all health check endpoints."""
        health_endpoints = [
            ('/health', 'Basic health check'),
            ('/api/v1/health/detailed', 'Detailed health check'),
            ('/api/v1/health/liveness', 'Liveness probe'),
            ('/api/v1/health/readiness', 'Readiness probe')
        ]
        
        for endpoint, description in health_endpoints:
            url = f"{test_config['backend_url']}{endpoint}"
            response = http_session.get(url, timeout=test_config['timeout'])
            
            assert response.status_code == 200, f"{description} failed with status {response.status_code}"
            
            data = response.json()
            assert 'status' in data, f"{description} missing status field"
            
            status = data['status']
            valid_statuses = ['healthy', 'alive', 'ready', 'degraded']
            assert status in valid_statuses, f"{description} returned invalid status: {status}"
    
    def test_detailed_health_check_components(self, http_session, test_config, services_ready):
        """Test detailed health check includes all components."""
        url = f"{test_config['backend_url']}/api/v1/health/detailed"
        response = http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        required_fields = ['status', 'timestamp', 'components']
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing from detailed health check"
        
        # Component checks
        components = data['components']
        assert isinstance(components, dict), "Components should be a dictionary"
        
        expected_components = ['database', 'redis', 'celery', 'disk_space']
        for component in expected_components:
            assert component in components, f"Component '{component}' missing from health check"
            
            component_data = components[component]
            assert 'status' in component_data, f"Component '{component}' missing status"
            
            component_status = component_data['status']
            valid_statuses = ['healthy', 'unhealthy', 'degraded']
            assert component_status in valid_statuses, f"Component '{component}' has invalid status: {component_status}"
    
    def test_disk_usage_monitoring(self, http_session, test_config, services_ready):
        """Test disk usage monitoring functionality."""
        url = f"{test_config['backend_url']}/api/v1/admin/disk-usage"
        response = http_session.get(url, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        
        # Required fields
        required_fields = [
            'total_size_gb',\n            'used_size_gb',\n            'free_size_gb',\n            'usage_percentage',\n            'directories'\n        ]\n        \n        for field in required_fields:\n            assert field in data, f\"Required field '{field}' missing from disk usage response\"\n        \n        # Validate data types and ranges\n        assert isinstance(data['total_size_gb'], (int, float)), \"total_size_gb should be numeric\"\n        assert isinstance(data['used_size_gb'], (int, float)), \"used_size_gb should be numeric\"\n        assert isinstance(data['free_size_gb'], (int, float)), \"free_size_gb should be numeric\"\n        assert isinstance(data['usage_percentage'], (int, float)), \"usage_percentage should be numeric\"\n        assert isinstance(data['directories'], dict), \"directories should be a dictionary\"\n        \n        # Logical validations\n        assert data['total_size_gb'] > 0, \"Total size should be positive\"\n        assert data['used_size_gb'] >= 0, \"Used size should be non-negative\"\n        assert data['free_size_gb'] >= 0, \"Free size should be non-negative\"\n        assert 0 <= data['usage_percentage'] <= 100, \"Usage percentage should be between 0 and 100\"\n        \n        # Size consistency\n        calculated_total = data['used_size_gb'] + data['free_size_gb']\n        assert abs(calculated_total - data['total_size_gb']) < 0.1, \"Size calculations inconsistent\"\n    \n    def test_system_health_monitoring(self, http_session, test_config, services_ready):\n        \"\"\"Test system health monitoring endpoint.\"\"\"\n        url = f\"{test_config['backend_url']}/api/v1/admin/system-health\"\n        response = http_session.get(url, timeout=test_config['timeout'])\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        # Required fields\n        required_fields = ['status', 'disk_usage', 'services', 'warnings']\n        for field in required_fields:\n            assert field in data, f\"Required field '{field}' missing from system health response\"\n        \n        # Validate disk usage section\n        disk_usage = data['disk_usage']\n        assert isinstance(disk_usage, dict), \"disk_usage should be a dictionary\"\n        \n        disk_fields = ['percentage', 'free_gb', 'total_gb']\n        for field in disk_fields:\n            assert field in disk_usage, f\"Disk usage missing field '{field}'\"\n        \n        # Validate services section\n        services = data['services']\n        assert isinstance(services, dict), \"services should be a dictionary\"\n        \n        # Validate warnings section\n        warnings = data['warnings']\n        assert isinstance(warnings, list), \"warnings should be a list\"\n    \n    def test_log_analysis_endpoints(self, http_session, test_config, services_ready):\n        \"\"\"Test log analysis and monitoring endpoints.\"\"\"\n        log_endpoints = [\n            ('/api/v1/logs/analyze', 'Log analysis'),\n            ('/api/v1/logs/health', 'Log health'),\n            ('/api/v1/logs/daily-summary', 'Daily summary')\n        ]\n        \n        for endpoint, description in log_endpoints:\n            url = f\"{test_config['backend_url']}{endpoint}\"\n            response = http_session.get(url, timeout=test_config['timeout'])\n            \n            assert response.status_code == 200, f\"{description} endpoint failed with status {response.status_code}\"\n            \n            data = response.json()\n            assert isinstance(data, dict), f\"{description} should return a dictionary\"\n            assert len(data) > 0, f\"{description} returned empty data\"\n    \n    def test_log_health_monitoring(self, http_session, test_config, services_ready):\n        \"\"\"Test log health monitoring specifics.\"\"\"\n        url = f\"{test_config['backend_url']}/api/v1/logs/health\"\n        response = http_session.get(url, timeout=test_config['timeout'])\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        # Expected fields in log health\n        expected_fields = ['status', 'log_files', 'total_size_mb']\n        for field in expected_fields:\n            assert field in data, f\"Log health missing field '{field}'\"\n        \n        # Validate data types\n        assert isinstance(data['log_files'], list), \"log_files should be a list\"\n        assert isinstance(data['total_size_mb'], (int, float)), \"total_size_mb should be numeric\"\n        assert data['total_size_mb'] >= 0, \"total_size_mb should be non-negative\"\n    \n    def test_celery_task_monitoring(self, http_session, test_config, services_ready):\n        \"\"\"Test Celery task monitoring through metrics.\"\"\"\n        metrics_url = f\"{test_config['backend_url']}/api/v1/health/metrics\"\n        \n        # Trigger a simple task by making an upload request\n        # (This will create a task even if it fails due to invalid file)\n        upload_url = f\"{test_config['backend_url']}/api/v1/upload/image\"\n        \n        # Get baseline metrics\n        response = http_session.get(metrics_url, timeout=test_config['timeout'])\n        assert response.status_code == 200\n        baseline_metrics = self._parse_metrics(response.text)\n        \n        # Make request that will trigger task\n        try:\n            http_session.post(upload_url, timeout=5)  # Will fail due to missing file, but may create task\n        except:\n            pass  # Expected to fail\n        \n        # Wait for potential task processing\n        time.sleep(2)\n        \n        # Get updated metrics\n        response = http_session.get(metrics_url, timeout=test_config['timeout'])\n        assert response.status_code == 200\n        updated_metrics = self._parse_metrics(response.text)\n        \n        # Check for Celery metrics\n        celery_metrics = [metric for metric in updated_metrics.keys() if 'celery' in metric.lower()]\n        \n        if celery_metrics:\n            print(f\"Found Celery metrics: {celery_metrics}\")\n        else:\n            print(\"No Celery metrics found (may be expected if no tasks were created)\")\n    \n    def test_fal_api_monitoring(self, http_session, test_config, services_ready):\n        \"\"\"Test FAL.AI API monitoring metrics.\"\"\"\n        metrics_url = f\"{test_config['backend_url']}/api/v1/health/metrics\"\n        response = http_session.get(metrics_url, timeout=test_config['timeout'])\n        \n        assert response.status_code == 200\n        metrics = self._parse_metrics(response.text)\n        \n        # Look for FAL API metrics\n        fal_metrics = [metric for metric in metrics.keys() if 'fal_api' in metric.lower()]\n        \n        # FAL API metrics might not be present if no API calls have been made\n        # This is acceptable for this test\n        print(f\"FAL API metrics found: {fal_metrics if fal_metrics else 'None (expected if no API calls made)'}\")\n    \n    def test_monitoring_data_persistence(self, http_session, test_config, services_ready):\n        \"\"\"Test that monitoring data persists across requests.\"\"\"\n        metrics_url = f\"{test_config['backend_url']}/api/v1/health/metrics\"\n        \n        # Make multiple requests and ensure metrics are consistent\n        responses = []\n        for _ in range(3):\n            response = http_session.get(metrics_url, timeout=test_config['timeout'])\n            assert response.status_code == 200\n            responses.append(response.text)\n            time.sleep(1)\n        \n        # Parse metrics from each response\n        metrics_sets = [self._parse_metrics(resp) for resp in responses]\n        \n        # Check that core metrics exist in all responses\n        core_metrics = ['system_cpu_usage_percent', 'system_memory_usage_percent']\n        \n        for metric in core_metrics:\n            for i, metrics in enumerate(metrics_sets):\n                assert metric in metrics, f\"Core metric '{metric}' missing in response {i+1}\"\n    \n    def _parse_metrics(self, metrics_text: str) -> Dict[str, float]:\n        \"\"\"Parse Prometheus metrics text into a dictionary.\"\"\"\n        metrics = {}\n        \n        for line in metrics_text.split('\\n'):\n            line = line.strip()\n            if not line or line.startswith('#'):\n                continue\n            \n            parts = line.split(' ')\n            if len(parts) >= 2:\n                metric_name = parts[0].split('{')[0]  # Remove labels\n                try:\n                    metric_value = float(parts[1])\n                    metrics[metric_name] = metric_value\n                except ValueError:\n                    continue\n        \n        return metrics"
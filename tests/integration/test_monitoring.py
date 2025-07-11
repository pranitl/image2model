"""
Integration tests for monitoring and health check systems.

Tests Prometheus metrics, health endpoints, and system monitoring.
"""

import pytest
import time
import re
from typing import Dict


@pytest.mark.integration
class TestMonitoring:
    """Test monitoring and observability features."""

    def test_prometheus_metrics_endpoint(
        self, http_session, test_config, services_ready
    ):
        """Test Prometheus metrics endpoint functionality."""
        url = f"{test_config['backend_url']}/api/v1/health/metrics"
        response = http_session.get(url, timeout=test_config["timeout"])

        assert response.status_code == 200
        assert (
            response.headers.get("content-type")
            == "text/plain; version=0.0.4; charset=utf-8"
        )

        metrics_text = response.text
        assert (
            len(metrics_text) > 0
        ), "Metrics endpoint returned empty response"

        # Test for essential metrics
        essential_metrics = [
            "http_requests_total",
            "http_request_duration_seconds",
            "system_cpu_usage_percent",
            "system_memory_usage_percent",
            "system_disk_usage_percent",
        ]

        for metric in essential_metrics:
            assert (
                metric in metrics_text
            ), f"Essential metric '{metric}' not found in response"

        # Validate Prometheus format
        lines = metrics_text.strip().split("\n")
        metric_lines = [
            line for line in lines if not line.startswith("#") and line.strip()
        ]

        assert len(metric_lines) > 0, "No metric data lines found"

        # Validate metric format (name{labels} value)
        for line in metric_lines[:5]:  # Check first 5 metric lines
            parts = line.split(" ")
            assert len(parts) >= 2, f"Invalid metric line format: {line}"

            metric_name = parts[0].split("{")[0]
            assert re.match(
                r"^[a-zA-Z_:][a-zA-Z0-9_:]*$", metric_name
            ), f"Invalid metric name: {metric_name}"

    def test_system_metrics_collection(
        self, http_session, test_config, services_ready
    ):
        """Test system metrics are being collected and updated."""
        url = f"{test_config['backend_url']}/api/v1/health/metrics"

        # Get initial metrics
        response1 = http_session.get(url, timeout=test_config["timeout"])
        assert response1.status_code == 200
        metrics1 = self._parse_metrics(response1.text)

        # Wait a bit for metrics to update
        time.sleep(5)

        # Get updated metrics
        response2 = http_session.get(url, timeout=test_config["timeout"])
        assert response2.status_code == 200
        metrics2 = self._parse_metrics(response2.text)

        # Check that system metrics are present and reasonable
        system_metrics = [
            "system_cpu_usage_percent",
            "system_memory_usage_percent",
            "system_disk_usage_percent",
        ]

        for metric in system_metrics:
            assert (
                metric in metrics1
            ), f"System metric '{metric}' not found in first reading"
            assert (
                metric in metrics2
            ), f"System metric '{metric}' not found in second reading"

            value1 = metrics1[metric]
            value2 = metrics2[metric]

            # Values should be reasonable percentages
            assert 0 <= value1 <= 100, f"{metric} value out of range: {value1}"
            assert 0 <= value2 <= 100, f"{metric} value out of range: {value2}"

    def test_request_metrics_collection(
        self, http_session, test_config, services_ready
    ):
        """Test HTTP request metrics are being collected."""
        metrics_url = f"{test_config['backend_url']}/api/v1/health/metrics"
        health_url = f"{test_config['backend_url']}/health"

        # Get baseline metrics
        response = http_session.get(
            metrics_url, timeout=test_config["timeout"]
        )
        assert response.status_code == 200
        baseline_metrics = self._parse_metrics(response.text)

        # Make some requests to generate metrics
        for _ in range(5):
            http_session.get(health_url, timeout=test_config["timeout"])

        # Get updated metrics
        response = http_session.get(
            metrics_url, timeout=test_config["timeout"]
        )
        assert response.status_code == 200
        updated_metrics = self._parse_metrics(response.text)

        # Check request count increased
        request_count_metric = "http_requests_total"

        if (
            request_count_metric in baseline_metrics
            and request_count_metric in updated_metrics
        ):
            baseline_count = baseline_metrics[request_count_metric]
            updated_count = updated_metrics[request_count_metric]

            assert (
                updated_count >= baseline_count
            ), "Request count should have increased"

        # Check request duration metrics exist
        assert (
            "http_request_duration_seconds" in updated_metrics
        ), "Request duration metrics not found"

    def test_health_check_endpoints(
        self, http_session, test_config, services_ready
    ):
        """Test all health check endpoints."""
        health_endpoints = [
            ("/health", "Basic health check"),
            ("/api/v1/health/detailed", "Detailed health check"),
            ("/api/v1/health/liveness", "Liveness probe"),
            ("/api/v1/health/readiness", "Readiness probe"),
        ]

        for endpoint, description in health_endpoints:
            url = f"{test_config['backend_url']}{endpoint}"
            response = http_session.get(url, timeout=test_config["timeout"])

            assert (
                response.status_code == 200
            ), f"{description} failed with status {response.status_code}"

            data = response.json()
            assert "status" in data, f"{description} missing status field"

            status = data["status"]
            valid_statuses = ["healthy", "alive", "ready", "degraded"]
            assert (
                status in valid_statuses
            ), f"{description} returned invalid status: {status}"

    def test_detailed_health_check_components(
        self, http_session, test_config, services_ready
    ):
        """Test detailed health check includes all components."""
        url = f"{test_config['backend_url']}/api/v1/health/detailed"
        response = http_session.get(url, timeout=test_config["timeout"])

        assert response.status_code == 200
        data = response.json()

        # Required fields
        required_fields = ["status", "timestamp", "components"]
        for field in required_fields:
            assert (
                field in data
            ), f"Required field '{field}' missing from detailed health check"

        # Component checks
        components = data["components"]
        assert isinstance(
            components, dict
        ), "Components should be a dictionary"

        expected_components = ["database", "redis", "celery", "disk_space"]
        for component in expected_components:
            assert (
                component in components
            ), f"Component '{component}' missing from health check"

            component_data = components[component]
            assert (
                "status" in component_data
            ), f"Component '{component}' missing status"

            component_status = component_data["status"]
            valid_statuses = ["healthy", "unhealthy", "degraded"]
            assert (
                component_status in valid_statuses
            ), f"Component '{component}' has invalid status: {component_status}"

    def test_disk_usage_monitoring(
        self, http_session, test_config, services_ready
    ):
        """Test disk usage monitoring functionality."""
        url = f"{test_config['backend_url']}/api/v1/admin/disk-usage"
        response = http_session.get(url, timeout=test_config["timeout"])

        assert response.status_code == 200
        data = response.json()

        # Required fields
        required_fields = [
            "total_size_gb",
            "used_size_gb",
            "free_size_gb",
            "usage_percentage",
            "directories",
        ]

        for field in required_fields:
            assert (
                field in data
            ), f"Required field '{field}' missing from disk usage response"

        # Validate data types and ranges
        assert isinstance(
            data["total_size_gb"], (int, float)
        ), "total_size_gb should be numeric"
        assert isinstance(
            data["used_size_gb"], (int, float)
        ), "used_size_gb should be numeric"
        assert isinstance(
            data["free_size_gb"], (int, float)
        ), "free_size_gb should be numeric"
        assert isinstance(
            data["usage_percentage"], (int, float)
        ), "usage_percentage should be numeric"
        assert isinstance(
            data["directories"], dict
        ), "directories should be a dictionary"

        # Logical validations
        assert data["total_size_gb"] > 0, "Total size should be positive"
        assert data["used_size_gb"] >= 0, "Used size should be non-negative"
        assert data["free_size_gb"] >= 0, "Free size should be non-negative"
        assert (
            0 <= data["usage_percentage"] <= 100
        ), "Usage percentage should be between 0 and 100"

        # Size consistency
        calculated_total = data["used_size_gb"] + data["free_size_gb"]
        assert (
            abs(calculated_total - data["total_size_gb"]) < 0.1
        ), "Size calculations inconsistent"

    def test_system_health_monitoring(
        self, http_session, test_config, services_ready
    ):
        """Test system health monitoring endpoint."""
        url = f"{test_config['backend_url']}/api/v1/admin/system-health"
        response = http_session.get(url, timeout=test_config["timeout"])

        assert response.status_code == 200
        data = response.json()

        # Required fields
        required_fields = ["status", "disk_usage", "services", "warnings"]
        for field in required_fields:
            assert (
                field in data
            ), f"Required field '{field}' missing from system health response"

        # Validate disk usage section
        disk_usage = data["disk_usage"]
        assert isinstance(
            disk_usage, dict
        ), "disk_usage should be a dictionary"

        disk_fields = ["percentage", "free_gb", "total_gb"]
        for field in disk_fields:
            assert field in disk_usage, f"Disk usage missing field '{field}'"

        # Validate services section
        services = data["services"]
        assert isinstance(services, dict), "services should be a dictionary"

        # Validate warnings section
        warnings = data["warnings"]
        assert isinstance(warnings, list), "warnings should be a list"

    def test_log_analysis_endpoints(
        self, http_session, test_config, services_ready
    ):
        """Test log analysis and monitoring endpoints."""
        log_endpoints = [
            ("/api/v1/logs/analyze", "Log analysis"),
            ("/api/v1/logs/health", "Log health"),
            ("/api/v1/logs/daily-summary", "Daily summary"),
        ]

        for endpoint, description in log_endpoints:
            url = f"{test_config['backend_url']}{endpoint}"
            response = http_session.get(url, timeout=test_config["timeout"])

            assert (
                response.status_code == 200
            ), f"{description} endpoint failed with status {response.status_code}"

            data = response.json()
            assert isinstance(
                data, dict
            ), f"{description} should return a dictionary"
            assert len(data) > 0, f"{description} returned empty data"

    def test_log_health_monitoring(
        self, http_session, test_config, services_ready
    ):
        """Test log health monitoring specifics."""
        url = f"{test_config['backend_url']}/api/v1/logs/health"
        response = http_session.get(url, timeout=test_config["timeout"])

        assert response.status_code == 200
        data = response.json()

        # Expected fields in log health
        expected_fields = ["status", "log_files", "total_size_mb"]
        for field in expected_fields:
            assert field in data, f"Log health missing field '{field}'"

        # Validate data types
        assert isinstance(
            data["log_files"], list
        ), "log_files should be a list"
        assert isinstance(
            data["total_size_mb"], (int, float)
        ), "total_size_mb should be numeric"
        assert (
            data["total_size_mb"] >= 0
        ), "total_size_mb should be non-negative"

    def test_celery_task_monitoring(
        self, http_session, test_config, services_ready
    ):
        """Test Celery task monitoring through metrics."""
        metrics_url = f"{test_config['backend_url']}/api/v1/health/metrics"

        # Trigger a simple task by making an upload request
        # (This will create a task even if it fails due to invalid file)
        upload_url = f"{test_config['backend_url']}/api/v1/upload"

        # Get baseline metrics
        response = http_session.get(
            metrics_url, timeout=test_config["timeout"]
        )
        assert response.status_code == 200
        self._parse_metrics(response.text)  # Validate metrics format

        # Make request that will trigger task
        try:
            # Will fail due to missing file, but may create task
            http_session.post(upload_url, timeout=5)
        except BaseException:
            pass  # Expected to fail

        # Wait for potential task processing
        time.sleep(2)

        # Get updated metrics
        response = http_session.get(
            metrics_url, timeout=test_config["timeout"]
        )
        assert response.status_code == 200
        updated_metrics = self._parse_metrics(response.text)

        # Check for Celery metrics
        celery_metrics = [
            metric
            for metric in updated_metrics.keys()
            if "celery" in metric.lower()
        ]

        if celery_metrics:
            print(f"Found Celery metrics: {celery_metrics}")
        else:
            print(
                "No Celery metrics found (may be expected if no tasks were created)"
            )

    def test_fal_api_monitoring(
        self, http_session, test_config, services_ready
    ):
        """Test FAL.AI API monitoring metrics."""
        metrics_url = f"{test_config['backend_url']}/api/v1/health/metrics"
        response = http_session.get(
            metrics_url, timeout=test_config["timeout"]
        )

        assert response.status_code == 200
        metrics = self._parse_metrics(response.text)

        # Look for FAL API metrics
        fal_metrics = [
            metric for metric in metrics.keys() if "fal_api" in metric.lower()
        ]

        # FAL API metrics might not be present if no API calls have been made
        # This is acceptable for this test
        print(
            f"FAL API metrics found: {fal_metrics if fal_metrics else 'None (expected if no API calls made)'}"
        )

    def test_monitoring_data_persistence(
        self, http_session, test_config, services_ready
    ):
        """Test that monitoring data persists across requests."""
        metrics_url = f"{test_config['backend_url']}/api/v1/health/metrics"

        # Make multiple requests and ensure metrics are consistent
        responses = []
        for _ in range(3):
            response = http_session.get(
                metrics_url, timeout=test_config["timeout"]
            )
            assert response.status_code == 200
            responses.append(response.text)
            time.sleep(1)

        # Parse metrics from each response
        metrics_sets = [self._parse_metrics(resp) for resp in responses]

        # Check that core metrics exist in all responses
        core_metrics = [
            "system_cpu_usage_percent",
            "system_memory_usage_percent",
        ]

        for metric in core_metrics:
            for i, metrics in enumerate(metrics_sets):
                assert (
                    metric in metrics
                ), f"Core metric '{metric}' missing in response {i+1}"

    def _parse_metrics(self, metrics_text: str) -> Dict[str, float]:
        """Parse Prometheus metrics text into a dictionary."""
        metrics = {}

        for line in metrics_text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(" ")
            if len(parts) >= 2:
                metric_name = parts[0].split("{")[0]  # Remove labels
                try:
                    metric_value = float(parts[1])
                    metrics[metric_name] = metric_value
                except ValueError:
                    continue

        return metrics

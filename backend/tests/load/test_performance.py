"""
Load and performance tests for the API.
"""

import pytest
import requests
import time
import concurrent.futures
import statistics
import os
from typing import List, Dict, Any, Tuple

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY", "test-api-key")
LOAD_TEST_API_KEY = os.getenv("LOAD_TEST_API_KEY", API_KEY)


class TestPerformance:
    """Performance and load tests for API endpoints."""
    
    @pytest.fixture
    def headers(self):
        """Common headers for API requests."""
        return {
            "X-API-Key": LOAD_TEST_API_KEY,
            "Content-Type": "application/json"
        }
    
    def make_request(self, endpoint: str, method: str = "GET", 
                    headers: dict = None, json_data: dict = None) -> Tuple[float, int]:
        """Make a single request and return response time and status code."""
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=json_data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            return response_time, response.status_code
        
        except requests.exceptions.Timeout:
            return 30.0, 408  # Request timeout
        except requests.exceptions.ConnectionError:
            return 0.0, 503  # Service unavailable
        except Exception:
            return 0.0, 500  # Internal error
    
    def run_concurrent_requests(self, endpoint: str, num_requests: int, 
                              max_workers: int, headers: dict, 
                              method: str = "GET", json_data: dict = None) -> Dict[str, Any]:
        """Run concurrent requests and collect statistics."""
        response_times = []
        status_codes = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for _ in range(num_requests):
                future = executor.submit(self.make_request, endpoint, method, headers, json_data)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                response_time, status_code = future.result()
                response_times.append(response_time)
                status_codes.append(status_code)
        
        # Calculate statistics
        successful_requests = sum(1 for code in status_codes if 200 <= code < 300)
        failed_requests = sum(1 for code in status_codes if code >= 400)
        
        stats = {
            "total_requests": num_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / num_requests) * 100,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 1 else 0,
                "p99": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 1 else 0,
            },
            "status_code_distribution": {}
        }
        
        # Count status codes
        for code in set(status_codes):
            stats["status_code_distribution"][code] = status_codes.count(code)
        
        return stats
    
    @pytest.mark.load
    def test_health_endpoint_load(self, headers):
        """Test health endpoint under load."""
        stats = self.run_concurrent_requests(
            endpoint="/health",
            num_requests=100,
            max_workers=10,
            headers=headers
        )
        
        # Assertions
        assert stats["success_rate"] >= 95, f"Success rate too low: {stats['success_rate']}%"
        assert stats["response_times"]["p95"] < 1.0, f"95th percentile too high: {stats['response_times']['p95']}s"
        assert stats["response_times"]["mean"] < 0.5, f"Mean response time too high: {stats['response_times']['mean']}s"
    
    @pytest.mark.load
    def test_concurrent_uploads(self, headers):
        """Test concurrent upload requests."""
        upload_data = {
            "url": "https://example.com/test-image.jpg"
        }
        
        stats = self.run_concurrent_requests(
            endpoint="/upload/url",
            num_requests=50,
            max_workers=5,
            headers=headers,
            method="POST",
            json_data=upload_data
        )
        
        # More lenient for upload endpoint
        assert stats["success_rate"] >= 80, f"Success rate too low: {stats['success_rate']}%"
        assert stats["response_times"]["p95"] < 5.0, f"95th percentile too high: {stats['response_times']['p95']}s"
    
    @pytest.mark.load
    def test_status_endpoint_load(self, headers):
        """Test status endpoint under load."""
        # Use a dummy task ID
        task_id = "load-test-task-12345"
        
        stats = self.run_concurrent_requests(
            endpoint=f"/status/{task_id}",
            num_requests=100,
            max_workers=20,
            headers=headers
        )
        
        # Status endpoint might return 404 for non-existent tasks
        # Check that it handles load gracefully
        total_responses = stats["successful_requests"] + stats["failed_requests"]
        assert total_responses >= 95, f"Too many timeouts: {100 - total_responses}"
        assert stats["response_times"]["p95"] < 2.0, f"95th percentile too high: {stats['response_times']['p95']}s"
    
    @pytest.mark.load
    def test_api_rate_limiting(self, headers):
        """Test API rate limiting behavior."""
        # Send requests rapidly to trigger rate limiting
        stats = self.run_concurrent_requests(
            endpoint="/health",
            num_requests=200,
            max_workers=50,  # High concurrency
            headers=headers
        )
        
        # Check if rate limiting is in place
        rate_limited = stats["status_code_distribution"].get(429, 0)
        
        if rate_limited > 0:
            # Rate limiting is active
            assert rate_limited < 100, "Too many requests rate limited"
            print(f"Rate limiting active: {rate_limited} requests limited")
        else:
            # No rate limiting - ensure all requests succeeded
            assert stats["success_rate"] >= 90, f"Success rate too low without rate limiting: {stats['success_rate']}%"
    
    @pytest.mark.load
    @pytest.mark.slow
    def test_sustained_load(self, headers):
        """Test API under sustained load for a longer period."""
        # Run for 60 seconds with steady load
        duration = 60  # seconds
        requests_per_second = 5
        
        start_time = time.time()
        all_stats = []
        
        while time.time() - start_time < duration:
            # Send a batch of requests
            stats = self.run_concurrent_requests(
                endpoint="/health",
                num_requests=requests_per_second,
                max_workers=requests_per_second,
                headers=headers
            )
            all_stats.append(stats)
            
            # Wait to maintain steady rate
            elapsed = time.time() - start_time
            expected_elapsed = len(all_stats)
            if expected_elapsed > elapsed:
                time.sleep(expected_elapsed - elapsed)
        
        # Analyze overall performance
        total_requests = sum(s["total_requests"] for s in all_stats)
        total_successful = sum(s["successful_requests"] for s in all_stats)
        overall_success_rate = (total_successful / total_requests) * 100
        
        all_response_times = []
        for stats in all_stats:
            all_response_times.extend([stats["response_times"]["mean"]] * stats["total_requests"])
        
        overall_mean = statistics.mean(all_response_times)
        
        # Assertions for sustained load
        assert overall_success_rate >= 95, f"Overall success rate too low: {overall_success_rate}%"
        assert overall_mean < 0.5, f"Overall mean response time too high: {overall_mean}s"
    
    @pytest.mark.load
    def test_error_recovery(self, headers):
        """Test API recovery from errors."""
        # First, send requests to a non-existent endpoint to generate errors
        error_stats = self.run_concurrent_requests(
            endpoint="/nonexistent/endpoint",
            num_requests=50,
            max_workers=10,
            headers=headers
        )
        
        # Verify errors are handled properly
        assert error_stats["status_code_distribution"].get(404, 0) > 0, "Expected 404 errors"
        
        # Then send requests to valid endpoint to test recovery
        recovery_stats = self.run_concurrent_requests(
            endpoint="/health",
            num_requests=50,
            max_workers=10,
            headers=headers
        )
        
        # Should recover and handle requests normally
        assert recovery_stats["success_rate"] >= 95, f"Recovery success rate too low: {recovery_stats['success_rate']}%"
    
    @pytest.mark.load
    def test_mixed_endpoint_load(self, headers):
        """Test multiple endpoints under mixed load."""
        endpoints = [
            ("/health", "GET", None),
            ("/status/test-123", "GET", None),
            ("/models", "GET", None),
        ]
        
        all_stats = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            
            # Submit requests for different endpoints
            for endpoint, method, data in endpoints:
                for _ in range(30):  # 30 requests per endpoint
                    future = executor.submit(self.make_request, endpoint, method, headers, data)
                    futures.append((endpoint, future))
            
            # Collect results by endpoint
            endpoint_stats = {}
            for endpoint, future in futures:
                if endpoint not in endpoint_stats:
                    endpoint_stats[endpoint] = {"times": [], "codes": []}
                
                response_time, status_code = future.result()
                endpoint_stats[endpoint]["times"].append(response_time)
                endpoint_stats[endpoint]["codes"].append(status_code)
        
        # Verify each endpoint performs adequately
        for endpoint, stats in endpoint_stats.items():
            successful = sum(1 for code in stats["codes"] if 200 <= code < 300)
            success_rate = (successful / len(stats["codes"])) * 100
            mean_time = statistics.mean(stats["times"]) if stats["times"] else 0
            
            print(f"{endpoint}: {success_rate:.1f}% success, {mean_time:.3f}s mean response time")
            
            # Relaxed assertions for mixed load
            assert success_rate >= 80, f"{endpoint} success rate too low: {success_rate}%"
            assert mean_time < 3.0, f"{endpoint} mean response time too high: {mean_time}s"


if __name__ == "__main__":
    # Run only non-slow tests by default
    pytest.main([__file__, "-v", "-m", "not slow"])
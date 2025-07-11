"""
Load testing for performance validation.

Tests system behavior under various load conditions.
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import requests

@pytest.mark.load
class TestPerformance:
    """Performance and load testing."""
    
    def test_health_endpoint_load(self, http_session, test_config, services_ready):
        """Test health endpoint under load."""
        url = f"{test_config['backend_url']}/health"
        
        # Test parameters
        concurrent_requests = 20
        total_requests = 100
        
        def make_request() -> Dict[str, Any]:
            start_time = time.time()
            try:
                response = http_session.get(url, timeout=test_config['timeout'])
                duration = time.time() - start_time
                
                return {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'duration': duration,
                    'error': None
                }
            except Exception as e:
                duration = time.time() - start_time
                return {
                    'success': False,
                    'status_code': 0,
                    'duration': duration,
                    'error': str(e)
                }
        
        # Execute load test
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(total_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        total_duration = time.time() - start_time
        
        # Analyze results
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        success_rate = len(successful_requests) / len(results)
        avg_duration = statistics.mean([r['duration'] for r in successful_requests]) if successful_requests else 0
        max_duration = max([r['duration'] for r in successful_requests]) if successful_requests else 0
        min_duration = min([r['duration'] for r in successful_requests]) if successful_requests else 0
        
        requests_per_second = len(results) / total_duration
        
        # Print performance metrics
        print(f\"Load Test Results (Health Endpoint):\")
        print(f\"Total requests: {len(results)}\")
        print(f\"Successful: {len(successful_requests)} ({success_rate:.2%})\")
        print(f\"Failed: {len(failed_requests)}\")
        print(f\"Requests/second: {requests_per_second:.2f}\")
        print(f\"Average response time: {avg_duration:.3f}s\")
        print(f\"Min response time: {min_duration:.3f}s\")
        print(f\"Max response time: {max_duration:.3f}s\")
        
        # Performance assertions
        assert success_rate >= 0.95, f\"Success rate too low: {success_rate:.2%}\"
        assert avg_duration < 1.0, f\"Average response time too high: {avg_duration:.3f}s\"
        assert requests_per_second > 10, f\"Request rate too low: {requests_per_second:.2f} req/s\"
    
    def test_upload_endpoint_load(self, http_session, test_config, sample_image_file, services_ready):
        \"\"\"Test upload endpoint under moderate load.\"\"\"
        url = f\"{test_config['backend_url']}/api/v1/upload\"
        
        # Smaller load for upload tests (more resource intensive)
        concurrent_requests = 5
        total_requests = 10
        
        def upload_file() -> Dict[str, Any]:
            start_time = time.time()
            try:
                with open(sample_image_file, 'rb') as f:
                    files = [('files', (sample_image_file.name, f, 'image/jpeg'))]
                    response = http_session.post(url, files=files, timeout=60)  # Longer timeout for uploads
                
                duration = time.time() - start_time
                
                return {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'duration': duration,
                    'error': None,
                    'response_size': len(response.content)
                }
            except Exception as e:
                duration = time.time() - start_time
                return {
                    'success': False,
                    'status_code': 0,
                    'duration': duration,
                    'error': str(e),
                    'response_size': 0
                }
        
        # Execute upload load test
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(upload_file) for _ in range(total_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        total_duration = time.time() - start_time
        
        # Analyze results
        successful_uploads = [r for r in results if r['success']]
        failed_uploads = [r for r in results if not r['success']]
        
        success_rate = len(successful_uploads) / len(results)
        avg_duration = statistics.mean([r['duration'] for r in successful_uploads]) if successful_uploads else 0
        
        uploads_per_second = len(results) / total_duration
        
        # Print performance metrics
        print(f\"\
Load Test Results (Upload Endpoint):\")
        print(f\"Total uploads: {len(results)}\")
        print(f\"Successful: {len(successful_uploads)} ({success_rate:.2%})\")
        print(f\"Failed: {len(failed_uploads)}\")
        print(f\"Uploads/second: {uploads_per_second:.2f}\")
        print(f\"Average upload time: {avg_duration:.3f}s\")
        
        # Performance assertions (more lenient for uploads)
        assert success_rate >= 0.8, f\"Success rate too low: {success_rate:.2%}\"
        assert avg_duration < 30.0, f\"Average upload time too high: {avg_duration:.3f}s\"
    
    def test_mixed_load_scenario(self, http_session, test_config, sample_image_file, services_ready):
        \"\"\"Test mixed load scenario with different endpoints.\"\"\"
        
        def health_check() -> Dict[str, Any]:
            start_time = time.time()
            try:
                response = http_session.get(f\"{test_config['backend_url']}/health\", timeout=10)
                return {
                    'endpoint': 'health',
                    'success': response.status_code == 200,
                    'duration': time.time() - start_time
                }
            except Exception as e:
                return {
                    'endpoint': 'health',
                    'success': False,
                    'duration': time.time() - start_time,
                    'error': str(e)
                }
        
        def metrics_check() -> Dict[str, Any]:
            start_time = time.time()
            try:
                response = http_session.get(f\"{test_config['backend_url']}/api/v1/health/metrics\", timeout=10)
                return {
                    'endpoint': 'metrics',
                    'success': response.status_code == 200,
                    'duration': time.time() - start_time
                }
            except Exception as e:
                return {
                    'endpoint': 'metrics',
                    'success': False,
                    'duration': time.time() - start_time,
                    'error': str(e)
                }
        
        def disk_usage_check() -> Dict[str, Any]:
            start_time = time.time()
            try:
                response = http_session.get(f\"{test_config['backend_url']}/api/v1/admin/disk-usage\", timeout=10)
                return {
                    'endpoint': 'disk-usage',
                    'success': response.status_code == 200,
                    'duration': time.time() - start_time
                }
            except Exception as e:
                return {
                    'endpoint': 'disk-usage',
                    'success': False,
                    'duration': time.time() - start_time,
                    'error': str(e)
                }
        
        # Mix of different request types
        tasks = [
            health_check,
            metrics_check,
            disk_usage_check,
        ] * 10  # 30 total requests, 10 of each type
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(task) for task in tasks]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        total_duration = time.time() - start_time
        
        # Analyze results by endpoint
        endpoint_stats = {}
        for result in results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'total': 0, 'successful': 0, 'durations': []}
            
            endpoint_stats[endpoint]['total'] += 1
            if result['success']:
                endpoint_stats[endpoint]['successful'] += 1
                endpoint_stats[endpoint]['durations'].append(result['duration'])
        
        print(f\"\
Mixed Load Test Results:\")
        print(f\"Total duration: {total_duration:.2f}s\")
        print(f\"Overall requests/second: {len(results) / total_duration:.2f}\")
        
        for endpoint, stats in endpoint_stats.items():
            success_rate = stats['successful'] / stats['total']
            avg_duration = statistics.mean(stats['durations']) if stats['durations'] else 0
            
            print(f\"  {endpoint}: {stats['successful']}/{stats['total']} ({success_rate:.2%}) avg: {avg_duration:.3f}s\")
            
            # Each endpoint should have reasonable performance
            assert success_rate >= 0.9, f\"{endpoint} success rate too low: {success_rate:.2%}\"
    
    def test_sustained_load(self, http_session, test_config, services_ready):
        \"\"\"Test sustained load over a longer period.\"\"\"
        url = f\"{test_config['backend_url']}/health\"
        
        duration_seconds = 60  # 1 minute sustained load
        requests_per_second = 5
        
        results = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        def make_request() -> Dict[str, Any]:
            request_start = time.time()
            try:
                response = http_session.get(url, timeout=5)
                return {
                    'success': response.status_code == 200,
                    'duration': time.time() - request_start,
                    'timestamp': request_start
                }
            except Exception as e:
                return {
                    'success': False,
                    'duration': time.time() - request_start,
                    'timestamp': request_start,
                    'error': str(e)
                }
        
        # Sustained load with controlled rate
        while time.time() < end_time:
            batch_start = time.time()
            
            # Submit batch of requests
            with ThreadPoolExecutor(max_workers=requests_per_second) as executor:
                futures = [executor.submit(make_request) for _ in range(requests_per_second)]
                
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
            
            # Wait until next second
            elapsed = time.time() - batch_start
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
        
        # Analyze sustained load results
        successful_requests = [r for r in results if r['success']]
        total_duration = time.time() - start_time
        
        success_rate = len(successful_requests) / len(results) if results else 0
        actual_rps = len(results) / total_duration
        avg_response_time = statistics.mean([r['duration'] for r in successful_requests]) if successful_requests else 0
        
        print(f\"\
Sustained Load Test Results:\")
        print(f\"Duration: {total_duration:.1f}s\")
        print(f\"Total requests: {len(results)}\")
        print(f\"Success rate: {success_rate:.2%}\")
        print(f\"Actual RPS: {actual_rps:.2f}\")
        print(f\"Average response time: {avg_response_time:.3f}s\")
        
        # Performance assertions for sustained load
        assert success_rate >= 0.95, f\"Success rate degraded under sustained load: {success_rate:.2%}\"
        assert avg_response_time < 2.0, f\"Response time degraded under sustained load: {avg_response_time:.3f}s\"
        assert actual_rps >= requests_per_second * 0.8, f\"Request rate too low: {actual_rps:.2f} vs target {requests_per_second}\"
    
    def test_memory_usage_stability(self, http_session, test_config, services_ready):
        \"\"\"Test memory usage stability during load.\"\"\"
        metrics_url = f\"{test_config['backend_url']}/api/v1/health/metrics\"
        health_url = f\"{test_config['backend_url']}/health\"
        
        # Collect baseline memory
        try:
            response = http_session.get(metrics_url, timeout=10)
            assert response.status_code == 200
            
            baseline_metrics = response.text
            baseline_memory = self._extract_memory_metric(baseline_metrics)
        except Exception:
            pytest.skip(\"Memory metrics not available\")
        
        # Generate load for 30 seconds
        load_duration = 30
        start_time = time.time()
        
        request_count = 0
        while time.time() - start_time < load_duration:
            try:
                http_session.get(health_url, timeout=5)
                request_count += 1
            except:
                pass
            time.sleep(0.1)  # 10 requests per second
        
        # Collect memory after load
        time.sleep(5)  # Allow for any cleanup
        
        response = http_session.get(metrics_url, timeout=10)
        assert response.status_code == 200
        
        final_metrics = response.text
        final_memory = self._extract_memory_metric(final_metrics)
        
        if baseline_memory and final_memory:
            memory_increase = final_memory - baseline_memory
            memory_increase_percent = (memory_increase / baseline_memory) * 100
            
            print(f\"\
Memory Stability Test:\")
            print(f\"Requests made: {request_count}\")
            print(f\"Baseline memory: {baseline_memory:.1f}%\")
            print(f\"Final memory: {final_memory:.1f}%\")
            print(f\"Memory increase: {memory_increase_percent:.1f}%\")
            
            # Memory increase should be reasonable
            assert memory_increase_percent < 20, f\"Memory usage increased too much: {memory_increase_percent:.1f}%\"
        else:
            print(\"Memory metrics not available, skipping memory stability check\")
    
    def _extract_memory_metric(self, metrics_text: str) -> float:
        \"\"\"Extract memory usage percentage from Prometheus metrics.\"\"\"
        for line in metrics_text.split('\
'):
            if line.startswith('system_memory_usage_percent '):
                try:
                    return float(line.split(' ')[1])
                except (IndexError, ValueError):
                    continue
        return None
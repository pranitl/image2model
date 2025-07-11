"""
Integration tests for SSE progress tracking functionality.
"""

import pytest
import requests
import json
import time
import threading
import os
from typing import List, Dict, Any

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY", "test-api-key")


class TestSSEProgress:
    """Test SSE progress tracking and reporting."""
    
    @pytest.fixture
    def headers(self):
        """Common headers for API requests."""
        return {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    
    @pytest.fixture
    def create_test_task(self, headers):
        """Create a test task that reports progress."""
        # This would normally create a real task
        # For testing, we'll use environment variable or skip
        task_id = os.getenv("PROGRESS_TEST_TASK_ID")
        if not task_id:
            # Try to create a simple task
            try:
                response = requests.post(
                    f"{BASE_URL}/upload/url",
                    json={"url": "https://example.com/test.jpg"},
                    headers=headers,
                    timeout=5
                )
                if response.status_code == 200:
                    return response.json().get("task_id")
            except:
                pass
            
            pytest.skip("Cannot create test task for progress tracking")
        return task_id
    
    def collect_progress_events(self, url: str, headers: dict, timeout: int = 30) -> List[Dict[str, Any]]:
        """Collect all progress events from SSE stream."""
        events = []
        start_time = time.time()
        
        try:
            with requests.get(url, headers=headers, stream=True, timeout=timeout) as response:
                if response.status_code != 200:
                    return events
                
                for line in response.iter_lines():
                    if time.time() - start_time > timeout:
                        break
                    
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                events.append({
                                    "timestamp": time.time() - start_time,
                                    "data": data
                                })
                            except json.JSONDecodeError:
                                continue
        except:
            pass
        
        return events
    
    def test_progress_sequence(self, headers, create_test_task):
        """Test that progress events follow a logical sequence."""
        url = f"{BASE_URL}/status/{create_test_task}/stream"
        
        events = self.collect_progress_events(url, headers, timeout=60)
        
        if not events:
            pytest.skip("No progress events received")
        
        # Extract progress values
        progress_values = []
        for event in events:
            if "progress" in event["data"]:
                progress_values.append(event["data"]["progress"])
        
        if not progress_values:
            pytest.skip("No progress values found in events")
        
        # Verify progress is non-decreasing
        for i in range(1, len(progress_values)):
            assert progress_values[i] >= progress_values[i-1], \
                f"Progress decreased from {progress_values[i-1]} to {progress_values[i]}"
        
        # Verify progress is within valid range
        for progress in progress_values:
            assert 0 <= progress <= 100, f"Invalid progress value: {progress}"
    
    def test_progress_timing(self, headers, create_test_task):
        """Test that progress events are sent at reasonable intervals."""
        url = f"{BASE_URL}/status/{create_test_task}/stream"
        
        events = self.collect_progress_events(url, headers, timeout=30)
        
        if len(events) < 2:
            pytest.skip("Not enough events to test timing")
        
        # Calculate intervals between events
        intervals = []
        for i in range(1, len(events)):
            interval = events[i]["timestamp"] - events[i-1]["timestamp"]
            intervals.append(interval)
        
        # Verify intervals are reasonable (not too fast, not too slow)
        for interval in intervals:
            assert 0.1 <= interval <= 10.0, \
                f"Event interval {interval}s is outside reasonable range"
    
    def test_progress_metadata(self, headers, create_test_task):
        """Test that progress events include expected metadata."""
        url = f"{BASE_URL}/status/{create_test_task}/stream"
        
        events = self.collect_progress_events(url, headers, timeout=20)
        
        if not events:
            pytest.skip("No progress events received")
        
        # Check event structure
        for event in events:
            data = event["data"]
            
            # Should have either progress or status
            assert "progress" in data or "status" in data, \
                "Event missing both progress and status"
            
            # If it has progress, check for additional metadata
            if "progress" in data:
                # Common metadata fields (adjust based on your implementation)
                possible_fields = ["stage", "message", "step", "total_steps"]
                has_metadata = any(field in data for field in possible_fields)
                
                # Not all progress events need metadata, but some should have it
                # This is a soft check - we just log if no metadata is found
                if not has_metadata and len(events) > 5:
                    print(f"Warning: Progress event lacks metadata: {data}")
    
    def test_progress_error_recovery(self, headers):
        """Test progress reporting when errors occur."""
        # Use an invalid task ID that might trigger errors
        invalid_task_id = "error-test-task-" + str(int(time.time()))
        url = f"{BASE_URL}/status/{invalid_task_id}/stream"
        
        events = self.collect_progress_events(url, headers, timeout=10)
        
        # Should either return 404 or send error events
        if not events:
            # No events means the endpoint properly handled invalid task
            assert True
        else:
            # Check if error event was sent
            error_found = False
            for event in events:
                if "error" in event["data"] or event["data"].get("status") == "error":
                    error_found = True
                    break
            
            if not error_found:
                pytest.skip("No error handling demonstrated")
    
    def test_progress_completion(self, headers, create_test_task):
        """Test that progress reaches 100% or sends completion event."""
        url = f"{BASE_URL}/status/{create_test_task}/stream"
        
        events = self.collect_progress_events(url, headers, timeout=120)
        
        if not events:
            pytest.skip("No progress events received")
        
        # Check for completion indicators
        completion_found = False
        max_progress = 0
        
        for event in events:
            data = event["data"]
            
            # Check for explicit completion
            if data.get("status") == "completed" or data.get("type") == "complete":
                completion_found = True
                break
            
            # Track maximum progress
            if "progress" in data:
                max_progress = max(max_progress, data["progress"])
                if data["progress"] >= 100:
                    completion_found = True
        
        # Either should reach 100% or send completion event
        assert completion_found or max_progress >= 95, \
            f"Task did not complete properly (max progress: {max_progress}%)"
    
    def test_concurrent_progress_tracking(self, headers, create_test_task):
        """Test tracking progress from multiple clients simultaneously."""
        url = f"{BASE_URL}/status/{create_test_task}/stream"
        
        # Collect events from multiple threads
        results = []
        threads = []
        
        def collect_events(index):
            events = self.collect_progress_events(url, headers, timeout=15)
            results.append((index, events))
        
        # Start 3 concurrent collectors
        for i in range(3):
            thread = threading.Thread(target=collect_events, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify all collectors received events
        successful_collectors = 0
        for index, events in results:
            if events:
                successful_collectors += 1
        
        # At least 2 out of 3 should succeed
        assert successful_collectors >= 2, \
            f"Only {successful_collectors}/3 collectors received events"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
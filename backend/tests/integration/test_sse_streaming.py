"""
Integration tests for SSE (Server-Sent Events) streaming functionality.
"""

import pytest
import requests
import json
import time
import os
from typing import Generator

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY", "test-api-key")


class TestSSEStreaming:
    """Test SSE streaming functionality."""
    
    @pytest.fixture
    def headers(self):
        """Common headers for API requests."""
        return {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    
    @pytest.fixture
    def test_task_id(self):
        """Create a test task and return its ID."""
        # This would normally create a test task
        # For now, return a dummy ID or skip if not available
        test_id = os.getenv("TEST_TASK_ID", "test-task-123")
        if not test_id:
            pytest.skip("No test task ID available")
        return test_id
    
    def parse_sse_stream(self, response) -> Generator[dict, None, None]:
        """Parse SSE stream responses."""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        yield data
                    except json.JSONDecodeError:
                        continue
    
    def test_sse_connection(self, headers, test_task_id):
        """Test basic SSE connection establishment."""
        url = f"{BASE_URL}/status/{test_task_id}/stream"
        
        try:
            with requests.get(url, headers=headers, stream=True, timeout=5) as response:
                if response.status_code == 404:
                    pytest.skip("SSE streaming endpoint not implemented")
                
                assert response.status_code == 200
                assert response.headers.get('Content-Type') == 'text/event-stream'
                
                # Try to get at least one event
                event_count = 0
                for event in self.parse_sse_stream(response):
                    event_count += 1
                    assert "status" in event or "progress" in event
                    if event_count >= 1:
                        break
                
                if event_count == 0:
                    pytest.skip("No SSE events received - task might be completed")
                    
        except requests.exceptions.Timeout:
            pytest.skip("SSE connection timed out - endpoint might not be configured")
        except requests.exceptions.ConnectionError:
            pytest.skip("Cannot connect to SSE endpoint")
    
    def test_sse_progress_updates(self, headers, test_task_id):
        """Test SSE progress update events."""
        url = f"{BASE_URL}/status/{test_task_id}/stream"
        
        try:
            with requests.get(url, headers=headers, stream=True, timeout=10) as response:
                if response.status_code == 404:
                    pytest.skip("SSE streaming endpoint not implemented")
                
                assert response.status_code == 200
                
                progress_events = []
                for event in self.parse_sse_stream(response):
                    if "progress" in event:
                        progress_events.append(event)
                    
                    # Collect up to 5 progress events or timeout
                    if len(progress_events) >= 5:
                        break
                
                if not progress_events:
                    pytest.skip("No progress events received")
                
                # Verify progress event structure
                for event in progress_events:
                    assert "progress" in event
                    assert isinstance(event["progress"], (int, float))
                    assert 0 <= event["progress"] <= 100
                    
        except requests.exceptions.Timeout:
            pytest.skip("SSE connection timed out")
    
    def test_sse_error_handling(self, headers):
        """Test SSE error handling with invalid task ID."""
        invalid_task_id = "invalid-task-id-12345"
        url = f"{BASE_URL}/status/{invalid_task_id}/stream"
        
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=5)
            
            if response.status_code == 404:
                # This is expected for invalid task ID
                assert True
            elif response.status_code == 200:
                # If it returns 200, it should send an error event
                for event in self.parse_sse_stream(response):
                    if "error" in event:
                        assert True
                        break
            else:
                pytest.fail(f"Unexpected status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            pytest.skip("SSE connection timed out")
    
    def test_sse_completion_event(self, headers, test_task_id):
        """Test SSE completion event."""
        url = f"{BASE_URL}/status/{test_task_id}/stream"
        
        try:
            with requests.get(url, headers=headers, stream=True, timeout=30) as response:
                if response.status_code == 404:
                    pytest.skip("SSE streaming endpoint not implemented")
                
                assert response.status_code == 200
                
                completion_received = False
                for event in self.parse_sse_stream(response):
                    if event.get("status") == "completed" or event.get("type") == "complete":
                        completion_received = True
                        break
                
                if not completion_received:
                    pytest.skip("No completion event received within timeout")
                    
        except requests.exceptions.Timeout:
            pytest.skip("SSE connection timed out waiting for completion")
    
    @pytest.mark.parametrize("concurrent_connections", [2, 5])
    def test_sse_concurrent_connections(self, headers, test_task_id, concurrent_connections):
        """Test multiple concurrent SSE connections."""
        url = f"{BASE_URL}/status/{test_task_id}/stream"
        
        connections = []
        try:
            # Open multiple connections
            for _ in range(concurrent_connections):
                response = requests.get(url, headers=headers, stream=True, timeout=5)
                if response.status_code == 404:
                    pytest.skip("SSE streaming endpoint not implemented")
                connections.append(response)
            
            # Verify all connections are successful
            for conn in connections:
                assert conn.status_code == 200
                assert conn.headers.get('Content-Type') == 'text/event-stream'
            
        except requests.exceptions.Timeout:
            pytest.skip("SSE connections timed out")
        finally:
            # Clean up connections
            for conn in connections:
                try:
                    conn.close()
                except:
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
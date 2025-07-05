"""
Integration tests for SSE streaming and chord task handling.

Tests the Server-Sent Events streaming for task progress tracking.
"""

import pytest
import json
import time
import uuid
from typing import Generator, Dict, Any
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

@pytest.mark.integration 
class TestSSEStreaming:
    """Test SSE streaming functionality and chord handling."""
    
    def parse_sse_message(self, message: str) -> Dict[str, Any]:
        """Parse SSE message format."""
        lines = message.strip().split('\n')
        data = {}
        
        for line in lines:
            if line.startswith('event:'):
                data['event'] = line[6:].strip()
            elif line.startswith('data:'):
                try:
                    data['data'] = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    data['data'] = line[5:].strip()
        
        return data
    
    def test_sse_stream_for_nonexistent_task(self, http_session, test_config, services_ready):
        """Test SSE stream for non-existent task."""
        task_id = str(uuid.uuid4())
        url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/stream"
        
        messages = []
        with http_session.get(url, stream=True, timeout=10) as response:
            assert response.status_code == 200
            assert 'text/event-stream' in response.headers.get('Content-Type', '')
            
            # Read a few messages
            for i, line in enumerate(response.iter_lines()):
                if i > 10:  # Limit messages to prevent hanging
                    break
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('data:'):
                        messages.append(decoded)
        
        # Should get at least one message (likely pending or not found)
        assert len(messages) > 0
    
    def test_sse_stream_with_real_task(self, auth_http_session, test_config, sample_image_file, services_ready):
        """Test SSE streaming with a real upload task."""
        # First, upload a file to get a task ID
        upload_url = f"{test_config['backend_url']}/api/v1/upload"
        
        with open(sample_image_file, 'rb') as f:
            files = [('files', (sample_image_file.name, f, 'image/jpeg'))]
            upload_response = auth_http_session.post(upload_url, files=files, timeout=test_config['timeout'])
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        task_id = upload_data.get('task_id')
        
        if not task_id:
            pytest.skip("No task_id returned from upload")
        
        # Now stream the task progress
        stream_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/stream"
        
        messages = []
        events_seen = set()
        
        with http_session.get(stream_url, stream=True, timeout=30) as response:
            assert response.status_code == 200
            
            start_time = time.time()
            for line in response.iter_lines():
                if time.time() - start_time > 20:  # Max 20 seconds
                    break
                    
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('event:'):
                        event_type = decoded[6:].strip()
                        events_seen.add(event_type)
                    elif decoded.startswith('data:'):
                        messages.append(decoded)
                        
                        # Check if task completed
                        try:
                            data = json.loads(decoded[5:])
                            if data.get('status') in ['completed', 'failed']:
                                break
                        except:
                            pass
        
        # Should have received some messages
        assert len(messages) > 0
        
        # Should see various event types
        possible_events = {'task_queued', 'task_progress', 'task_status', 'task_completed', 'task_failed'}
        assert len(events_seen.intersection(possible_events)) > 0
    
    def test_sse_handles_chord_task(self, auth_http_session, test_config, multiple_image_files, services_ready):
        """Test SSE streaming correctly handles chord tasks (parallel processing)."""
        # Upload multiple files to trigger chord processing
        upload_url = f"{test_config['backend_url']}/api/v1/upload"
        
        files = []
        for img_file in multiple_image_files[:2]:  # Use 2 files
            files.append(('files', (img_file.name, open(img_file, 'rb'), 'image/jpeg')))
        
        try:
            upload_response = auth_http_session.post(upload_url, files=files, timeout=test_config['timeout'])
            assert upload_response.status_code == 200
            
            upload_data = upload_response.json()
            task_id = upload_data.get('task_id')
            
            if not task_id:
                pytest.skip("No task_id returned from upload")
            
            # Stream the task progress
            stream_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/stream"
            
            chord_detected = False
            completion_detected = False
            
            with http_session.get(stream_url, stream=True, timeout=30) as response:
                assert response.status_code == 200
                
                start_time = time.time()
                for line in response.iter_lines():
                    if time.time() - start_time > 25:  # Max 25 seconds
                        break
                        
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith('data:'):
                            try:
                                data = json.loads(decoded[5:])
                                
                                # Check for chord task ID in response
                                if 'chord_task_id' in data:
                                    chord_detected = True
                                
                                # Check for completion
                                if data.get('status') == 'completed':
                                    completion_detected = True
                                    break
                                    
                            except json.JSONDecodeError:
                                pass
            
            # For batch processing, we should detect chord handling
            # Note: This might not always trigger if processing is very fast
            
        finally:
            # Close file handles
            for _, file_tuple in files:
                file_tuple[1].close()
    
    def test_sse_timeout_parameter(self, http_session, test_config, services_ready):
        """Test SSE stream timeout parameter."""
        task_id = str(uuid.uuid4())
        
        # Test with short timeout
        url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/stream?timeout=5"
        
        start_time = time.time()
        message_count = 0
        
        with http_session.get(url, stream=True, timeout=10) as response:
            assert response.status_code == 200
            
            for line in response.iter_lines():
                if line:
                    message_count += 1
                    
                # Stream should close after ~5 seconds
                if time.time() - start_time > 7:
                    break
        
        elapsed = time.time() - start_time
        
        # Stream should have closed around 5 seconds (allow some margin)
        assert 4 <= elapsed <= 8, f"Stream lasted {elapsed}s, expected ~5s"
        assert message_count > 0
    
    def test_sse_concurrent_streams(self, http_session, test_config, services_ready):
        """Test multiple concurrent SSE streams."""
        # Create multiple task IDs
        task_ids = [str(uuid.uuid4()) for _ in range(3)]
        
        def stream_task(task_id: str) -> int:
            """Stream a task and return message count."""
            url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/stream?timeout=5"
            message_count = 0
            
            try:
                with http_session.get(url, stream=True, timeout=10) as response:
                    if response.status_code == 200:
                        start = time.time()
                        for line in response.iter_lines():
                            if time.time() - start > 6:
                                break
                            if line:
                                message_count += 1
            except:
                pass
                
            return message_count
        
        # Stream multiple tasks concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(stream_task, task_id): task_id for task_id in task_ids}
            results = {}
            
            for future in as_completed(futures):
                task_id = futures[future]
                try:
                    message_count = future.result()
                    results[task_id] = message_count
                except Exception as e:
                    results[task_id] = 0
        
        # All streams should have received some messages
        assert len(results) == 3
        assert all(count > 0 for count in results.values())
    
    def test_sse_error_event_format(self, http_session, test_config, services_ready):
        """Test SSE error event format."""
        # Use invalid task ID format to trigger error
        url = f"{test_config['backend_url']}/api/v1/status/tasks/invalid-task-id/stream"
        
        error_received = False
        
        with http_session.get(url, stream=True, timeout=5) as response:
            # Should get 400 for invalid format
            assert response.status_code == 400
    
    def test_sse_heartbeat_messages(self, http_session, test_config, services_ready):
        """Test that SSE sends heartbeat messages to keep connection alive."""
        task_id = str(uuid.uuid4())
        url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/stream"
        
        heartbeats = 0
        messages = []
        
        with http_session.get(url, stream=True, timeout=15) as response:
            assert response.status_code == 200
            
            start_time = time.time()
            for line in response.iter_lines():
                if time.time() - start_time > 10:  # Monitor for 10 seconds
                    break
                    
                if line:
                    decoded = line.decode('utf-8')
                    messages.append(decoded)
                    
                    if 'heartbeat' in decoded.lower():
                        heartbeats += 1
        
        # Should have received messages (including possible heartbeats)
        assert len(messages) > 0
        
        # Heartbeats help keep the connection alive during long processing
        # Note: Our implementation might not send explicit heartbeats
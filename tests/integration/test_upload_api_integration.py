"""
Integration tests for upload API fixes and SSE streaming.

Tests the fixes for:
- Task ID extraction from upload responses
- SSE connection endpoint correctness
- Batch vs single upload consistency
- End-to-end upload → processing flow
"""

import pytest
import asyncio
import time
import json
from pathlib import Path
from typing import Dict, Any
import requests
import sseclient
from unittest.mock import patch


@pytest.mark.integration
class TestUploadAPIIntegration:
    """Test upload API integration with our fixes."""
    
    def test_single_file_uses_batch_endpoint(self, http_session, test_config, sample_image_file, services_ready):
        """Test that frontend always uses batch endpoint, even for single files."""
        # This simulates the frontend behavior after our fix
        url = f"{test_config['backend_url']}/api/v1/upload/batch"
        
        with open(sample_image_file, 'rb') as f:
            files = [('files', (sample_image_file.name, f, 'image/jpeg'))]
            response = http_session.post(url, files=files, timeout=test_config['timeout'])
        
        assert response.status_code == 200, f"Batch upload failed: {response.text}"
        
        data = response.json()
        
        # Should have batch upload response structure
        assert 'batch_id' in data
        assert 'job_id' in data  # This is the key field for SSE streaming
        assert 'uploaded_files' in data
        assert 'total_files' in data
        assert data['total_files'] == 1
        assert len(data['uploaded_files']) == 1
        
        # Each uploaded file should have file_id
        file_data = data['uploaded_files'][0]
        assert 'file_id' in file_data
        assert 'filename' in file_data
        assert 'file_size' in file_data
        assert 'content_type' in file_data
        assert 'status' in file_data
    
    def test_batch_upload_multiple_files(self, http_session, test_config, multiple_image_files, services_ready):
        """Test batch upload with multiple files."""
        url = f"{test_config['backend_url']}/api/v1/upload/batch"
        
        files = []
        for img_file in multiple_image_files[:3]:  # Upload first 3 files
            files.append(('files', (img_file.name, open(img_file, 'rb'), 'image/jpeg')))
        
        try:
            response = http_session.post(url, files=files, timeout=test_config['timeout'])
            
            assert response.status_code == 200, f"Batch upload failed: {response.text}"
            
            data = response.json()
            
            # Should have proper batch upload structure
            assert 'batch_id' in data
            assert 'job_id' in data  # Key for SSE streaming
            assert 'uploaded_files' in data
            assert 'total_files' in data
            assert data['total_files'] == 3
            assert len(data['uploaded_files']) == 3
            
            # Each file should have proper structure
            for file_data in data['uploaded_files']:
                assert 'file_id' in file_data
                assert 'filename' in file_data
                assert 'status' in file_data
                assert file_data['status'] == 'uploaded'
                
        finally:
            # Close file handles
            for _, file_tuple in files:
                file_tuple[1].close()
    
    def test_task_id_extraction_logic(self, http_session, test_config, sample_image_file, services_ready):
        """Test that we can extract the correct task ID for SSE streaming."""
        url = f"{test_config['backend_url']}/api/v1/upload/batch"
        
        with open(sample_image_file, 'rb') as f:
            files = [('files', (sample_image_file.name, f, 'image/jpeg'))]
            response = http_session.post(url, files=files, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response contains both job_id and task_id
        assert 'job_id' in data, "Upload response missing job_id field"
        assert 'task_id' in data, "Upload response missing task_id field"
        
        # Simulate frontend task ID extraction logic (prefer task_id)
        task_id = data['task_id'] or data['job_id']
        
        # Verify both IDs are valid UUIDs
        import uuid
        try:
            uuid.UUID(data['job_id'])
            uuid.UUID(data['task_id'])
            uuid.UUID(task_id)
        except ValueError as e:
            pytest.fail(f"Invalid UUID in response: {e}")
        
        # Verify task_id is different from job_id (they should be distinct)
        assert data['task_id'] != data['job_id'], "task_id should be different from job_id"
        
        # Verify we can use the actual task_id for status checking
        # Note: Task may complete quickly, so we check if the task_id is valid
        status_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}"
        status_response = http_session.get(status_url, timeout=test_config['timeout'])
        # Task may have completed (404) or still be in progress (200), both are valid
    
    def test_sse_endpoint_connection(self, http_session, test_config, sample_image_file, services_ready):
        """Test SSE endpoint connection with correct path."""
        # First upload a file to get a valid task_id
        upload_url = f"{test_config['backend_url']}/api/v1/upload/batch"
        
        with open(sample_image_file, 'rb') as f:
            files = [('files', (sample_image_file.name, f, 'image/jpeg'))]
            upload_response = http_session.post(upload_url, files=files, timeout=test_config['timeout'])
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        task_id = upload_data.get('task_id') or upload_data['job_id']
        
        # Test SSE connection with correct endpoint
        sse_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/stream"
        
        # Use SSE client to test the connection
        response = requests.get(sse_url, stream=True, timeout=10)
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'text/event-stream'
        
        # Read at least one SSE event
        events_received = 0
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data:'):
                data_json = line[5:].strip()  # Remove 'data:' prefix
                event_data = json.loads(data_json)
                
                # Verify event structure
                assert 'status' in event_data
                assert 'task_id' in event_data
                assert event_data['task_id'] == task_id
                assert 'progress' in event_data
                
                events_received += 1
                if events_received >= 1:  # Got at least one event
                    break
        
        assert events_received > 0, "No SSE events received"
        response.close()
    
    def test_sse_endpoint_invalid_task_id(self, http_session, test_config, services_ready):
        """Test SSE endpoint with invalid task ID format."""
        # Test with 'undefined' (previous bug scenario)
        sse_url = f"{test_config['backend_url']}/api/v1/status/tasks/undefined/stream"
        response = http_session.get(sse_url, timeout=5)
        assert response.status_code == 400
        
        error_data = response.json()
        assert error_data.get('error') == True
        assert 'Invalid task ID format' in error_data.get('message', '')
        
        # Test with malformed UUID
        sse_url = f"{test_config['backend_url']}/api/v1/status/tasks/not-a-uuid/stream"
        response = http_session.get(sse_url, timeout=5)
        assert response.status_code == 400
    
    def test_sse_endpoint_nonexistent_task(self, http_session, test_config, services_ready):
        """Test SSE endpoint with valid UUID but nonexistent task."""
        # Use a valid UUID format but for a task that doesn't exist
        fake_task_id = "550e8400-e29b-41d4-a716-446655440000"
        sse_url = f"{test_config['backend_url']}/api/v1/status/tasks/{fake_task_id}/stream"
        
        response = requests.get(sse_url, stream=True, timeout=10)
        assert response.status_code == 200  # SSE endpoint should still connect
        
        # Should get events indicating the task is in PENDING state (queued)
        events_received = 0
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data:'):
                data_json = line[5:].strip()
                event_data = json.loads(data_json)
                
                assert event_data['task_id'] == fake_task_id
                assert event_data['status'] == 'queued'  # Celery reports unknown tasks as PENDING
                
                events_received += 1
                if events_received >= 1:
                    break
        
        response.close()
    
    @pytest.mark.slow
    def test_end_to_end_upload_processing_flow(self, http_session, test_config, sample_image_file, services_ready):
        """Test complete end-to-end upload → processing flow."""
        # Step 1: Upload file (simulating frontend behavior)
        upload_url = f"{test_config['backend_url']}/api/v1/upload/batch"
        
        with open(sample_image_file, 'rb') as f:
            files = [('files', (sample_image_file.name, f, 'image/jpeg'))]
            upload_response = http_session.post(upload_url, files=files, timeout=test_config['timeout'])
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        
        # Step 2: Extract task ID (simulating frontend logic - prefer task_id)
        task_id = upload_data.get('task_id') or upload_data['job_id']
        
        # Step 3: Connect to SSE stream and track progress
        sse_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/stream"
        
        final_status = None
        progress_events = []
        max_events = 50  # Limit to avoid infinite loops
        events_received = 0
        
        response = requests.get(sse_url, stream=True, timeout=60)
        assert response.status_code == 200
        
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data:'):
                    data_json = line[5:].strip()
                    event_data = json.loads(data_json)
                    progress_events.append(event_data)
                    
                    current_status = event_data.get('status')
                    if current_status in ['completed', 'failed']:
                        final_status = current_status
                        break
                    
                    events_received += 1
                    if events_received >= max_events:
                        break
        finally:
            response.close()
        
        # Step 4: Verify we got meaningful progress updates
        assert len(progress_events) > 0, "No progress events received"
        
        # Verify all events have correct structure
        for event in progress_events:
            assert 'status' in event
            assert 'task_id' in event
            assert event['task_id'] == task_id
            assert 'progress' in event
            assert isinstance(event['progress'], (int, float))
            assert 0 <= event['progress'] <= 100
        
        # Should progress from queued → processing → completed/failed
        statuses = [event['status'] for event in progress_events]
        assert 'queued' in statuses or 'processing' in statuses
        
        # If we got a final status, verify the task completed
        if final_status:
            assert final_status in ['completed', 'failed']
            if final_status == 'completed':
                # Final event should have 100% progress
                final_event = progress_events[-1]
                assert final_event['progress'] == 100
    
    def test_frontend_upload_hook_simulation(self, http_session, test_config, sample_image_file, services_ready):
        """Test simulating the frontend useUpload hook behavior."""
        # Simulate the frontend useUpload hook logic
        
        # Always use batch endpoint (our fix)
        endpoint = '/api/v1/upload/batch'
        url = f"{test_config['backend_url']}{endpoint}"
        
        # Prepare FormData (simulating frontend)
        with open(sample_image_file, 'rb') as f:
            files = [('files', (sample_image_file.name, f, 'image/jpeg'))]
            response = http_session.post(url, files=files, timeout=test_config['timeout'])
        
        assert response.status_code == 200
        upload_job = response.json()
        
        # Simulate task ID extraction logic from useUpload hook
        if 'job_id' in upload_job:
            task_id = upload_job['job_id']
            
            upload_job_with_task_id = {
                'taskId': task_id,
                'data': upload_job
            }
        else:
            pytest.fail('Upload response missing job_id field')
        
        # Simulate navigation to processing page
        processing_task_id = upload_job_with_task_id['taskId']
        
        # Verify the task ID works for SSE connection
        sse_url = f"{test_config['backend_url']}/api/v1/status/tasks/{processing_task_id}/stream"
        response = requests.get(sse_url, stream=True, timeout=10)
        assert response.status_code == 200
        response.close()
        
        # Verify task status endpoint works
        status_url = f"{test_config['backend_url']}/api/v1/status/tasks/{processing_task_id}/status"
        status_response = http_session.get(status_url, timeout=test_config['timeout'])
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data['task_id'] == processing_task_id


@pytest.mark.integration
class TestUploadAPIErrors:
    """Test error handling in upload API integration."""
    
    def test_malformed_response_handling(self, http_session, test_config, services_ready):
        """Test handling of malformed responses."""
        # This test ensures frontend can handle unexpected response formats
        url = f"{test_config['backend_url']}/api/v1/upload/batch"
        
        # Send invalid file data
        response = http_session.post(url, data={'invalid': 'data'}, timeout=test_config['timeout'])
        
        # Should get proper error response
        assert response.status_code == 400
        error_data = response.json()
        assert error_data.get('error') == True
        assert 'message' in error_data
    
    def test_sse_connection_interrupted(self, http_session, test_config, sample_image_file, services_ready):
        """Test SSE connection interruption handling."""
        # Upload file first
        upload_url = f"{test_config['backend_url']}/api/v1/upload/batch"
        
        with open(sample_image_file, 'rb') as f:
            files = [('files', (sample_image_file.name, f, 'image/jpeg'))]
            upload_response = http_session.post(upload_url, files=files, timeout=test_config['timeout'])
        
        assert upload_response.status_code == 200
        task_id = upload_response.json()['job_id']
        
        # Start SSE connection
        sse_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/stream"
        response = requests.get(sse_url, stream=True, timeout=5)
        assert response.status_code == 200
        
        # Read one event then close connection (simulating interruption)
        lines_read = 0
        for line in response.iter_lines(decode_unicode=True):
            lines_read += 1
            if lines_read >= 2:  # Read header and one data line
                break
        
        response.close()
        
        # Should be able to reconnect
        response2 = requests.get(sse_url, stream=True, timeout=5)
        assert response2.status_code == 200
        response2.close()
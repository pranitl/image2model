"""
Tests for SSE progress streaming with chord task tracking.
"""
import pytest
import json
import time


class TestSSEProgress:
    """Test SSE progress updates for batch processing."""
    
    @pytest.mark.integration
    def test_sse_progress_includes_file_counts(self, auth_http_session, test_config, multiple_image_files, services_ready, monkeypatch):
        """Test that SSE progress updates include file count information."""
        # Mock FAL.AI client
        import sys
        if 'app.workers.fal_client' in sys.modules:
            del sys.modules['app.workers.fal_client']
        
        from tests.mocks.fal_mock import create_fal_mock
        fal_mocks = create_fal_mock(success=True, progress_updates=True)
        
        import types
        mock_fal = types.ModuleType('fal_client')
        mock_fal.upload_file = fal_mocks['upload_file']
        mock_fal.subscribe = fal_mocks['subscribe']
        
        monkeypatch.setitem(sys.modules, 'fal_client', mock_fal)
        
        # Upload batch
        upload_url = f"{test_config['backend_url']}/api/v1/upload/"
        files = []
        for img_file in multiple_image_files[:2]:  # Upload 2 files
            with open(img_file, 'rb') as f:
                files.append(('files', (img_file.name, f.read())))
        
        files_data = [('files', (f'test_{i}.jpg', content, 'image/jpeg')) 
                      for i, (_, (_, content)) in enumerate(files)]
        
        upload_response = auth_http_session.post(upload_url, files=files_data, timeout=test_config['timeout'])
        assert upload_response.status_code == 200
        
        upload_data = upload_response.json()
        task_id = upload_data['task_id']
        job_id = upload_data['job_id']
        expected_files = 2
        
        # Track SSE events
        sse_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/stream"
        headers = auth_http_session.headers.copy()
        headers['Accept'] = 'text/event-stream'
        
        progress_events = []
        chord_detected = False
        file_count_seen = False
        
        with auth_http_session.get(sse_url, headers=headers, stream=True, timeout=30) as response:
            start_time = time.time()
            
            for line in response.iter_lines():
                if time.time() - start_time > 20:  # 20 second timeout
                    break
                    
                if not line:
                    continue
                    
                line = line.decode('utf-8')
                
                # Parse SSE format
                event_type = None
                if line.startswith('event:'):
                    event_type = line.split(':', 1)[1].strip()
                elif line.startswith('data:'):
                    data_str = line.split(':', 1)[1].strip()
                    try:
                        data = json.loads(data_str)
                        if event_type:
                            progress_events.append((event_type, data))
                        else:
                            progress_events.append(('message', data))
                    
                        # Check for chord detection
                        if data.get('chord_task_id'):
                            chord_detected = True
                            # After chord detection, file count should be included
                            assert data.get('total_files') == expected_files or data.get('total') == expected_files, \
                                f"File count missing after chord detection: {data}"
                            file_count_seen = True
                    
                        # Check progress events have file information
                        if event_type == 'task_progress' and data.get('status') == 'processing':
                            # Should have either total_files or total field
                            if 'total_files' in data or 'total' in data:
                                file_count = data.get('total_files', data.get('total', 0))
                                assert file_count == expected_files, \
                                    f"Incorrect file count in progress: expected {expected_files}, got {file_count}"
                                file_count_seen = True
                        
                        # Stop on completion
                        if event_type == 'task_completed' or data.get('status') == 'completed':
                            break
                            
                    except json.JSONDecodeError:
                        continue
        
        # Verify expectations
        assert chord_detected, "Chord task was not detected in SSE stream"
        assert file_count_seen, "File count information was not seen in SSE events"
        assert len(progress_events) > 0, "No progress events were received"
        
        # Check final results
        time.sleep(1)  # Allow time for results storage
        download_url = f"{test_config['backend_url']}/api/v1/download/{job_id}/all"
        download_response = auth_http_session.get(download_url, timeout=test_config['timeout'])
        
        if download_response.status_code == 200:
            result_data = download_response.json()
            assert result_data['total_files'] == expected_files, \
                f"Final result file count mismatch: expected {expected_files}, got {result_data['total_files']}"
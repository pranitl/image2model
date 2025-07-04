"""
Integration tests for the core upload workflow.

Tests the complete upload process from file validation to task creation.
"""

import pytest
import asyncio
import time
from pathlib import Path
from typing import Dict, Any
import requests

@pytest.mark.integration
class TestUploadWorkflow:
    """Test complete upload workflow integration."""
    
    def test_single_image_upload_success(self, auth_http_session, test_config, sample_image_file, services_ready):
        """Test successful single image upload (using single file endpoint)."""
        url = f"{test_config['backend_url']}/api/v1/upload/image"
        
        with open(sample_image_file, 'rb') as f:
            files = {'file': (sample_image_file.name, f, 'image/jpeg')}
            response = auth_http_session.post(url, files=files, timeout=test_config['timeout'])
        
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        data = response.json()
        # Single file upload returns file_id (not job_id/task_id)
        assert 'file_id' in data
        assert 'filename' in data
        assert 'file_size' in data
        assert 'content_type' in data
        assert 'status' in data
        assert data['status'] == 'uploaded'
    
    def test_batch_upload_success(self, auth_http_session, test_config, multiple_image_files, services_ready):
        """Test successful batch upload."""
        url = f"{test_config['backend_url']}/api/v1/upload"
        
        files = []
        for img_file in multiple_image_files[:3]:  # Upload first 3 files
            files.append(('files', (img_file.name, open(img_file, 'rb'), 'image/jpeg')))
        
        try:
            response = auth_http_session.post(url, files=files, timeout=test_config['timeout'])
            
            assert response.status_code == 200, f"Batch upload failed: {response.text}"
            
            data = response.json()
            assert 'batch_id' in data
            assert 'job_id' in data  # Unique job identifier for results
            assert 'task_id' in data  # Celery task ID for tracking
            assert 'uploaded_files' in data
            assert 'total_files' in data
            assert data['total_files'] == 3
            assert len(data['uploaded_files']) == 3
            
            # Verify each uploaded file has required fields
            for file_data in data['uploaded_files']:
                assert 'file_id' in file_data
                assert 'filename' in file_data
                assert 'status' in file_data
                assert file_data['status'] == 'uploaded'
                
        finally:
            # Close file handles
            for _, file_tuple in files:
                file_tuple[1].close()
    
    def test_upload_file_validation_errors(self, auth_http_session, test_config, invalid_file, services_ready):
        """Test file validation error handling."""
        url = f"{test_config['backend_url']}/api/v1/upload/image"
        
        with open(invalid_file, 'rb') as f:
            files = {'file': (invalid_file.name, f, 'text/plain')}
            response = auth_http_session.post(url, files=files, timeout=test_config['timeout'])
        
        assert response.status_code == 400
        
        error_data = response.json()
        assert error_data.get('error') == True
        assert 'FILE_VALIDATION_ERROR' in error_data.get('error_code', '')
        assert 'message' in error_data
    
    def test_upload_large_file_handling(self, auth_http_session, test_config, large_image_file, services_ready):
        """Test handling of large files."""
        url = f"{test_config['backend_url']}/api/v1/upload/image"
        
        with open(large_image_file, 'rb') as f:
            files = {'file': (large_image_file.name, f, 'image/jpeg')}
            
            # This might succeed or fail depending on file size limits
            # We're testing that it handles the large file gracefully
            try:
                response = auth_http_session.post(url, files=files, timeout=60)  # Longer timeout for large file
                
                if response.status_code == 200:
                    # Large file was accepted
                    data = response.json()
                    assert 'job_id' in data
                    assert 'task_id' in data
                elif response.status_code == 400:
                    # Large file was rejected (expected for files > 10MB)
                    error_data = response.json()
                    assert error_data.get('error') == True
                    assert 'too large' in error_data.get('message', '').lower()
                else:
                    pytest.fail(f"Unexpected status code: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                # Timeout is acceptable for very large files
                pass
    
    def test_upload_missing_file(self, auth_http_session, test_config, services_ready):
        """Test upload with missing file parameter."""
        url = f"{test_config['backend_url']}/api/v1/upload/image"
        
        # Send request without file
        response = auth_http_session.post(url, timeout=test_config['timeout'])
        
        assert response.status_code == 400
        error_data = response.json()
        assert error_data.get('error') == True
    
    def test_upload_empty_file(self, auth_http_session, test_config, temp_dir, services_ready):
        """Test upload with empty file."""
        url = f"{test_config['backend_url']}/api/v1/upload/image"
        
        # Create empty file
        empty_file = temp_dir / "empty.jpg"
        empty_file.touch()
        
        with open(empty_file, 'rb') as f:
            files = {'file': (empty_file.name, f, 'image/jpeg')}
            response = auth_http_session.post(url, files=files, timeout=test_config['timeout'])
        
        assert response.status_code == 400
        error_data = response.json()
        assert error_data.get('error') == True
    
    def test_batch_upload_size_limit(self, auth_http_session, test_config, multiple_image_files, services_ready):
        """Test batch upload with too many files."""
        url = f"{test_config['backend_url']}/api/v1/upload"
        
        # Try to upload more than 25 files (simulate with same files repeated)
        files = []
        for i in range(26):  # Try to upload 26 files (over the limit)
            img_file = multiple_image_files[i % len(multiple_image_files)]
            files.append(('files', (f"{i}_{img_file.name}", open(img_file, 'rb'), 'image/jpeg')))
        
        try:
            response = auth_http_session.post(url, files=files, timeout=test_config['timeout'])
            
            # Should return error for too many files
            assert response.status_code == 400
            error_data = response.json()
            assert error_data.get('error') == True
            assert 'too many files' in error_data.get('message', '').lower()
            
        finally:
            # Close file handles
            for _, file_tuple in files:
                file_tuple[1].close()
    
    @pytest.mark.slow
    def test_upload_and_task_tracking(self, auth_http_session, test_config, sample_image_file, services_ready, monkeypatch):
        """Test complete upload and task tracking workflow using batch endpoint."""
        # Import the modules we need to mock
        import sys
        if 'app.workers.fal_client' in sys.modules:
            del sys.modules['app.workers.fal_client']
        
        from tests.mocks.fal_mock import create_fal_mock
        
        # Create FAL.AI mock that simulates successful processing
        fal_mocks = create_fal_mock(success=True, progress_updates=True)
        
        # Create a mock fal_client module
        import types
        mock_fal = types.ModuleType('fal_client')
        mock_fal.upload_file = fal_mocks['upload_file']
        mock_fal.subscribe = fal_mocks['subscribe']
        
        # Patch the import in sys.modules
        monkeypatch.setitem(sys.modules, 'fal_client', mock_fal)
        
        try:
            # Use batch upload for proper task tracking (matches frontend behavior)
            upload_url = f"{test_config['backend_url']}/api/v1/upload/"
            
            with open(sample_image_file, 'rb') as f:
                files = [('files', (sample_image_file.name, f, 'image/jpeg'))]
                upload_response = auth_http_session.post(upload_url, files=files, timeout=test_config['timeout'])
            
            assert upload_response.status_code == 200
            upload_data = upload_response.json()
            task_id = upload_data['task_id']  # Use task_id for status tracking
            job_id = upload_data['job_id']  # Use job_id for download
            
            # Track task progress
            status_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/status"
            
            max_attempts = 20  # More attempts for mocked processing
            attempt = 0
            final_status = None
            chord_complete = False
            
            while attempt < max_attempts:
                status_response = auth_http_session.get(status_url, timeout=test_config['timeout'])
                assert status_response.status_code == 200
                
                status_data = status_response.json()
                current_status = status_data.get('status')
                
                # Print status for debugging
                print(f"Attempt {attempt + 1}: Status = {current_status}, Data = {status_data}")
                
                # Check if this is a chord task that needs more tracking
                if current_status == 'completed' and status_data.get('result', {}).get('chord_task_id') and not chord_complete:
                    # This is a batch task that started a chord - wait for chord to complete
                    chord_id = status_data['result']['chord_task_id']
                    print(f"Main task completed, waiting for chord {chord_id} to complete...")
                    
                    # Check chord status
                    chord_url = f"{test_config['backend_url']}/api/v1/status/tasks/{chord_id}/status"
                    chord_response = auth_http_session.get(chord_url, timeout=test_config['timeout'])
                    
                    if chord_response.status_code == 200:
                        chord_data = chord_response.json()
                        chord_status = chord_data.get('status')
                        print(f"Chord status: {chord_status}")
                        
                        if chord_status == 'completed':
                            chord_complete = True
                            final_status = 'completed'
                            break
                        elif chord_status == 'failed':
                            final_status = 'failed'
                            break
                    
                    # Continue waiting for chord
                    current_status = 'processing'
                elif current_status == 'completed' and chord_complete:
                    final_status = 'completed'
                    break
                elif current_status == 'failed':
                    final_status = 'failed'
                    break
                
                attempt += 1
                time.sleep(2)  # Shorter wait for mocked processing
            
            # Verify we got a final status
            assert final_status is not None, "Task did not complete within expected time"
            assert final_status == 'completed', f"Task failed with status: {final_status}"
            
            # If completed successfully, check if we can download results
            if final_status == 'completed':
                # Small delay to ensure results are stored
                time.sleep(1)
                download_url = f"{test_config['backend_url']}/api/v1/download/{job_id}/all"
                download_response = auth_http_session.get(download_url, timeout=test_config['timeout'])
                
                # Should return list of available files
                assert download_response.status_code == 200, f"Download failed: {download_response.text}"
                
                # Verify response contains expected data
                download_data = download_response.json()
                assert 'files' in download_data
                assert len(download_data['files']) > 0
                
                # Verify file has expected fields
                file_info = download_data['files'][0]
                assert 'filename' in file_info
                assert 'model_url' in file_info
                assert file_info['model_url'].startswith('https://v3.fal.media/')  # Mock URL
                
        finally:
            # Clean up the mock
            if 'fal_client' in sys.modules:
                del sys.modules['fal_client']
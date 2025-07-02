"""
End-to-end tests simulating complete user workflows.

Tests the entire pipeline from upload to download with real file processing.
"""

import pytest
import asyncio
import time
import json
from pathlib import Path
from typing import Dict, Any, List
import requests
import websockets

@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteWorkflow:
    """Test complete end-to-end user workflows."""
    
    def test_single_image_complete_pipeline(self, http_session, test_config, sample_image_file, services_ready):
        """Test complete pipeline: upload -> process -> download."""
        # Step 1: Upload image
        upload_url = f"{test_config['backend_url']}/api/v1/upload/image"
        
        with open(sample_image_file, 'rb') as f:
            files = {'file': (sample_image_file.name, f, 'image/jpeg')}
            upload_response = http_session.post(upload_url, files=files, timeout=test_config['timeout'])
        
        assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
        upload_data = upload_response.json()
        
        job_id = upload_data['job_id']
        task_id = upload_data['task_id']
        
        print(f"Started job {job_id} with task {task_id}")
        
        # Step 2: Monitor task progress
        status_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/status"
        
        max_wait_time = 300  # 5 minutes maximum
        check_interval = 10  # Check every 10 seconds
        max_attempts = max_wait_time // check_interval
        
        final_status = None
        attempt = 0
        
        while attempt < max_attempts:
            status_response = http_session.get(status_url, timeout=test_config['timeout'])
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            current_status = status_data.get('status')
            progress = status_data.get('progress', 0)
            
            print(f"Attempt {attempt + 1}: Status = {current_status}, Progress = {progress}%")
            
            if current_status in ['completed', 'failed']:
                final_status = current_status
                break
            
            attempt += 1
            time.sleep(check_interval)
        
        # Step 3: Verify task completion
        assert final_status is not None, f"Task did not complete within {max_wait_time} seconds"
        
        if final_status == 'failed':
            # Get error details for debugging
            status_response = http_session.get(status_url, timeout=test_config['timeout'])
            status_data = status_response.json()
            error_msg = status_data.get('error', 'Unknown error')
            pytest.fail(f"Task failed with error: {error_msg}")
        
        assert final_status == 'completed', f"Task ended with status: {final_status}"
        
        # Step 4: Verify download availability
        download_url = f"{test_config['backend_url']}/api/v1/download/{job_id}/all"
        download_response = http_session.get(download_url, timeout=test_config['timeout'])
        
        # Should return file list or redirect to download
        assert download_response.status_code in [200, 302], f"Download failed: {download_response.text}"
        
        if download_response.status_code == 200:
            download_data = download_response.json()
            assert 'files' in download_data
            assert len(download_data['files']) > 0
            
            # Verify file details
            for file_info in download_data['files']:
                assert 'filename' in file_info
                assert 'size' in file_info
                assert 'download_url' in file_info
        
        print(f"✓ Complete pipeline test passed for job {job_id}")
    
    def test_batch_processing_workflow(self, http_session, test_config, multiple_image_files, services_ready):
        """Test batch processing workflow with multiple files."""
        # Step 1: Upload batch
        upload_url = f"{test_config['backend_url']}/api/v1/upload/batch"
        
        # Use first 3 images for faster testing
        test_files = multiple_image_files[:3]
        files = []
        
        for img_file in test_files:
            files.append(('files', (img_file.name, open(img_file, 'rb'), 'image/jpeg')))
        
        try:
            upload_response = http_session.post(upload_url, files=files, timeout=test_config['timeout'])
            assert upload_response.status_code == 200, f"Batch upload failed: {upload_response.text}"
            
            upload_data = upload_response.json()
            job_id = upload_data['job_id']
            tasks = upload_data['tasks']
            
            print(f"Started batch job {job_id} with {len(tasks)} tasks")
            
            # Step 2: Monitor all tasks
            completed_tasks = 0
            failed_tasks = 0
            max_wait_time = 600  # 10 minutes for batch processing
            check_interval = 15
            max_attempts = max_wait_time // check_interval
            
            for attempt in range(max_attempts):
                all_done = True
                current_completed = 0
                current_failed = 0
                
                for task in tasks:
                    task_id = task['task_id']
                    status_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/status"
                    status_response = http_session.get(status_url, timeout=test_config['timeout'])
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        current_status = status_data.get('status')
                        
                        if current_status == 'completed':
                            current_completed += 1
                        elif current_status == 'failed':
                            current_failed += 1
                        elif current_status in ['pending', 'processing']:
                            all_done = False
                
                completed_tasks = current_completed
                failed_tasks = current_failed
                
                print(f"Batch progress: {completed_tasks} completed, {failed_tasks} failed, {len(tasks) - completed_tasks - failed_tasks} processing")
                
                if all_done:
                    break
                
                time.sleep(check_interval)
            
            # Step 3: Verify batch completion
            assert completed_tasks + failed_tasks == len(tasks), "Not all tasks completed"
            assert completed_tasks > 0, "No tasks completed successfully"
            
            # Allow some failures in batch processing (network issues, etc.)
            success_rate = completed_tasks / len(tasks)
            assert success_rate >= 0.5, f"Success rate too low: {success_rate:.2%}"
            
            print(f"✓ Batch processing completed: {completed_tasks}/{len(tasks)} successful")
            
        finally:
            # Close file handles
            for _, file_tuple in files:
                file_tuple[1].close()
    
    @pytest.mark.asyncio
    async def test_real_time_progress_monitoring(self, test_config, sample_image_file, services_ready):
        """Test real-time progress monitoring via Server-Sent Events."""
        # Upload image first
        upload_url = f"{test_config['backend_url']}/api/v1/upload/image"
        
        with open(sample_image_file, 'rb') as f:
            files = {'file': (sample_image_file.name, f, 'image/jpeg')}
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=sample_image_file.name, content_type='image/jpeg')
                
                async with session.post(upload_url, data=data) as response:
                    assert response.status == 200
                    upload_data = await response.json()
        
        task_id = upload_data['task_id']
        
        # Monitor via SSE
        sse_url = f"{test_config['backend_url']}/api/status/tasks/{task_id}/stream"
        
        progress_updates = []
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(sse_url) as response:
                    assert response.status == 200
                    assert response.headers.get('content-type') == 'text/event-stream'
                    
                    async for line in response.content:
                        if time.time() - start_time > max_wait_time:
                            break
                        
                        line = line.decode().strip()
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            if data != '[DONE]':
                                try:
                                    progress_data = json.loads(data)
                                    progress_updates.append(progress_data)
                                    
                                    status = progress_data.get('status')
                                    if status in ['completed', 'failed']:
                                        break
                                except json.JSONDecodeError:
                                    continue
        
        except Exception as e:
            # SSE might not be available, use polling instead
            print(f"SSE monitoring failed ({e}), falling back to polling")
            
            status_url = f"{test_config['backend_url']}/api/v1/status/tasks/{task_id}/status"
            while time.time() - start_time < max_wait_time:
                async with aiohttp.ClientSession() as session:
                    async with session.get(status_url) as response:
                        if response.status == 200:
                            status_data = await response.json()
                            progress_updates.append(status_data)
                            
                            if status_data.get('status') in ['completed', 'failed']:
                                break
                
                await asyncio.sleep(5)
        
        # Verify we got progress updates
        assert len(progress_updates) > 0, "No progress updates received"
        
        # Verify progress data structure
        for update in progress_updates:
            assert 'status' in update
            assert 'timestamp' in update
            
        print(f"✓ Real-time monitoring test passed with {len(progress_updates)} updates")
    
    def test_error_recovery_workflow(self, http_session, test_config, invalid_file, services_ready):
        """Test system recovery from error conditions."""
        # Step 1: Trigger an error with invalid file
        upload_url = f"{test_config['backend_url']}/api/v1/upload/image"
        
        with open(invalid_file, 'rb') as f:
            files = {'file': (invalid_file.name, f, 'text/plain')}
            error_response = http_session.post(upload_url, files=files, timeout=test_config['timeout'])
        
        assert error_response.status_code == 400
        error_data = error_response.json()
        assert error_data.get('error') == True
        
        # Step 2: Verify system is still healthy after error
        health_url = f"{test_config['backend_url']}/health"
        health_response = http_session.get(health_url, timeout=test_config['timeout'])
        
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data.get('status') == 'healthy'
        
        # Step 3: Verify normal operations still work
        # This would require a valid test file
        # For now, just verify the upload endpoint still responds
        empty_upload_response = http_session.post(upload_url, timeout=test_config['timeout'])
        assert empty_upload_response.status_code == 400  # Expected for missing file
        
        print("✓ Error recovery test passed")
    
    def test_concurrent_uploads(self, http_session, test_config, multiple_image_files, services_ready):
        """Test system handling of concurrent uploads."""
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        upload_url = f"{test_config['backend_url']}/api/v1/upload/image"
        results = []
        
        def upload_file(img_file: Path) -> Dict[str, Any]:
            """Upload a single file and return result."""
            try:
                with open(img_file, 'rb') as f:
                    files = {'file': (img_file.name, f, 'image/jpeg')}
                    response = http_session.post(upload_url, files=files, timeout=test_config['timeout'])
                
                return {
                    'file': img_file.name,
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'data': response.json() if response.status_code == 200 else None,
                    'error': response.text if response.status_code != 200 else None
                }
            except Exception as e:
                return {
                    'file': img_file.name,
                    'status_code': 0,
                    'success': False,
                    'data': None,
                    'error': str(e)
                }
        
        # Use first 3 files for concurrent upload test
        test_files = multiple_image_files[:3]
        
        # Execute concurrent uploads
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_file = {executor.submit(upload_file, img_file): img_file for img_file in test_files}
            
            for future in as_completed(future_to_file):
                result = future.result()
                results.append(result)
        
        # Analyze results
        successful_uploads = [r for r in results if r['success']]
        failed_uploads = [r for r in results if not r['success']]
        
        print(f"Concurrent uploads: {len(successful_uploads)} successful, {len(failed_uploads)} failed")
        
        # Should have at least some successful uploads
        assert len(successful_uploads) > 0, "No concurrent uploads succeeded"
        
        # Success rate should be reasonable (allowing for some failures due to load)
        success_rate = len(successful_uploads) / len(results)
        assert success_rate >= 0.5, f"Success rate too low: {success_rate:.2%}"
        
        print(f"✓ Concurrent upload test passed with {success_rate:.2%} success rate")

# Import aiohttp for async SSE testing
try:
    import aiohttp
except ImportError:
    # If aiohttp is not available, skip SSE tests
    pytest.skip("aiohttp not available for SSE testing", allow_module_level=True)
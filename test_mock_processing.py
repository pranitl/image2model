#!/usr/bin/env python3
"""
Test end-to-end flow with mocked FAL.AI - inject mock at worker level
"""
import os
import sys
import time
import json
import requests
from pathlib import Path

# API configuration
API_BASE = "http://localhost:8000/api/v1"
API_KEY = "dev-api-key-123456"

def setup_fal_mock():
    """Set environment variable to enable FAL.AI mocking in workers."""
    # This will be checked by the worker to use mock instead of real FAL.AI
    os.environ['USE_FAL_MOCK'] = 'true'
    print("FAL.AI mocking enabled via environment variable")

def test_batch_upload_with_mocked_fal():
    """Test batch upload with mocked FAL.AI processing."""
    
    setup_fal_mock()
    
    # Find test images
    test_images_dir = Path("tests/fixtures/images")
    test_images = list(test_images_dir.glob("*.jpg"))[:2]
    print(f"Found {len(test_images)} test images")
    
    # Prepare files for upload
    files = []
    for img_path in test_images:
        files.append(('files', (img_path.name, open(img_path, 'rb'), 'image/jpeg')))
    
    # Upload batch
    print("\n1. Uploading batch of images...")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    try:
        response = requests.post(f"{API_BASE}/upload/", files=files, headers=headers)
        response.raise_for_status()
        
        upload_data = response.json()
        task_id = upload_data['task_id']
        job_id = upload_data['job_id']
        
        print(f"Upload successful!")
        print(f"Task ID: {task_id}")
        print(f"Job ID: {job_id}")
        
        # Poll for task completion (simpler than SSE for testing)
        print("\n2. Polling for task completion...")
        
        max_attempts = 60  # 60 seconds timeout
        for i in range(max_attempts):
            status_response = requests.get(
                f"{API_BASE}/status/tasks/{task_id}/status",
                headers=headers
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status')
                state = status_data.get('state')
                
                print(f"[{i+1}s] Status: {status}, State: {state}")
                
                # Check if this is a chord task
                if status == 'completed' and status_data.get('result', {}).get('chord_task_id'):
                    chord_id = status_data['result']['chord_task_id']
                    print(f"Main task completed, switching to chord {chord_id}")
                    task_id = chord_id  # Switch to tracking chord
                    continue
                
                if status == 'completed':
                    print("\nTask completed successfully!")
                    
                    # Get job results
                    print(f"\n3. Getting job results...")
                    time.sleep(1)  # Give time for results to be stored
                    
                    results_response = requests.get(
                        f"{API_BASE}/download/{job_id}/all",
                        headers=headers
                    )
                    
                    if results_response.status_code == 200:
                        results_data = results_response.json()
                        print(f"Results available!")
                        print(f"Total files: {results_data.get('total_files', 0)}")
                        print(f"Files: {len(results_data.get('files', []))}")
                        
                        for file in results_data.get('files', []):
                            print(f"  - {file.get('filename')}: {file.get('size', 0)} bytes")
                    else:
                        print(f"Failed to get results: {results_response.status_code}")
                        print(f"Response: {results_response.text}")
                    
                    break
                
                elif status == 'failed':
                    print(f"\nTask failed: {status_data.get('error', 'Unknown error')}")
                    break
            
            time.sleep(1)
        else:
            print("\nTimeout waiting for task completion")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        for _, (_, file_obj, _) in files:
            file_obj.close()

if __name__ == "__main__":
    test_batch_upload_with_mocked_fal()
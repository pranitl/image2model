#!/usr/bin/env python3
"""
Test end-to-end flow with mocked FAL.AI
"""
import os
import time
import json
import requests
from pathlib import Path

# API configuration
API_BASE = "http://localhost:8000/api/v1"
API_KEY = "dev-api-key-123456"

def test_batch_upload_with_sse():
    """Test batch upload with SSE streaming to verify chord tracking works."""
    
    # Find test images
    test_images_dir = Path("tests/fixtures/images")
    if not test_images_dir.exists():
        print(f"Creating test images directory: {test_images_dir}")
        test_images_dir.mkdir(parents=True, exist_ok=True)
        
        # Create simple test images
        from PIL import Image
        for i in range(2):
            img = Image.new('RGB', (100, 100), color=(255, 0, 0))
            img.save(test_images_dir / f"test_image_{i+1}.jpg")
    
    # Get test images
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
        
        # Test SSE streaming
        print("\n2. Testing SSE stream for task progress...")
        
        # Use requests to simulate SSE client
        headers = {"Authorization": f"Bearer {API_KEY}", "Accept": "text/event-stream"}
        
        with requests.get(f"{API_BASE}/status/tasks/{task_id}/stream", 
                         headers=headers, stream=True, timeout=60) as response:
            
            start_time = time.time()
            events_received = []
            chord_detected = False
            completion_detected = False
            
            for line in response.iter_lines():
                if not line:
                    continue
                    
                line = line.decode('utf-8')
                
                # Parse SSE event
                if line.startswith('event:'):
                    event_type = line.split(':', 1)[1].strip()
                elif line.startswith('data:'):
                    data_str = line.split(':', 1)[1].strip()
                    try:
                        data = json.loads(data_str)
                        events_received.append((event_type if 'event_type' in locals() else 'unknown', data))
                        
                        # Print progress
                        status = data.get('status', 'unknown')
                        progress = data.get('progress', 0)
                        message = data.get('message', '')
                        
                        print(f"[{time.time() - start_time:.1f}s] Event: {event_type if 'event_type' in locals() else 'unknown'}")
                        print(f"  Status: {status}, Progress: {progress}%, Message: {message}")
                        
                        # Check for chord detection
                        if data.get('chord_task_id'):
                            chord_detected = True
                            print(f"  CHORD DETECTED: {data['chord_task_id']}")
                            print(f"  Main task transitioned to chord tracking")
                        
                        # Check for completion
                        if event_type == 'task_completed' or status == 'completed':
                            completion_detected = True
                            print(f"  TASK COMPLETED!")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON: {e}")
                        print(f"Raw data: {data_str}")
                
                # Timeout after 30 seconds
                if time.time() - start_time > 30:
                    print("Timeout waiting for completion")
                    break
        
        print(f"\n3. Summary:")
        print(f"Total events received: {len(events_received)}")
        print(f"Chord detected: {chord_detected}")
        print(f"Completion detected: {completion_detected}")
        
        # Check job results
        if completion_detected:
            print(f"\n4. Checking job results...")
            time.sleep(2)  # Give time for results to be stored
            
            response = requests.get(f"{API_BASE}/download/{job_id}/all", headers=headers)
            if response.status_code == 200:
                result_data = response.json()
                print(f"Results available!")
                print(f"Total files: {result_data.get('total_files', 0)}")
                print(f"Files: {len(result_data.get('files', []))}")
                
                # Print file details
                for file in result_data.get('files', []):
                    print(f"  - {file.get('filename')}: {file.get('size', 0)} bytes")
            else:
                print(f"Failed to get results: {response.status_code}")
                print(f"Response: {response.text}")
        
        # Cleanup
        for _, (_, file_obj, _) in files:
            file_obj.close()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_batch_upload_with_sse()
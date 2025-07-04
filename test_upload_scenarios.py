#!/usr/bin/env python3
"""Test different upload scenarios and log results/errors."""

import requests
import json
import time
import subprocess
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test files
TEST_FILES = [
    "tests/test-images/test1.png",
    "tests/test-images/test2.png", 
    "tests/test-images/test3.png"
]

def get_worker_logs(tail_lines=100):
    """Get recent worker logs."""
    try:
        result = subprocess.run(
            ["docker", "logs", "image2model-worker", f"--tail={tail_lines}"],
            capture_output=True,
            text=True
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Failed to get logs: {str(e)}"

def test_upload(files_to_upload, scenario_name):
    """Test upload with given files and log results."""
    print(f"\n{'='*60}")
    print(f"Testing: {scenario_name}")
    print(f"Files: {files_to_upload}")
    print(f"{'='*60}")
    
    # Clear worker logs before test
    subprocess.run(["docker", "compose", "restart", "worker"], capture_output=True)
    time.sleep(3)  # Wait for worker to restart
    
    # Prepare files for upload
    files = []
    for file_path in files_to_upload:
        files.append(('files', (file_path.split('/')[-1], open(file_path, 'rb'), 'image/png')))
    
    # Make upload request
    response = requests.post(f"{BASE_URL}/upload", files=files)
    
    # Close file handles
    for _, file_tuple in files:
        file_tuple[1].close()
    
    # Log response
    log_filename = f"upload_test_{scenario_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    with open(log_filename, 'w') as log_file:
        log_file.write(f"Test Scenario: {scenario_name}\n")
        log_file.write(f"Timestamp: {datetime.now().isoformat()}\n")
        log_file.write(f"Files uploaded: {files_to_upload}\n")
        log_file.write(f"\n{'='*60}\n")
        log_file.write("UPLOAD RESPONSE:\n")
        log_file.write(f"{'='*60}\n")
        log_file.write(f"Status Code: {response.status_code}\n")
        log_file.write(f"Headers: {dict(response.headers)}\n\n")
        
        try:
            response_json = response.json()
            log_file.write(f"Response Body:\n{json.dumps(response_json, indent=2)}\n")
            
            # If successful, wait and check status
            if response.status_code == 200 and 'job_id' in response_json:
                job_id = response_json['job_id']
                task_id = response_json.get('task_id')
                
                log_file.write(f"\n{'='*60}\n")
                log_file.write(f"Job ID: {job_id}\n")
                log_file.write(f"Task ID: {task_id}\n")
                
                # Wait for processing
                time.sleep(5)
                
                # Check job status
                status_response = requests.get(f"{BASE_URL}/jobs/{job_id}/status")
                log_file.write(f"\n{'='*60}\n")
                log_file.write("JOB STATUS CHECK:\n")
                log_file.write(f"{'='*60}\n")
                log_file.write(f"Status Code: {status_response.status_code}\n")
                try:
                    log_file.write(f"Response: {json.dumps(status_response.json(), indent=2)}\n")
                except:
                    log_file.write(f"Response Text: {status_response.text}\n")
                
                # Check task status via Celery
                if task_id:
                    task_response = requests.get(f"{BASE_URL}/tasks/{task_id}/status")
                    log_file.write(f"\n{'='*60}\n")
                    log_file.write("TASK STATUS CHECK:\n")
                    log_file.write(f"{'='*60}\n")
                    log_file.write(f"Status Code: {task_response.status_code}\n")
                    try:
                        log_file.write(f"Response: {json.dumps(task_response.json(), indent=2)}\n")
                    except:
                        log_file.write(f"Response Text: {task_response.text}\n")
                        
        except Exception as e:
            log_file.write(f"Response Text: {response.text}\n")
            log_file.write(f"Error parsing response: {str(e)}\n")
        
        # Get worker logs
        log_file.write(f"\n{'='*60}\n")
        log_file.write("WORKER LOGS:\n")
        log_file.write(f"{'='*60}\n")
        worker_logs = get_worker_logs(200)
        log_file.write(worker_logs)
        
        # Get any error logs specifically
        log_file.write(f"\n{'='*60}\n")
        log_file.write("ERROR LOGS (filtered):\n")
        log_file.write(f"{'='*60}\n")
        error_lines = [line for line in worker_logs.split('\n') if any(word in line.lower() for word in ['error', 'exception', 'traceback', 'coroutine'])]
        log_file.write('\n'.join(error_lines))
    
    print(f"Results logged to: {log_filename}")
    return log_filename

# Run tests
if __name__ == "__main__":
    print("Starting upload tests...")
    
    # Test 1: Single file
    log1 = test_upload([TEST_FILES[0]], "Single File Upload")
    time.sleep(5)
    
    # Test 2: Two files
    log2 = test_upload(TEST_FILES[:2], "Two Files Upload")
    time.sleep(5)
    
    # Test 3: Three files
    log3 = test_upload(TEST_FILES[:3], "Three Files Upload")
    
    print(f"\n{'='*60}")
    print("Test Summary:")
    print(f"{'='*60}")
    print(f"Single file log: {log1}")
    print(f"Two files log: {log2}")
    print(f"Three files log: {log3}")
    print("\nTests completed!")
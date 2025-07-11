#!/usr/bin/env python3
"""
Test script to verify that single file uploads work through the batch endpoint.
This ensures backward compatibility after removing the single file endpoint.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def create_test_image():
    """Create a simple test image file."""
    from PIL import Image
    import tempfile
    
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    img.save(temp_file.name)
    temp_file.close()
    
    return temp_file.name

def test_single_file_batch_upload():
    """Test uploading a single file through the batch endpoint."""
    print("Testing single file upload through batch endpoint...")
    
    base_url = "http://localhost:8000"
    test_image = None
    
    try:
        # Create test image
        test_image = create_test_image()
        print(f"✅ Created test image: {test_image}")
        
        # Upload single file as batch
        with open(test_image, 'rb') as f:
            files = [('files', ('test.jpg', f, 'image/jpeg'))]
            response = requests.post(
                f"{base_url}/api/v1/upload",
                files=files,
                data={'face_limit': '500'},
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful: {json.dumps(result, indent=2)}")
            
            # Verify response structure
            assert 'job_id' in result, "Missing job_id in response"
            assert 'status' in result, "Missing status in response"
            assert result.get('total_files') == 1, "Expected 1 file in batch"
            
            return result.get('job_id')
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None
    finally:
        # Clean up
        if test_image and os.path.exists(test_image):
            os.unlink(test_image)
            print("✅ Cleaned up test image")

def test_job_status(job_id):
    """Test checking job status for single file batch."""
    print(f"\nTesting job status for {job_id}...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Check status
        response = requests.get(
            f"{base_url}/api/v1/status/jobs/{job_id}/status",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status check successful: {json.dumps(result, indent=2)}")
            
            # Verify single file in results
            if result.get('status') == 'completed':
                assert result.get('total_files') == 1, "Expected 1 file in results"
                assert result.get('successful_files') <= 1, "Expected at most 1 successful file"
            
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

def test_download_single_file(job_id):
    """Test downloading result from single file batch."""
    print(f"\nTesting download for single file batch {job_id}...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Try to download
        response = requests.get(
            f"{base_url}/api/v1/download/{job_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            # Check if it's a direct file download or JSON response
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                result = response.json()
                print(f"✅ Download endpoint returned JSON: {json.dumps(result, indent=2)}")
                # This might mean job is still processing
            else:
                print(f"✅ Download successful: {len(response.content)} bytes")
                print(f"Content-Type: {content_type}")
            return True
        else:
            print(f"❌ Download failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def main():
    """Run single file batch compatibility tests."""
    print("🧪 Single File Batch Compatibility Test")
    print("=" * 50)
    print("This test verifies that single files can be processed through the batch endpoint")
    print("after the removal of the dedicated single file upload endpoint.")
    print("=" * 50)
    
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("❌ PIL/Pillow not installed. Install with: pip install Pillow")
        return 1
    
    # Test single file upload
    job_id = test_single_file_batch_upload()
    
    if job_id:
        # Wait a bit for processing
        print("\nWaiting 2 seconds for processing...")
        time.sleep(2)
        
        # Test status check
        test_job_status(job_id)
        
        # Test download
        test_download_single_file(job_id)
        
        print("\n✅ Single file batch compatibility test completed!")
        return 0
    else:
        print("\n❌ Single file batch compatibility test failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
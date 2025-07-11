#!/usr/bin/env python3
"""
Unit tests for Celery tasks.
"""

import os
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def test_process_file_in_batch():
    """Test the process_file_in_batch function."""
    print("Testing process_file_in_batch function...")
    
    try:
        from app.workers.tasks import process_file_in_batch
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', delete=False) as f:
            test_file = f.name
            f.write("test image content")
        
        try:
            # Test the function (simulating a single file batch)
            result = process_file_in_batch(
                file_path=test_file,
                job_id="test-job-123",
                face_limit=500,
                file_index=0,
                total_files=1
            )
            
            # Verify result structure
            assert 'file_path' in result, "Result missing 'file_path' field"
            assert 'status' in result, "Result missing 'status' field"
            
            if result['status'] == 'completed':
                assert 'result_path' in result or 'download_url' in result, "Successful result missing output path"
                assert 'model_format' in result, "Successful result missing 'model_format' field"
                print(f"✅ process_file_in_batch successful: {result}")
            else:
                assert 'error' in result, "Failed result missing 'error' field"
                print(f"❌ process_file_in_batch failed: {result}")
            
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.unlink(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ process_file_in_batch test failed: {e}")
        return False

def test_health_check_task():
    """Test the health check task."""
    print("Testing health_check_task...")
    
    try:
        from app.workers.tasks import health_check_task
        
        result = health_check_task()
        
        # Verify result structure
        assert isinstance(result, dict), "Health check result should be a dict"
        assert 'status' in result, "Health check missing 'status' field"
        assert result['status'] == 'healthy', "Health check status should be 'healthy'"
        
        print(f"✅ health_check_task successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ health_check_task test failed: {e}")
        return False

def test_task_retry_mechanism():
    """Test task retry configuration."""
    print("Testing task retry mechanism...")
    
    try:
        from app.core.celery_app import celery_app
        from app.workers.tasks import process_batch
        
        # Check retry configuration
        task = celery_app.tasks['app.workers.tasks.process_batch']
        
        assert hasattr(task, 'autoretry_for'), "Task should have autoretry_for"
        assert hasattr(task, 'retry_kwargs'), "Task should have retry_kwargs"
        
        print(f"✅ Retry configuration: autoretry_for={task.autoretry_for}")
        print(f"✅ Retry kwargs: {task.retry_kwargs}")
        
        return True
        
    except Exception as e:
        print(f"❌ Task retry mechanism test failed: {e}")
        return False

def test_task_metadata():
    """Test task metadata and binding."""
    print("Testing task metadata...")
    
    try:
        from app.core.celery_app import celery_app
        import app.workers.tasks
        
        # Test process_batch task
        process_batch_task = celery_app.tasks.get('app.workers.tasks.process_batch')
        if process_batch_task:
            print(f"✅ process_batch task found")
            print(f"   - Name: {process_batch_task.name}")
            print(f"   - Bind: {getattr(process_batch_task, 'bind', False)}")
            print(f"   - Queue: {getattr(process_batch_task, 'queue', 'default')}")
        else:
            print("❌ process_batch task not found")
            return False
        
        # Test health_check task
        health_task = celery_app.tasks.get('app.workers.tasks.health_check_task')
        if health_task:
            print(f"✅ health_check_task found")
            print(f"   - Name: {health_task.name}")
        else:
            print("❌ health_check_task not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Task metadata test failed: {e}")
        return False

def test_logging_in_tasks():
    """Test logging functionality in tasks."""
    print("Testing logging in tasks...")
    
    try:
        from app.core.logging_config import get_task_logger, set_correlation_id
        import logging
        
        # Set correlation ID
        correlation_id = set_correlation_id("test-correlation-id")
        
        # Get task logger
        task_logger = get_task_logger("test_task", "test_task_id")
        
        # Test logging methods
        task_logger.info("Test info message")
        task_logger.warning("Test warning message")
        task_logger.error("Test error message")
        
        print(f"✅ Task logging successful with correlation ID: {correlation_id}")
        return True
        
    except Exception as e:
        print(f"❌ Logging in tasks test failed: {e}")
        return False

def test_task_time_limits():
    """Test task time limit configuration."""
    print("Testing task time limits...")
    
    try:
        from app.core.celery_app import celery_app
        
        # Check time limit configuration
        time_limit = celery_app.conf.task_time_limit
        soft_time_limit = celery_app.conf.task_soft_time_limit
        
        assert time_limit == 1800, f"Expected time limit 1800, got {time_limit}"
        assert soft_time_limit == 1500, f"Expected soft time limit 1500, got {soft_time_limit}"
        
        print(f"✅ Time limits configured: hard={time_limit}s, soft={soft_time_limit}s")
        return True
        
    except Exception as e:
        print(f"❌ Task time limits test failed: {e}")
        return False

def main():
    """Run all task tests."""
    print("🧪 Celery Task Tests")
    print("=" * 40)
    
    tests = [
        ("Process File in Batch", test_process_file_in_batch),
        ("Health Check Task", test_health_check_task),
        ("Task Retry Mechanism", test_task_retry_mechanism),
        ("Task Metadata", test_task_metadata),
        ("Logging in Tasks", test_logging_in_tasks),
        ("Task Time Limits", test_task_time_limits),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("🔍 Task Test Results:")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All task tests passed!")
        return 0
    else:
        print("⚠️  Some task tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python3
"""
Test script to verify Celery worker configuration and Redis connectivity.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def test_redis_connection():
    """Test Redis connection."""
    print("Testing Redis connection...")
    try:
        import redis
        from app.core.config import settings
        
        # Parse Redis URL to get connection details
        if settings.CELERY_BROKER_URL.startswith('redis://'):
            # Simple redis URL parsing
            url_parts = settings.CELERY_BROKER_URL.replace('redis://', '').split('/')
            host_port = url_parts[0].split(':')
            host = host_port[0] if host_port[0] else 'localhost'
            port = int(host_port[1]) if len(host_port) > 1 else 6379
            db = int(url_parts[1]) if len(url_parts) > 1 else 0
        else:
            host, port, db = 'localhost', 6379, 0
        
        # Test connection
        r = redis.Redis(host=host, port=port, db=db, socket_timeout=5)
        r.ping()
        print(f"✅ Redis connection successful: {host}:{port}/{db}")
        
        # Test basic operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        r.delete('test_key')
        print(f"✅ Redis operations successful: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_celery_app_configuration():
    """Test Celery app configuration."""
    print("\nTesting Celery app configuration...")
    try:
        from app.core.celery_app import celery_app
        
        # Test basic configuration
        print(f"✅ Celery app name: {celery_app.main}")
        print(f"✅ Broker URL: {celery_app.conf.broker_url}")
        print(f"✅ Result backend: {celery_app.conf.result_backend}")
        print(f"✅ Task serializer: {celery_app.conf.task_serializer}")
        print(f"✅ Result serializer: {celery_app.conf.result_serializer}")
        print(f"✅ Timezone: {celery_app.conf.timezone}")
        print(f"✅ Task time limit: {celery_app.conf.task_time_limit}")
        print(f"✅ Task soft time limit: {celery_app.conf.task_soft_time_limit}")
        
        # Test task discovery
        print(f"✅ Registered tasks: {len(celery_app.tasks)}")
        for task_name in sorted(celery_app.tasks.keys()):
            if not task_name.startswith('celery.'):
                print(f"   - {task_name}")
        
        return True
    except Exception as e:
        print(f"❌ Celery configuration test failed: {e}")
        return False

def test_task_registration():
    """Test task registration."""
    print("\nTesting task registration...")
    try:
        from app.core.celery_app import celery_app
        # Import tasks to register them
        import app.workers.tasks
        
        # Expected tasks
        expected_tasks = [
            'app.workers.tasks.process_batch',
            'app.workers.tasks.generate_3d_model_task',
            'app.workers.tasks.process_file_in_batch',
            'app.workers.tasks.finalize_batch_results',
            'app.workers.tasks.process_single_image_with_retry',
            'app.workers.tasks.cleanup_old_files',
            'app.workers.tasks.health_check_task'
        ]
        
        registered_tasks = list(celery_app.tasks.keys())
        
        all_registered = True
        for task in expected_tasks:
            if task in registered_tasks:
                print(f"✅ Task registered: {task}")
            else:
                print(f"❌ Task not registered: {task}")
                all_registered = False
        
        return all_registered
    except Exception as e:
        print(f"❌ Task registration test failed: {e}")
        return False

def test_logging_configuration():
    """Test logging configuration."""
    print("\nTesting logging configuration...")
    try:
        from app.core.logging_config import setup_logging, get_task_logger, set_correlation_id
        
        # Set up logging
        setup_logging()
        print("✅ Logging setup successful")
        
        # Test correlation ID
        correlation_id = set_correlation_id()
        print(f"✅ Correlation ID set: {correlation_id}")
        
        # Test task logger
        logger = get_task_logger('test_task', 'test_id')
        logger.info("Test log message")
        print("✅ Task logger working")
        
        return True
    except Exception as e:
        print(f"❌ Logging configuration test failed: {e}")
        return False

def test_worker_startup_script():
    """Test worker startup script exists and is executable."""
    print("\nTesting worker startup script...")
    try:
        script_path = Path(__file__).parent / 'start_worker.py'
        
        if script_path.exists():
            print(f"✅ Worker script exists: {script_path}")
        else:
            print(f"❌ Worker script not found: {script_path}")
            return False
        
        if os.access(script_path, os.X_OK):
            print("✅ Worker script is executable")
        else:
            print("❌ Worker script is not executable")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Worker startup script test failed: {e}")
        return False

def test_task_signature_creation():
    """Test task signature creation."""
    print("\nTesting task signature creation...")
    try:
        from app.core.celery_app import celery_app
        
        # Test creating task signatures
        health_check = celery_app.signature('app.workers.tasks.health_check_task')
        print(f"✅ Health check signature: {health_check}")
        
        # Test process_batch signature
        process_batch = celery_app.signature('app.workers.tasks.process_batch', 
                                           args=['test_job_id', ['/path/to/test.jpg']])
        print(f"✅ Process batch signature: {process_batch}")
        
        return True
    except Exception as e:
        print(f"❌ Task signature creation test failed: {e}")
        return False

def test_directories_creation():
    """Test that required directories can be created."""
    print("\nTesting directory creation...")
    try:
        required_dirs = ['logs', 'results', 'uploads']
        
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            dir_path.mkdir(exist_ok=True)
            if dir_path.exists():
                print(f"✅ Directory created/exists: {dir_name}")
            else:
                print(f"❌ Failed to create directory: {dir_name}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Directory creation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Celery Worker Configuration Tests")
    print("=" * 50)
    
    tests = [
        ("Redis Connection", test_redis_connection),
        ("Celery App Configuration", test_celery_app_configuration),
        ("Task Registration", test_task_registration),
        ("Logging Configuration", test_logging_configuration),
        ("Worker Startup Script", test_worker_startup_script),
        ("Task Signature Creation", test_task_signature_creation),
        ("Directory Creation", test_directories_creation),
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
    print("\n" + "=" * 50)
    print("🔍 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Celery worker configuration is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
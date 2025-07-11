"""
Test environment setup for consistent test configuration.
"""

import os
from unittest.mock import patch

# Test API keys
TEST_API_KEY = "test-api-key-for-development"
TEST_ADMIN_API_KEY = "test-admin-api-key-for-development"
TEST_FAL_API_KEY = "test-fal-api-key-12345"

def setup_test_env():
    """Set up test environment variables."""
    env_vars = {
        'API_KEY': TEST_API_KEY,
        'ADMIN_API_KEY': TEST_ADMIN_API_KEY,
        'FAL_API_KEY': TEST_FAL_API_KEY,
        'ENVIRONMENT': 'development',
        'REDIS_URL': 'redis://localhost:6379/0',
        'CELERY_BROKER_URL': 'redis://localhost:6379/0',
        'CELERY_RESULT_BACKEND': 'redis://localhost:6379/0'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    return env_vars

def mock_settings(**overrides):
    """Create a mock settings object with test values."""
    from types import SimpleNamespace
    
    settings = SimpleNamespace(
        API_KEY=TEST_API_KEY,
        ADMIN_API_KEY=TEST_ADMIN_API_KEY,
        FAL_API_KEY=TEST_FAL_API_KEY,
        ENVIRONMENT='development',
        REDIS_URL='redis://localhost:6379/0',
        CELERY_BROKER_URL='redis://localhost:6379/0',
        CELERY_RESULT_BACKEND='redis://localhost:6379/0',
        UPLOAD_DIR='uploads',
        OUTPUT_DIR='results',
        MAX_FILE_SIZE=10 * 1024 * 1024,
        ALLOWED_EXTENSIONS=['.jpg', '.jpeg', '.png', '.webp'],
        UPLOAD_MAX_FILES=25,
        RATE_LIMIT_PER_MINUTE=60,
        RATE_LIMIT_PER_HOUR=1000
    )
    
    # Apply any overrides
    for key, value in overrides.items():
        setattr(settings, key, value)
    
    return settings
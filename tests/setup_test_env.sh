#!/bin/bash
# Setup test environment variables for authentication tests

# Export test API keys that match what the tests expect
export API_KEY="test-api-key-for-development"
export ADMIN_API_KEY="test-admin-api-key-for-development"
export FAL_API_KEY="test-fal-api-key-12345"

# Set environment to development to allow test keys
export ENVIRONMENT="development"

# Set Redis URL for tests
export REDIS_URL="redis://localhost:6379/0"

echo "Test environment variables set:"
echo "API_KEY=$API_KEY"
echo "ADMIN_API_KEY=$ADMIN_API_KEY"
echo "FAL_API_KEY=$FAL_API_KEY"
echo "ENVIRONMENT=$ENVIRONMENT"
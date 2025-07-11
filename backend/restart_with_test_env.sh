#!/bin/bash
# Restart backend with test environment variables

# Export test environment variables
export API_KEY="test-api-key-for-development"
export ADMIN_API_KEY="test-admin-api-key-for-development"
export FAL_API_KEY="test-fal-api-key-12345"
export ENVIRONMENT="development"
export REDIS_URL="redis://localhost:6379/0"
export DATABASE_URL="postgresql://postgres:password@localhost:5432/image2model"
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
export SECRET_KEY="test-secret-key-for-development"
export LOG_LEVEL="INFO"
export DEBUG="True"

# Kill existing backend process
echo "Stopping existing backend..."
pkill -f "uvicorn app.main:app" || true

# Wait for process to stop
sleep 2

# Start backend with test environment
echo "Starting backend with test environment..."
cd /Users/pranit/Documents/AI/image2model/backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend_test.log 2>&1 &

echo "Backend started with PID: $!"
echo "Waiting for backend to be ready..."
sleep 5

# Check if backend is running
curl -s http://localhost:8000/health | jq . || echo "Backend health check failed"

echo "Backend is ready for testing with test API keys"
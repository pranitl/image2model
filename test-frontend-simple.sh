#!/bin/bash
# Simple test script to verify frontend-simple works

echo "Testing Frontend-Simple Setup"
echo "============================"

# Step 1: Build and run ONLY frontend-simple
echo "1. Building frontend-simple container..."
docker build -t frontend-simple-test ./frontend-simple

# Step 2: Run it temporarily
echo "2. Running frontend-simple on port 3001..."
docker run -d --name frontend-simple-test \
  -p 3001:80 \
  --network image2model-network \
  frontend-simple-test

echo "3. Waiting for container to start..."
sleep 5

# Step 3: Test basic pages
echo "4. Testing pages..."
echo -n "   - Homepage: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/ | grep -q "200" && echo "✓ OK" || echo "✗ FAILED"

echo -n "   - Upload page: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/upload.html | grep -q "200" && echo "✓ OK" || echo "✗ FAILED"

echo -n "   - CSS loads: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/css/style.css | grep -q "200" && echo "✓ OK" || echo "✗ FAILED"

echo -n "   - JS loads: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/js/api.js | grep -q "200" && echo "✓ OK" || echo "✗ FAILED"

# Step 4: Cleanup
echo ""
echo "5. Cleaning up test container..."
docker stop frontend-simple-test
docker rm frontend-simple-test

echo ""
echo "Test complete! If all tests passed, frontend-simple is ready."
echo "Next step: Run 'docker-compose up -d frontend-simple' to test with backend"
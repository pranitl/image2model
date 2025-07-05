#!/bin/bash
# End-to-end test script for image2model

set -e

echo "=== Testing Image2Model End-to-End Flow ==="
echo

# Test image path
TEST_IMAGE="./tests/test-images/test1.png"

if [ ! -f "$TEST_IMAGE" ]; then
    echo "Error: Test image not found at $TEST_IMAGE"
    echo "Please ensure tests/test-images/sample1.jpg exists"
    exit 1
fi

echo "1. Testing API health..."
curl -s http://localhost:8000/api/v1/health/ready | jq '.' || echo "API not ready"
echo

echo "2. Uploading test image..."
UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/upload \
  -F "files=@${TEST_IMAGE}" \
  -F "face_limit=5000")

echo "Upload response:"
echo "$UPLOAD_RESPONSE" | jq '.'

JOB_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.job_id')
echo "Job ID: $JOB_ID"
echo

if [ "$JOB_ID" == "null" ]; then
    echo "Error: Failed to get job ID from upload"
    exit 1
fi

echo "3. Waiting for processing to complete..."
sleep 10

echo "4. Checking job status..."
STATUS_RESPONSE=$(curl -s http://localhost:8000/api/v1/status/$JOB_ID)
echo "$STATUS_RESPONSE" | jq '.'
echo

echo "5. Testing debug endpoint..."
DEBUG_RESPONSE=$(curl -s http://localhost:8000/api/v1/debug/job/$JOB_ID)
echo "$DEBUG_RESPONSE" | jq '.'
echo

echo "6. Fetching results..."
RESULTS_RESPONSE=$(curl -s http://localhost:8000/api/v1/download/$JOB_ID/all)
echo "$RESULTS_RESPONSE" | jq '.'
echo

# Check if results contain files
FILES_COUNT=$(echo "$RESULTS_RESPONSE" | jq '.files | length')
if [ "$FILES_COUNT" -gt 0 ]; then
    echo "✅ Success! Found $FILES_COUNT files in results"
    echo "First file:"
    echo "$RESULTS_RESPONSE" | jq '.files[0]'
else
    echo "❌ Error: No files found in results"
    
    echo
    echo "Checking Redis directly..."
    docker compose exec redis redis-cli GET "job_result:$JOB_ID" | jq '.' 2>/dev/null || echo "No Redis data"
    
    echo
    echo "Checking worker logs..."
    docker compose logs worker --tail 20 | grep -E "$JOB_ID|error|Error" || echo "No relevant worker logs"
fi

echo
echo "=== Test Complete ==="
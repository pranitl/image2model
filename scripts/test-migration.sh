#!/bin/bash
# Test script for frontend migration

echo "Frontend Migration Test Script"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local url=$1
    local name=$2
    
    echo -n "Testing $name... "
    
    # Test if endpoint responds
    if curl -s -f -o /dev/null "$url"; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Function to test API proxy
test_api() {
    local base_url=$1
    local name=$2
    
    echo -n "Testing $name API proxy... "
    
    # Test if API health endpoint responds through proxy
    if curl -s -f -o /dev/null "$base_url/api/v1/health"; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        return 1
    fi
}

echo "1. Testing React Frontend (Port 3000)"
echo "-------------------------------------"
test_endpoint "http://localhost:3000" "Homepage"
test_endpoint "http://localhost:3000/upload" "Upload page"
test_api "http://localhost:3000" "React frontend"
echo ""

echo "2. Testing Simple Frontend (Port 3001)"
echo "--------------------------------------"
test_endpoint "http://localhost:3001" "Homepage"
test_endpoint "http://localhost:3001/upload.html" "Upload page"
test_endpoint "http://localhost:3001/processing.html" "Processing page"
test_endpoint "http://localhost:3001/results.html" "Results page"
test_api "http://localhost:3001" "Simple frontend"
echo ""

echo "3. Testing Static Assets"
echo "------------------------"
test_endpoint "http://localhost:3001/css/style.css" "CSS file"
test_endpoint "http://localhost:3001/js/api.js" "API JS"
test_endpoint "http://localhost:3001/js/upload.js" "Upload JS"
test_endpoint "http://localhost:3001/assets/favicon.svg" "Favicon"
echo ""

echo "4. Testing Backend API (Port 8000)"
echo "----------------------------------"
test_endpoint "http://localhost:8000/api/v1/health" "Health endpoint"
test_endpoint "http://localhost:8000/docs" "API Documentation"
echo ""

# Check if both containers are running
echo "5. Container Status"
echo "-------------------"
echo -e "${YELLOW}Running containers:${NC}"
docker compose ps --services | grep -E "frontend|backend" | while read service; do
    status=$(docker compose ps $service --format "table {{.Status}}" | tail -n 1)
    if [[ $status == *"Up"* ]]; then
        echo -e "  $service: ${GREEN}Running${NC}"
    else
        echo -e "  $service: ${RED}Not running${NC}"
    fi
done

echo ""
echo "=============================="
echo "Migration test complete!"
echo ""
echo "Next steps:"
echo "1. If all tests pass, you can start gradual migration"
echo "2. Update nginx configuration for traffic routing"
echo "3. Monitor logs: docker compose logs -f frontend-simple"
echo "4. Check metrics and performance"
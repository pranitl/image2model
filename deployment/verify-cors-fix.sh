#!/bin/bash
# Script to verify the CORS fix for frontend build

set -e

echo "🔍 Verifying CORS fix..."
echo ""

# Step 1: Show current environment variable
echo "📋 Step 1: Checking .env.production for PUBLIC_API_URL"
if [ -f .env.production ]; then
    grep "PUBLIC_API_URL" .env.production || echo "PUBLIC_API_URL not found in .env.production"
else
    echo "❌ .env.production not found!"
    exit 1
fi

echo ""
echo "🔨 Step 2: Rebuilding frontend container with --no-cache"
echo "This ensures we get a fresh build with the environment variable..."
docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache frontend

echo ""
echo "🚀 Step 3: Starting the updated frontend container"
docker compose -f docker-compose.prod.yml --env-file .env.production up -d frontend

echo ""
echo "🔍 Step 4: Checking built files for localhost references"
echo "Waiting 10 seconds for container to start..."
sleep 10

# Check if the container is running
if docker ps | grep -q "image2model-frontend"; then
    echo "✅ Frontend container is running"
    
    # Check for localhost references in built files
    echo ""
    echo "Searching for 'localhost:8000' in built JavaScript files..."
    
    # Execute grep inside the container
    LOCALHOST_FOUND=$(docker exec image2model-frontend sh -c "grep -r 'localhost:8000' /app/build || true" | wc -l)
    
    if [ "$LOCALHOST_FOUND" -gt 0 ]; then
        echo "❌ FAILED: Found 'localhost:8000' in built files!"
        echo "The environment variable is not being properly injected during build."
        docker exec image2model-frontend sh -c "grep -r 'localhost:8000' /app/build" | head -5
    else
        echo "✅ SUCCESS: No 'localhost:8000' references found in built files!"
        
        # Check for the correct production URL
        echo ""
        echo "Verifying production API URL is present..."
        PROD_URL_FOUND=$(docker exec image2model-frontend sh -c "grep -r 'image2model.pranitlab.com/api/v1' /app/build || true" | wc -l)
        
        if [ "$PROD_URL_FOUND" -gt 0 ]; then
            echo "✅ CONFIRMED: Production API URL found in built files!"
            echo ""
            echo "🎉 The CORS fix has been successfully applied!"
            echo "The frontend should now use the correct production API URL."
        else
            echo "⚠️  WARNING: Production API URL not found in built files."
            echo "The build may have failed to inject the environment variable."
        fi
    fi
else
    echo "❌ Frontend container is not running!"
    docker ps
fi

echo ""
echo "📊 Container logs (last 20 lines):"
docker logs image2model-frontend --tail 20

echo ""
echo "✅ Verification complete!"
#!/bin/bash
# MVP Deployment Script
# 
# Features:
# - Uses git rebase instead of pull to maintain clean history
# - Supports both cached and no-cache builds (use --no-cache flag for fresh builds)
# - Ensures proper newline handling when appending to .env files
#
# Usage:
#   ./deploy-mvp.sh              # Normal deployment (uses cache)
#   ./deploy-mvp.sh --no-cache   # Force fresh build without cache

# Load deployment configuration from environment or .env.production file
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Load .env.production if it exists
if [ -f "$PROJECT_ROOT/.env.production" ]; then
    export $(grep -E '^(DEPLOY_HOST|DEPLOY_USER)=' "$PROJECT_ROOT/.env.production" | xargs)
fi

DEPLOY_HOST=${DEPLOY_HOST}
DEPLOY_USER=${DEPLOY_USER}
NO_CACHE_FLAG=""

# Validate required variables
if [ -z "$DEPLOY_HOST" ] || [ -z "$DEPLOY_USER" ]; then
    echo "❌ Error: DEPLOY_HOST and DEPLOY_USER must be set!"
    echo "   Either export them or ensure they're in .env.production"
    exit 1
fi

# Get the current local branch
LOCAL_BRANCH=$(git branch --show-current)
if [ -z "$LOCAL_BRANCH" ]; then
    echo "❌ Error: Could not determine current branch!"
    exit 1
fi

echo "📌 Current local branch: $LOCAL_BRANCH"

# Check for --no-cache argument
if [ "$1" = "--no-cache" ]; then
    NO_CACHE_FLAG="--no-cache"
    echo "🔨 No-cache mode enabled - will rebuild everything from scratch"
fi

echo "🚀 Deploying branch '$LOCAL_BRANCH' to $DEPLOY_HOST..."

ssh $DEPLOY_USER@$DEPLOY_HOST "NO_CACHE_FLAG='$NO_CACHE_FLAG' LOCAL_BRANCH='$LOCAL_BRANCH' bash -s" << 'EOF'
set -e  # Exit on error

# Source deployment functions
source <(curl -s https://raw.githubusercontent.com/pranitl/image2model/main/deployment/scripts/deployment-functions.sh || cat /opt/image2model/deployment/scripts/deployment-functions.sh 2>/dev/null || echo "")

# Set up error handling
trap handle_error ERR

# Initialize deployment
init_deployment

# Create backup before deployment
create_backup

cd /opt/image2model

# Ensure we're on the right repo
if ! git remote -v | grep -q "github.com/pranitl/image2model"; then
    echo "❌ Wrong git repo!"
    exit 1
fi

# Pull latest changes with rebase
mark_stage "git_pull"
echo "📥 Pulling latest code with rebase..."

# First, fetch all branches to ensure we have the latest
git fetch origin

# Check current branch on server
SERVER_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "📍 Server is currently on branch: $SERVER_BRANCH"
echo "🎯 Target branch from local: $LOCAL_BRANCH"

# If branches don't match, switch to the correct branch
if [ "$SERVER_BRANCH" != "$LOCAL_BRANCH" ]; then
    echo "🔄 Switching from '$SERVER_BRANCH' to '$LOCAL_BRANCH'..."
    # Check if branch exists locally
    if git show-ref --verify --quiet refs/heads/$LOCAL_BRANCH; then
        git checkout $LOCAL_BRANCH
    else
        # Create and checkout the branch, tracking the remote
        git checkout -b $LOCAL_BRANCH origin/$LOCAL_BRANCH
    fi
fi

# Now pull with rebase
echo "📥 Rebasing $LOCAL_BRANCH with origin/$LOCAL_BRANCH..."
git pull --rebase origin $LOCAL_BRANCH

# Ensure environment file is up to date
if [ -f ".env.production" ]; then
    cp .env.production .env
    # Ensure file ends with newline before appending
    [ -n "$(tail -c 1 .env)" ] && echo >> .env
    # Add any missing Docker-specific variables
    grep -q "BACKEND_HOST" .env || echo "BACKEND_HOST=backend" >> .env
    grep -q "BACKEND_PORT" .env || echo "BACKEND_PORT=8000" >> .env
    grep -q "POSTGRES_PORT" .env || echo "POSTGRES_PORT=5432" >> .env
fi

# Restart services with optional rebuild
mark_stage "docker_deployment"
echo "🔄 Restarting services..."
# Use DOCKER_BUILDKIT=1 for better performance and BUILDKIT_PROGRESS=plain for clearer output
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

# Down the services first
docker compose -f docker-compose.prod.yml --env-file .env.production down

if [ -n "$NO_CACHE_FLAG" ]; then
    echo "🔨 Building with --no-cache (fresh build)..."
    docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache
    docker compose -f docker-compose.prod.yml --env-file .env.production up -d
else
    echo "⚡ Building with cache (faster)..."
    # Use --build flag with up for better performance when cache is enabled
    docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
fi

# Wait and check
echo "⏳ Waiting for services..."
sleep 60

# Health check
mark_stage "health_check"
if health_check_with_retry "http://localhost/api/v1/health/" 5 15; then
    echo "✅ Local health check passed!"
    
    # Test via Cloudflare
    echo "🌐 Testing via Cloudflare..."
    if health_check_with_retry "https://image2model.pranitlab.com/api/v1/health/" 3 10; then
        echo "✅ Deployment successful! Site is live."
        cleanup_deployment
    else
        echo "⚠️  Warning: Cloudflare check failed (might need DNS propagation)"
        cleanup_deployment
    fi
else
    echo "❌ Health check failed!"
    docker logs image2model-backend --tail 20
    exit 1
fi
EOF

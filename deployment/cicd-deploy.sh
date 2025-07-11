#!/bin/bash
# CI/CD deployment script for Image2Model
# This script is designed to be run in CI/CD pipelines (GitHub Actions, GitLab CI, etc.)

set -e  # Exit on error

# Configuration from environment variables
PROJECT_NAME=${PROJECT_NAME:-"image2model"}
DEPLOY_USER=${DEPLOY_USER:-"root"}
DEPLOY_HOST=${DEPLOY_HOST:-"66.228.60.251"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
SLACK_WEBHOOK=${SLACK_WEBHOOK:-""}  # Optional Slack notifications

# Colors for output (may not work in all CI environments)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect CI environment
CI_PLATFORM="unknown"
if [ -n "$GITHUB_ACTIONS" ]; then
    CI_PLATFORM="github"
elif [ -n "$GITLAB_CI" ]; then
    CI_PLATFORM="gitlab"
elif [ -n "$JENKINS_URL" ]; then
    CI_PLATFORM="jenkins"
elif [ -n "$CIRCLECI" ]; then
    CI_PLATFORM="circleci"
fi

echo "🚀 Starting deployment for $PROJECT_NAME"
echo "📦 Environment: $ENVIRONMENT"
echo "🏗️  CI Platform: $CI_PLATFORM"
echo "🎯 Target: $DEPLOY_USER@$DEPLOY_HOST"

# Function to send Slack notification
send_slack_notification() {
    if [ -n "$SLACK_WEBHOOK" ]; then
        local color="$1"
        local title="$2"
        local message="$3"
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"attachments\":[{\"color\":\"$color\",\"title\":\"$title\",\"text\":\"$message\"}]}" \
            "$SLACK_WEBHOOK" 2>/dev/null || true
    fi
}

# Check required environment variables
check_env() {
    local required_vars=(
        "CLOUDFLARE_API_TOKEN"
        "CLOUDFLARE_ACCOUNT_ID"
        "FAL_API_KEY"
        "DATABASE_URL"
        "API_KEY"
    )
    
    echo "✓ Checking required environment variables..."
    local missing=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing+=("$var")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo "❌ Missing required environment variables:"
        printf '%s\n' "${missing[@]}"
        exit 1
    fi
    
    echo "✓ All required environment variables are set"
}

# Build Docker images
build_images() {
    echo "🏗️  Building Docker images..."
    
    # Tag images with git commit hash
    GIT_COMMIT=${GITHUB_SHA:-${CI_COMMIT_SHA:-$(git rev-parse HEAD)}}
    export IMAGE_TAG="${GIT_COMMIT:0:7}"
    
    # Build with BuildKit for better caching
    export DOCKER_BUILDKIT=1
    
    docker compose -f docker-compose.prod.yml build \
        --build-arg GIT_COMMIT="$GIT_COMMIT" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    
    echo "✓ Images built with tag: $IMAGE_TAG"
}

# Run tests
run_tests() {
    echo "🧪 Running tests..."
    
    # Backend tests
    echo "  Running backend tests..."
    docker run --rm \
        -e DATABASE_URL="sqlite:///test.db" \
        ${PROJECT_NAME}-backend:latest \
        pytest -v --cov=app tests/
    
    # Frontend tests (if applicable)
    # echo "  Running frontend tests..."
    # docker run --rm ${PROJECT_NAME}-frontend:latest npm test
    
    echo "✓ All tests passed"
}

# Deploy to server
deploy_to_server() {
    echo "📦 Deploying to $DEPLOY_HOST..."
    
    # Create deployment package
    tar -czf deploy.tar.gz \
        docker-compose.prod.yml \
        docker/ \
        deployment/ \
        nginx.conf \
        redis.conf
    
    # Copy to server
    scp -o StrictHostKeyChecking=no deploy.tar.gz $DEPLOY_USER@$DEPLOY_HOST:/tmp/
    
    # Execute deployment with error handling
    ssh -o StrictHostKeyChecking=no $DEPLOY_USER@$DEPLOY_HOST << 'ENDSSH'
set -e

# Simple error handler for CI/CD
DEPLOY_BACKUP="/opt/image2model-backup-$(date +%s)"
rollback() {
    echo "🔄 Rolling back deployment..."
    if [ -d "$DEPLOY_BACKUP" ]; then
        cd /opt
        docker compose -f image2model/docker-compose.prod.yml down || true
        rm -rf image2model
        mv "$DEPLOY_BACKUP" image2model
        cd image2model
        docker compose -f docker-compose.prod.yml up -d
        echo "✓ Rollback completed"
    fi
    exit 1
}
trap rollback ERR

echo "🚀 Starting deployment on server..."

# Create backup if exists
if [ -d "/opt/image2model" ]; then
    echo "📦 Creating backup..."
    cp -r /opt/image2model "$DEPLOY_BACKUP"
fi

# Navigate to project directory
cd /opt/image2model || mkdir -p /opt/image2model && cd /opt/image2model

# Extract deployment files
tar -xzf /tmp/deploy.tar.gz
rm /tmp/deploy.tar.gz

# Create .env file from CI environment variables
cat > .env.production << EOF
ENVIRONMENT=production
DATABASE_URL=$DATABASE_URL
CELERY_BROKER_URL=$CELERY_BROKER_URL
FAL_API_KEY=$FAL_API_KEY
API_KEY=$API_KEY
ADMIN_API_KEY=$ADMIN_API_KEY
CLOUDFLARE_TEAM_DOMAIN=$CLOUDFLARE_TEAM_DOMAIN
CLOUDFLARE_AUD_TAG=$CLOUDFLARE_AUD_TAG
CLOUDFLARE_ALLOWED_EMAILS=$CLOUDFLARE_ALLOWED_EMAILS
EOF

# Copy to .env for Docker Compose
cp .env.production .env

# Pull latest images (if using registry)
# docker compose -f docker-compose.prod.yml pull

# Stop old containers
docker compose -f docker-compose.prod.yml down

# Start new containers
docker compose -f docker-compose.prod.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Health check with retries
MAX_ATTEMPTS=5
ATTEMPT=1
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Health check attempt $ATTEMPT/$MAX_ATTEMPTS..."
    if curl -f http://localhost/api/v1/health/ >/dev/null 2>&1; then
        echo "✓ Deployment successful!"
        # Clean up backup on success
        rm -rf "$DEPLOY_BACKUP"
        break
    else
        if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
            echo "❌ Health check failed after $MAX_ATTEMPTS attempts!"
            docker logs image2model-backend --tail 50
            exit 1
        fi
        echo "⏳ Waiting 15s before retry..."
        sleep 15
        ATTEMPT=$((ATTEMPT + 1))
    fi
done
ENDSSH
    
    echo "✓ Deployment completed"
}

# Configure Cloudflare Access
configure_cloudflare() {
    echo "🔐 Configuring Cloudflare Access..."
    
    # Run the configuration script
    python3 deployment/configure-access.py deployment/access-config.yaml
    
    echo "✓ Cloudflare Access configured"
}

# Post-deployment checks
post_deployment_checks() {
    echo "🔍 Running post-deployment checks..."
    
    # Check public endpoint
    if curl -sf https://image2model.pranitlab.com/api/v1/health/ > /dev/null; then
        echo "✓ Public health endpoint accessible"
    else
        echo "❌ Public health endpoint not accessible"
        return 1
    fi
    
    # Check protected endpoint
    status=$(curl -s -o /dev/null -w "%{http_code}" https://image2model.pranitlab.com/api/v1/models/generate)
    if [ "$status" == "401" ]; then
        echo "✓ Protected endpoints require authentication"
    else
        echo "❌ Protected endpoint returned unexpected status: $status"
        return 1
    fi
    
    echo "✓ All checks passed"
}

# Main deployment flow
main() {
    # Start deployment
    send_slack_notification "warning" "Deployment Started" "Deploying $PROJECT_NAME to $ENVIRONMENT"
    
    # Run deployment steps
    check_env
    build_images
    
    if [ "$SKIP_TESTS" != "true" ]; then
        run_tests
    fi
    
    deploy_to_server
    configure_cloudflare
    post_deployment_checks
    
    # Success notification
    send_slack_notification "good" "Deployment Successful" "$PROJECT_NAME deployed to $ENVIRONMENT successfully!"
    
    echo "✅ Deployment completed successfully!"
}

# Error handling
trap 'handle_error $? $LINENO' ERR

handle_error() {
    local exit_code=$1
    local line_number=$2
    
    echo "❌ Deployment failed at line $line_number with exit code $exit_code"
    send_slack_notification "danger" "Deployment Failed" "$PROJECT_NAME deployment to $ENVIRONMENT failed at line $line_number"
    
    # Cleanup
    rm -f deploy.tar.gz
    
    exit $exit_code
}

# Run main function
main
#!/bin/bash
# Common deployment functions for error handling and rollback

# State file for tracking deployment progress
DEPLOY_STATE_FILE="/tmp/deploy-state-$(date +%s)"
DEPLOY_BACKUP_DIR="/opt/image2model-backup-$(date +%s)"

# Initialize deployment state
init_deployment() {
    echo "DEPLOYMENT_START=$(date +%s)" > "$DEPLOY_STATE_FILE"
    echo "DEPLOYMENT_STATUS=in_progress" >> "$DEPLOY_STATE_FILE"
    echo "ROLLBACK_ENABLED=false" >> "$DEPLOY_STATE_FILE"
}

# Mark deployment stage
mark_stage() {
    local stage=$1
    echo "CURRENT_STAGE=$stage" >> "$DEPLOY_STATE_FILE"
    echo "✓ Entering stage: $stage"
}

# Enable rollback after backup
enable_rollback() {
    echo "ROLLBACK_ENABLED=true" >> "$DEPLOY_STATE_FILE"
    echo "BACKUP_DIR=$DEPLOY_BACKUP_DIR" >> "$DEPLOY_STATE_FILE"
}

# Create backup before deployment
create_backup() {
    mark_stage "backup"
    
    if [ -d "/opt/image2model" ]; then
        echo "📦 Creating backup..."
        mkdir -p "$DEPLOY_BACKUP_DIR"
        
        # Backup current deployment
        cp -r /opt/image2model "$DEPLOY_BACKUP_DIR/" || return 1
        
        # Backup database state
        if docker ps | grep -q image2model-postgres; then
            docker exec image2model-postgres pg_dump -U postgres image2model > "$DEPLOY_BACKUP_DIR/db-backup.sql" || true
        fi
        
        enable_rollback
        echo "✓ Backup created at $DEPLOY_BACKUP_DIR"
    fi
}

# Rollback function
rollback_deployment() {
    echo "🔄 Rolling back deployment..."
    
    if [ -f "$DEPLOY_STATE_FILE" ]; then
        source "$DEPLOY_STATE_FILE"
        
        if [ "$ROLLBACK_ENABLED" = "true" ] && [ -d "$BACKUP_DIR" ]; then
            # Stop current containers
            cd /opt/image2model
            docker compose -f docker-compose.prod.yml down || true
            
            # Restore backup
            rm -rf /opt/image2model
            cp -r "$BACKUP_DIR/image2model" /opt/
            
            # Restart services
            cd /opt/image2model
            docker compose -f docker-compose.prod.yml up -d
            
            # Restore database if backup exists
            if [ -f "$BACKUP_DIR/db-backup.sql" ]; then
                sleep 10
                docker exec -i image2model-postgres psql -U postgres image2model < "$BACKUP_DIR/db-backup.sql" || true
            fi
            
            echo "✓ Rollback completed"
        else
            echo "❌ No backup available for rollback"
        fi
    fi
    
    cleanup_deployment
}

# Cleanup function
cleanup_deployment() {
    rm -f "$DEPLOY_STATE_FILE"
    # Keep backup for 24 hours
    find /opt -name "image2model-backup-*" -mtime +1 -exec rm -rf {} \; 2>/dev/null || true
}

# Error handler
handle_error() {
    local exit_code=$?
    echo "❌ Deployment failed at stage: $(grep CURRENT_STAGE $DEPLOY_STATE_FILE 2>/dev/null | cut -d= -f2)"
    rollback_deployment
    exit $exit_code
}

# Health check with retry
health_check_with_retry() {
    local url=$1
    local max_attempts=${2:-5}
    local wait_time=${3:-15}
    
    for i in $(seq 1 $max_attempts); do
        echo "Attempt $i/$max_attempts: Checking $url"
        if curl -f "$url" >/dev/null 2>&1; then
            echo "✓ Health check passed!"
            return 0
        fi
        
        if [ $i -lt $max_attempts ]; then
            echo "⏳ Waiting ${wait_time}s before retry..."
            sleep $wait_time
        fi
    done
    
    echo "❌ Health check failed after $max_attempts attempts"
    return 1
}

# Export functions
export -f init_deployment mark_stage enable_rollback create_backup rollback_deployment cleanup_deployment handle_error health_check_with_retry
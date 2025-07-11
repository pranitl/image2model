#!/bin/sh
# Redis startup script that generates config with actual password

set -e

# Create config directory
mkdir -p /usr/local/etc/redis

# Generate redis.conf from template with actual password
cat > /usr/local/etc/redis/redis.conf << EOF
# Redis Production Configuration
# Generated at runtime with secure password

# Network and binding (allow connections from Docker network)
bind 0.0.0.0 ::
protected-mode yes
port 6379

# Authentication
requirepass ${REDIS_PASSWORD}

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG ""
rename-command SHUTDOWN ""

# Persistence
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes

# Logging
loglevel notice
logfile ""

# Memory management
maxmemory 1gb
maxmemory-policy allkeys-lru

# Client management
timeout 300
tcp-keepalive 300
maxclients 10000

# Snapshotting
dbfilename dump.rdb
dir /data

# Append only file
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
EOF

# Set proper permissions
chmod 600 /usr/local/etc/redis/redis.conf

# Start Redis with the generated config
exec redis-server /usr/local/etc/redis/redis.conf
# CORS Fix Summary

## Problem
The frontend was calling `http://localhost:8000` instead of `https://image2model.pranitlab.com/api/v1` in production, causing CORS errors.

## Root Cause
Vite doesn't automatically use shell environment variables during build. Even though we set `ENV PUBLIC_API_URL` in the Dockerfile, Vite's build process wasn't picking it up.

## Solution Implemented

### 1. Updated Dockerfile (frontend-svelte/Dockerfile)
Changed line 23 from:
```dockerfile
RUN npm run build
```
to:
```dockerfile
RUN PUBLIC_API_URL=$PUBLIC_API_URL npm run build
```

This explicitly passes the environment variable to the build command where Vite can access it.

### 2. Updated vite.config.js
Added explicit environment variable definition:
```javascript
define: {
  __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  // Explicitly pass PUBLIC_API_URL to the client-side code
  'import.meta.env.PUBLIC_API_URL': JSON.stringify(process.env.PUBLIC_API_URL)
}
```

This ensures Vite replaces `import.meta.env.PUBLIC_API_URL` with the actual value during build.

## How to Deploy

1. Commit these changes
2. Run the deployment script:
   ```bash
   ./deployment/deploy-mvp.sh
   ```

Or manually on the server:
```bash
# SSH to server
ssh root@66.228.60.251

# Navigate to project
cd /opt/image2model

# Pull latest changes
git pull

# Rebuild with --no-cache to ensure fresh build
docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache frontend

# Restart services
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

## Verification

Run the verification script to check if the fix worked:
```bash
./verify-cors-fix.sh
```

This script will:
1. Rebuild the frontend container
2. Check for localhost references in built files
3. Verify the production API URL is present

## Key Lesson
Vite's environment variable system is **build-time only** for client-side code. Environment variables must be available during the build process, not just at runtime.
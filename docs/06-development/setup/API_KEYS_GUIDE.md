# API Keys Guide: Understanding Authentication in the Image2Model Project

This guide explains the different API keys used in the Image2Model project, their purposes, where they're stored, and how they work together to secure the application.

## Overview

The Image2Model project uses multiple API keys for different purposes:
1. **Internal API Key** - For frontend-to-backend communication
2. **FAL.AI API Key** - For external AI model generation services
3. **Admin API Key** - For administrative operations

## 1. Internal API Key (`API_KEY`)

### Purpose
This is the primary authentication key that allows the frontend to communicate securely with the backend API. Think of it as a password that proves the frontend is authorized to make requests to the backend.

### Where It's Stored
- **Environment File**: `/Users/pranit/Documents/AI/image2model/.env`
- **Docker Environment**: Passed as build argument and runtime environment variable
- **Frontend**: Injected at build time and passed via server-side rendering

### How It Works
```
┌─────────────┐    API_KEY     ┌─────────────┐
│   Frontend  │ ────────────► │   Backend   │
│  (Svelte)   │               │  (FastAPI)  │
└─────────────┘               └─────────────┘
```

1. **Backend**: Expects requests to include `Authorization: Bearer {API_KEY}` header
2. **Frontend**: Automatically adds this header to all API requests
3. **Validation**: Backend verifies the key matches before processing requests

### Configuration Files
```bash
# .env file
API_KEY=dev-api-key-123456

# docker-compose.yml (backend)
environment:
  - API_KEY=dev-api-key-123456

# docker-compose.yml (frontend build)
build:
  args:
    API_KEY: ${API_KEY}
```

### SvelteKit Implementation
The API key is passed from server to client using SvelteKit's server-side rendering:

```javascript
// hooks.server.js - Server-side
import { API_KEY } from '$env/static/private';
event.locals.apiKey = API_KEY;

// +layout.server.js - Server load function
export function load({ locals }) {
  return { apiKey: locals.apiKey };
}

// +layout.svelte - Client initialization
onMount(() => {
  if (data.apiKey) {
    api.setApiKey(data.apiKey);
  }
});
```

## 2. FAL.AI API Key (`FAL_API_KEY`)

### Purpose
This key authenticates with FAL.AI's external service for AI model generation. FAL.AI is a third-party service that converts 2D images into 3D models.

### Where It's Stored
- **Environment File**: `/Users/pranit/Documents/AI/image2model/.env`
- **Backend Only**: Only the backend needs access to this key
- **Never Exposed**: This key is never sent to the frontend for security

### How It Works
```
┌─────────────┐               ┌─────────────┐    FAL_API_KEY    ┌─────────────┐
│   Frontend  │ ────────────► │   Backend   │ ─────────────────► │   FAL.AI    │
│             │               │             │                   │   Service   │
└─────────────┘               └─────────────┘                   └─────────────┘
```

1. **User uploads images**: Frontend sends files to backend
2. **Backend processes**: Backend uses FAL.AI key to send images to FAL.AI
3. **Model generation**: FAL.AI generates 3D models and returns them
4. **Results delivered**: Backend returns generated models to frontend

### Security Note
The FAL.AI key is kept secret on the backend to prevent:
- Unauthorized usage of your FAL.AI account
- Exposure of billing/quota information
- Potential abuse by malicious users

## 3. Admin API Key (`ADMIN_API_KEY`)

### Purpose
This key provides elevated privileges for administrative operations like:
- System maintenance
- Bulk operations
- Monitoring and analytics
- User management (if implemented)

### Where It's Stored
- **Environment File**: `/Users/pranit/Documents/AI/image2model/.env`
- **Backend Only**: Only used for backend administrative endpoints
- **Restricted Access**: Should only be known to system administrators

## Environment Variable Configuration

### Development Setup
```bash
# .env file (project root)
API_KEY=dev-api-key-123456                    # Frontend-Backend auth
ADMIN_API_KEY=dev-admin-api-key-789012        # Admin operations
FAL_API_KEY=your-actual-fal-api-key-here      # FAL.AI service
```

### Production Considerations
```bash
# Generate secure random keys for production
API_KEY=$(openssl rand -hex 32)
ADMIN_API_KEY=$(openssl rand -hex 32)
FAL_API_KEY=prod-fal-key-from-account
```

## Why This Setup is Secure

### 1. Environment-Based Configuration
- Keys are stored in environment files, not hardcoded
- Different keys for different environments (dev/staging/prod)
- Keys can be rotated without code changes

### 2. Separation of Concerns
- **Frontend**: Only knows internal API key
- **Backend**: Knows all keys but keeps external ones private
- **External Services**: Only receive their specific keys

### 3. Docker Security
- Keys passed as build arguments (not in image layers)
- Runtime environment variables for dynamic configuration
- No keys exposed in Docker image history

## Common Issues and Solutions

### Issue: "VITE_API_KEY conflict error"
**Cause**: SvelteKit doesn't allow VITE_ prefixed environment variables at runtime
**Solution**: Use server-side rendering to pass keys to client

### Issue: 403 Forbidden errors
**Cause**: API key mismatch between frontend and backend
**Solution**: Ensure same API_KEY value in all configuration files

### Issue: FAL.AI authentication errors
**Cause**: Invalid or missing FAL_API_KEY
**Solution**: Verify FAL.AI account and copy correct key to .env file

## Best Practices

### 1. Key Rotation
- Regularly rotate API keys (monthly/quarterly)
- Use different keys for different environments
- Monitor key usage and access patterns

### 2. Access Control
- Limit who has access to production keys
- Use least-privilege principle
- Document key ownership and responsibility

### 3. Monitoring
- Log authentication attempts (without exposing keys)
- Monitor for unusual API usage patterns
- Set up alerts for authentication failures

### 4. Backup and Recovery
- Securely store backup keys
- Document key recovery procedures
- Test key rotation process regularly

## File Locations Summary

```
image2model/
├── .env                          # Main environment file (all keys)
├── .env.example                  # Template with example values
├── docker-compose.yml            # Docker environment configuration
├── frontend-svelte/
│   ├── src/
│   │   ├── hooks.server.js       # Server-side key loading
│   │   ├── routes/
│   │   │   └── +layout.server.js # Key passing to client
│   │   └── lib/services/api.js   # Client-side key usage
│   └── Dockerfile                # Build-time key injection
└── backend/
    └── app/core/security.py      # Key validation logic
```

This architecture ensures that API keys are handled securely throughout the application while maintaining the flexibility needed for development and deployment.
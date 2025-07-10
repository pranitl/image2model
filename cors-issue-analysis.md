# CORS Issue Analysis - Critical Review

## The Problem
Production site at https://image2model.pranitlab.com is getting CORS errors when trying to access the API:
- Error: "Access to fetch at 'http://localhost:8000/api/v1/upload/' from origin 'https://image2model.pranitlab.com' has been blocked by CORS policy"
- The frontend is trying to call localhost:8000 instead of the production API

## Initial Hypothesis (INCORRECT)
The frontend is not using the production PUBLIC_API_URL and is falling back to localhost:8000. This could be because:
1. The environment variable is not being properly passed to the frontend build
2. The frontend is not being rebuilt with production environment variables
3. There's a caching issue with the built frontend assets

## Critical Analysis - THE ROOT CAUSE

### ❌ The Initial Hypothesis is INCORRECT

The problem is NOT that the frontend isn't using the PUBLIC_API_URL. The actual issue is more fundamental:

### 🔴 THE ROOT CAUSE

**PUBLIC_API_URL is a BUILD-TIME variable in Vite/SvelteKit, but you're trying to set it at RUNTIME in Docker.**

Here's what's happening:

1. **Build Process Issue**: 
   - The Dockerfile builds the frontend WITHOUT the PUBLIC_API_URL variable
   - Line 17 in Dockerfile: `RUN npm run build` - no env vars set here
   - PUBLIC_API_URL is NOT available during build time
   - `import.meta.env.PUBLIC_API_URL` becomes `undefined` in the built code
   - The fallback to 'http://localhost:8000/api/v1' is hardcoded into the production bundle

2. **Runtime Environment Variables Don't Work**:
   - Docker compose sets PUBLIC_API_URL at runtime (line 237)
   - But Vite replaces `import.meta.env.PUBLIC_API_URL` at BUILD time
   - The runtime env var is completely ignored by the already-built frontend

3. **Missing Build Configuration**:
   - No `.env` file in frontend-svelte directory for build
   - Vite config loads env from parent directory (`loadEnv(mode, '../', '')`)
   - But Docker build context doesn't include parent directory env files

### 🎯 Additional Issues Found

1. **Inconsistent Environment Handling**:
   - `svelte.config.js` uses `envPrefix: 'VITE_'` but the env var is `PUBLIC_API_URL`
   - Should be `VITE_PUBLIC_API_URL` or remove the envPrefix restriction

2. **Security Concern**:
   - CSRF protection is disabled (`checkOrigin: false`)
   - This is dangerous in production

3. **Build Context Problem**:
   - Frontend Dockerfile copies only frontend-svelte directory
   - Can't access parent directory .env files during build

### 📊 Ranked Root Causes (by probability)

1. **95% - Build-time vs Runtime Environment Variable Mismatch** ✅
2. **3% - Incorrect env var prefix (VITE_ vs PUBLIC_)**
3. **1% - Docker build context issues**
4. **1% - Caching issues**

### 🛠️ Recommended Fix

The solution requires making PUBLIC_API_URL available at BUILD time:

1. **Option A (Recommended)**: Multi-stage build with build args
   - Pass PUBLIC_API_URL as a Docker build argument
   - Set it during the build stage in Dockerfile

2. **Option B**: Dynamic configuration
   - Create a runtime config endpoint
   - Fetch API URL from the backend at app initialization

3. **Option C**: Build-time env file
   - Create .env.production in frontend-svelte before build
   - Ensure it's available in Docker build context

The fix is straightforward once you understand the build-time vs runtime distinction in Vite/SvelteKit.
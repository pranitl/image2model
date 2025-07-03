# Frontend Migration Guide

## Current Status
- React frontend running on port 3000
- Simple frontend ready in `frontend-simple/`
- Both can run in parallel for testing

## Migration Steps

### Step 1: Test Frontend-Simple Standalone
```bash
# Run the test script
./test-frontend-simple.sh
```

### Step 2: Test Frontend-Simple with Backend
```bash
# Stop current setup
docker-compose down

# Start with both frontends
docker-compose up -d

# Add frontend-simple
docker-compose up -d frontend-simple

# Test simple frontend on http://localhost:3001
# Test React frontend still works on http://localhost:3000
```

### Step 3: Verify Everything Works
Test these flows on http://localhost:3001:
- [ ] Upload multiple images
- [ ] Set face limit
- [ ] Submit and get redirected to processing page
- [ ] See real-time progress updates
- [ ] Get redirected to results page
- [ ] Download individual files
- [ ] Download all files

### Step 4: Switch to Simple Frontend Only
```bash
# Stop everything
docker-compose down

# Use the simple-only compose file
docker-compose -f docker-compose.simple.yml up -d

# Now frontend-simple runs on http://localhost:3000
```

### Step 5: Update Main docker-compose.yml
Once verified working:
1. Remove the `frontend` service (React)
2. Rename `frontend-simple` to `frontend`
3. Update port from 3001 to 3000
4. Remove the old frontend volume

### Step 6: Clean Up (After Everything Works)
```bash
# Remove React frontend directory
rm -rf frontend/

# Remove React-related Docker images
docker rmi image2model-frontend

# Update any documentation
```

## Rollback Plan
If anything goes wrong:
```bash
# Go back to original setup
docker-compose down
git checkout main
docker-compose up -d
```

## Testing Checklist
- [ ] All pages load correctly
- [ ] CSS and JS files load
- [ ] File upload works
- [ ] Progress streaming works (SSE)
- [ ] File downloads work
- [ ] API calls work correctly
- [ ] No console errors
- [ ] No 404 errors
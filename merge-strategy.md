# Safe Merge Strategy for Tasks 2, 3, and 5

## Overview
Three parallel tasks have been completed in separate worktrees. Each implements different pages of the simplified frontend with some overlapping files (mainly CSS).

## Merge Order and Steps

### Step 1: Merge Task 2 (Landing Page)
```bash
# From main branch
git checkout main
git merge task-2-landing-page --no-ff -m "feat: Implement landing page with hero and how-it-works sections (task 2)"
```

**Files added:**
- `frontend-simple/index.html`
- `frontend-simple/css/style.css` (base styles + landing page styles)

### Step 2: Merge Task 3 (Upload Page)
```bash
# Review CSS changes first
git diff task-3-upload-page -- frontend-simple/css/style.css

# Merge with strategy to handle CSS conflict
git merge task-3-upload-page --no-ff -m "feat: Build upload page with drag-and-drop functionality (task 3)"
```

**Files to add:**
- `frontend-simple/upload.html`
- `frontend-simple/js/upload.js`
- `frontend-simple/js/api.js`

**Conflict Resolution for style.css:**
- Keep base styles from Task 2
- Add upload-specific styles from Task 3 (drop-zone, file-list, config-section)

### Step 3: Merge Task 5 (Results Page)
```bash
# Review CSS changes
git diff task-5-results-page -- frontend-simple/css/style.css

# Merge with careful CSS handling
git merge task-5-results-page --no-ff -m "feat: Create results page with download functionality (task 5)"
```

**Files to add:**
- `frontend-simple/results.html`
- `frontend-simple/js/results.js`

**Conflict Resolution for style.css:**
- Keep all existing styles
- Add results-specific styles (model-list, model-item, model-preview, toast animations)

## CSS Consolidation Strategy

Since Task 5 has the most comprehensive CSS file (550 lines), we should:

1. Use Task 5's CSS as the base (it likely includes all necessary styles)
2. Verify no styles are missing from Tasks 2 and 3
3. Remove any duplicates

## Pre-merge Checklist

- [ ] Backup current state: `git stash` or commit current changes
- [ ] Ensure on main branch
- [ ] Review each task's implementation
- [ ] Have CSS diff tool ready for conflict resolution

## Post-merge Verification

1. Test all pages work correctly:
   - Landing page loads and "Start Creating" button works
   - Upload page drag-and-drop and file validation work
   - Results page displays mock data correctly

2. Verify CSS consistency across all pages

3. Check JavaScript console for errors

4. Update task statuses in Task Master

## Alternative Approach (if conflicts are complex)

Instead of merging, manually consolidate:

1. Copy all HTML files from each branch
2. Copy all JS files from each branch  
3. Manually merge CSS files into one comprehensive style.css
4. Test thoroughly
5. Commit as a single consolidated change
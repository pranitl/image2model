# Claude Guide


### Standard Implementation Process

1. `task-master show <id>` - Understand requirements
2. Create feature branch for task
3. `task-master set-status --id=<id> --status=in-progress`
4. Implement code following task requirements
5. Fix any issues found during testing
6. Commit changes with descriptive message
7. `task-master set-status --id=<id> --status=done` - Only after testing passes
8. Merge to main when task complete

## Key Files

- `.taskmaster/tasks/tasks.json` - Main task data (auto-managed)
- `CLAUDE.md` - This file (auto-loaded context)
- `.mcp.json` - MCP server configuration
- `frontend/tests/e2e/` - Playwright test files

## Git Management

- Create branch for each task: `git checkout -b feature/task-description`
- Commit after each subtask completion
- **NEVER update README.md during task work** - only coordinator updates README after all merges
- Reference tasks in commits: `git commit -m "feat: implement feature (task X)"`
- When going through a todo list or phase after planning, for each todo you complete, do a git commit for those relevant files.

## Commands
Always use docker compose not docker-compose

## Testing
When we are making source code changes, we need to ensure we co-develop the test suite so it stays updated!

## UI Development Guidelines

### Visual Consistency Pattern
When implementing UI across different pages:

1. **Use index.html as the source of truth** for styling patterns
2. **Section/Content Pattern**:
   - Body background: Light gray (#f8f9fa)
   - Section backgrounds: Also #f8f9fa (consistent with body)
   - Content containers: White (#ffffff) with subtle shadows
   - This creates visual separation through white cards on gray backgrounds

3. **When to Use Style Overrides**:
   - Inline `<style>` blocks in HTML when theme consistency is critical
   - Explicit color values (#f8f9fa) instead of variables when cross-page consistency is needed
   - Keep overrides minimal and well-documented

4. **CSS File Hierarchy**:
   - `style.css` - Base styles and resets
   - `variables.css` - Color palette and spacing tokens
   - `components.css` - Reusable UI components
   - Page-specific CSS - Unique page layouts
   - Inline overrides - Critical visual consistency

5. **Common Pitfalls to Avoid**:
   - Don't alternate section background colors
   - Don't wrap content in unnecessary containers
   - Don't use tertiary backgrounds for main content
   - Always check how similar sections are styled in index.html

6. **Visual Hierarchy Checklist**:
   - [ ] Gray page background
   - [ ] Gray section backgrounds
   - [ ] White content containers
   - [ ] Subtle shadows and borders
   - [ ] Consistent spacing
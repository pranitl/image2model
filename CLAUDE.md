# Task Master AI - Claude Code Integration Guide

## **CRITICAL: Setup Playwright MCP for Live Testing**

**🚨 MANDATORY SETUP - Run this FIRST in every Claude Code session:**

```bash
claude mcp add playwright npx '@playwright/mcp@latest'
```

**Why This Is Critical:**
- **Early Bug Detection**: Catch UI/UX issues during development, not after
- **Real-time Validation**: Test components as you build them across all browsers
- **Accessibility Compliance**: Ensure components work for all users from day 1
- **Cross-platform Testing**: Mobile, tablet, desktop responsiveness validation

## Essential Commands

### Task Master Core Commands

```bash
# Project Setup
task-master init                                    # Initialize Task Master
task-master parse-prd .taskmaster/docs/prd.txt      # Generate tasks from PRD
task-master models --setup                        # Configure AI models

# Daily Workflow
task-master list                                   # Show all tasks with status
task-master next                                   # Get next available task
task-master show <id>                             # View detailed task information
task-master set-status --id=<id> --status=done    # Mark task complete

# Task Management
task-master expand --id=<id> --research           # Break task into subtasks
task-master update-subtask --id=<id> --prompt="notes"  # Add implementation notes
```

### Testing Commands

```bash
# Interactive testing during development
npm run test:e2e:ui

# Full test suite
npm run test:e2e

# Debug mode
npm run test:e2e:debug
```

## Development Workflow

### Standard Implementation Process

1. `task-master show <id>` - Understand requirements
2. Create feature branch for task
3. `task-master set-status --id=<id> --status=in-progress`
4. Implement code following task requirements
5. **🚨 MANDATORY: Test immediately with Playwright MCP**
6. Fix any issues found during testing
7. Commit changes with descriptive message
8. `task-master set-status --id=<id> --status=done` - Only after testing passes
9. Merge to main when task complete

### Live Testing Workflow (MANDATORY for UI Development)

**For Every UI Component/Feature:**

1. **Build** - Implement the feature
2. **Test Immediately** - Use Playwright MCP to validate:
   - Cross-browser compatibility (Chrome, Firefox, Safari)
   - Mobile responsiveness (iPhone, Android, tablet)
   - Accessibility (keyboard navigation, screen readers)
   - User interactions and error states
3. **Fix Issues** - Don't proceed until testing passes
4. **Document** - Update subtask with testing outcomes

### Testing Checklist

Before marking ANY UI work as "done":

✅ Cross-browser testing ✅ Mobile responsiveness ✅ Accessibility compliance  
✅ Error state handling ✅ User interaction flows ✅ Dark mode compatibility

**If ANY test fails, fix immediately before proceeding.**

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

## Important Notes

### AI-Powered Operations
These commands make AI calls (may take up to a minute):
- `parse-prd`, `expand`, `add-task`, `update-task`, `analyze-complexity`

### File Management
- Never manually edit `tasks.json` - use commands instead
- Use `task-master generate` after manual changes

### Testing Integration
- Playwright MCP server enables live testing during development
- Test suite covers components, workflows, and accessibility
- Use `npm run test:e2e:ui` for interactive testing during development

---

_Streamlined guide for efficient Task Master AI development with mandatory testing validation._
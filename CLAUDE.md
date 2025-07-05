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
Tests need to be run with API_KEY=dev-api-key-123456 environment variable
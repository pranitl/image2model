# Implement Issue Command

## Purpose
This command provides a systematic approach to implementing GitHub issues with comprehensive planning, execution, testing, and documentation.

## Process Overview

### 1. Issue Analysis Phase
```
1. Fetch issue details from GitHub
2. Extract all requirements, deliverables, and acceptance criteria
3. Understand the context and how it relates to existing work
4. Reference brand guidelines and existing documentation
```

### 2. Planning Phase
```
1. Create detailed todo list with 10-15 subtasks
2. Prioritize tasks (high/medium/low)
3. Identify dependencies between tasks
4. Plan the implementation order
```

### 3. Setup Phase
```
1. Create feature branch: `git checkout -b feature/[issue-name]`
2. Set first todo item to "in_progress"
3. Review related files and existing patterns
```

### 4. Implementation Phase
For each todo item:
```
1. Mark current task as "in_progress"
2. Implement the specific feature/change
3. Follow existing code patterns and conventions
4. Reference brand guidelines where applicable
5. Commit changes with descriptive message
6. Mark task as "completed"
7. Move to next task
```

### 5. Testing & Documentation Phase
```
1. Create test files to verify functionality
2. Write accessibility documentation if applicable
3. Create user-facing documentation with examples
4. Build interactive demo pages when relevant
5. Test across different scenarios/viewports
```

### 6. Integration Phase
```
1. Update main files to use new system
2. Remove duplicate/outdated code
3. Ensure backward compatibility
4. Final testing of integrated system
```

### 7. Completion Phase
```
1. Review all todos are marked complete
2. Commit final changes
3. Merge feature branch to main
4. Push to remote repository
5. Comment on issue with detailed summary
6. Close the issue
```

## Detailed Implementation Steps

### Step 1: Analyze the Issue
```bash
# Fetch issue details
gh issue view [issue-number]

# Or use WebFetch for detailed analysis
WebFetch: https://github.com/[owner]/[repo]/issues/[number]
```

### Step 2: Create Todo List
Use TodoWrite to create comprehensive task list based on issue type.

**📋 See `todo-template.md` for specific templates:**
- Design System Implementation (CSS/Styling)
- Feature Implementation
- Bug Fix
- Documentation Update
- Configuration/Setup
- Optimization Task

Example for Design System:
```
1. Create new feature branch for [system name]
2. Research and analyze requirements
3. Review existing implementation
4. Create main CSS file with core definitions
5. Define CSS variables
6. Create utility classes
7. Implement responsive behavior
8. Test accessibility compliance
9. Update existing files
10. Create documentation
11. Build interactive test page
12. Test across viewports
```

### Step 3: Implementation Pattern
For each major file created:
```
1. Core implementation file (e.g., variables.css, typography.css)
2. Utility classes file (e.g., color-utilities.css)
3. Accessibility guide (e.g., color-accessibility.md)
4. Usage documentation (e.g., README.md, guide.md)
5. Interactive test page (e.g., test-colors.html)
```

### Step 4: Git Workflow
```bash
# Create feature branch
git checkout -b feature/[descriptive-name]

# Regular commits after each subtask
git add [files]
git commit -m "feat: [description of what was completed]"

# After all work is complete
git checkout main
git merge feature/[branch-name]
git push origin main
```

### Step 5: Issue Summary Template
When commenting on completed issue:
```markdown
## ✅ [Issue Title] Completed

I've successfully implemented [brief description]. All requirements have been fulfilled and merged to main.

### 📁 What was created:
- **`file1.css`**: Description of what it contains
- **`file2.md`**: Description of documentation
- **`test-file.html`**: Interactive test page

### 🎨 Key Features:
- ✅ Feature 1 with brief description
- ✅ Feature 2 with brief description
- ✅ All acceptance criteria met

### 📝 Implementation Details:
[Key technical decisions and approach]

### 🚀 Usage:
```css
/* Example code snippet */
```

### 📝 Relevant Commits:
- [hash]: commit message
- [hash]: commit message

### 🧪 Testing:
Instructions on how to test the implementation

All acceptance criteria have been met:
- ✅ Criteria 1
- ✅ Criteria 2
```

## Todo List Templates

For detailed todo templates for different types of issues, see **`todo-template.md`**:
- 🎨 Design System Implementation
- 🏗️ Feature Implementation  
- 🐛 Bug Fix
- 📚 Documentation Update
- 🔧 Configuration/Setup
- 🎯 Optimization Task

Each template provides 10-15 specific tasks tailored to that type of work.

## Best Practices

### 1. Always Reference Brand Guidelines
- Check `/brand/guidelines/` for relevant guidance
- Ensure consistency with established patterns
- Use brand colors, typography, and voice

### 2. Comprehensive Documentation
- Create both technical and user-facing docs
- Include code examples and use cases
- Add accessibility considerations
- Provide migration guides when updating existing systems

### 3. Testing Approach
- Create interactive test pages for visual features
- Document all test scenarios
- Verify responsive behavior
- Check accessibility compliance

### 4. Code Organization
- Keep related files together
- Use clear, descriptive file names
- Follow existing project structure
- Maintain modularity

### 5. Communication
- Regular commits with clear messages
- Detailed issue comments
- Reference specific commits in summaries
- Close issues only after full verification

## Example Usage

To implement a new issue:
1. Start with: "Let's work on issue #[number]"
2. I'll analyze and create detailed todos
3. Systematically work through each task
4. Provide regular updates via commits
5. Complete with comprehensive summary

This process ensures:
- Nothing is missed
- Work is well-documented
- Changes are traceable
- Implementation is maintainable
- Users can easily adopt new features
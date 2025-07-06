# Quick Reference: Implement Issue Process

## 📋 The Process I Follow

### 1️⃣ Analyze Issue
- Fetch GitHub issue details
- Extract ALL requirements
- Check brand guidelines in `/brand/`
- Understand context

### 2️⃣ Create Detailed Todos (10-15 items)
**📋 Use templates from `todo-template.md`** based on issue type:
- 🎨 Design System → CSS/styling template
- 🏗️ Feature → Feature implementation template
- 🐛 Bug → Bug fix template
- 📚 Docs → Documentation template
- 🔧 Config → Configuration template
- 🎯 Performance → Optimization template

Example (Design System):
```
1. Create feature branch
2. Research existing code
3. Create main implementation
4. Add configurations/variables
5. Build utility classes
6. Test accessibility
7. Update existing files
8. Write documentation
9. Create test page
10. Verify responsiveness
```

### 3️⃣ Implementation Pattern
For each feature, create:
- **Core file**: Main implementation (e.g., `typography.css`)
- **Utilities**: Helper classes (e.g., `color-utilities.css`)
- **Docs**: Usage guide (e.g., `typography-guide.md`)
- **Accessibility**: Compliance notes (e.g., `typography-accessibility.md`)
- **Test page**: Interactive demo (e.g., `test-typography.html`)

### 4️⃣ Git Workflow
```bash
git checkout -b feature/[name]
# ... implement each todo with commits ...
git add [files] && git commit -m "feat: [what was done]"
# ... after all todos complete ...
git checkout main && git merge feature/[name]
git push origin main
```

### 5️⃣ Complete Issue
1. Add detailed comment with:
   - What was created
   - Key features
   - Usage examples
   - Relevant commits
   - Testing instructions
2. Close issue

## 🎯 Key Principles

- **Break it down**: 10-15 specific subtasks
- **Reference brand**: Use `/brand/guidelines/`
- **Document everything**: Code, usage, accessibility
- **Test thoroughly**: Create demo pages
- **Commit often**: After each subtask
- **Communicate clearly**: Detailed issue summaries

## 📋 Todo Templates
See **`todo-template.md`** for detailed templates:
- Each issue type has a specific template
- Templates include 10-15 tasks
- Tasks are ordered by logical progression
- Includes priority guidelines

Quick format:
```
1. Setup ⬜
2. Research ⬜
3. Core implementation ⬜
4. Supporting features ⬜
5. Testing ⬜
6. Documentation ⬜
7. Integration ⬜
8. Review ⬜
```

## ✅ Success Criteria
- All todos completed
- Tests pass
- Documentation complete
- Merged to main
- Issue closed with summary
# Quick Reference: Implement Issue Process

## 📋 The Process I Follow

### 1️⃣ Analyze Issue
- Fetch GitHub issue details
- Extract ALL requirements
- Check brand guidelines in `/brand/`
- Understand context

### 2️⃣ Create Detailed Todos (10-15 items)
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

## 📝 Todo Template
```
1. Create feature branch ⬜
2. Analyze existing [system] ⬜
3. Create [main file] with [feature] ⬜
4. Define [variables/config] ⬜
5. Implement [core functionality] ⬜
6. Create [utility classes] ⬜
7. Test [accessibility/compliance] ⬜
8. Update [existing files] ⬜
9. Write [documentation] ⬜
10. Build test page ⬜
11. Test responsive behavior ⬜
12. Final review and cleanup ⬜
```

## ✅ Success Criteria
- All todos completed
- Tests pass
- Documentation complete
- Merged to main
- Issue closed with summary
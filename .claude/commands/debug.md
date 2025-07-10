# Debugging Process

When the user asks to debug or help resolve an error, follow these steps:

1. **Understand the Problem**:
   - Clarify the exact error message, stack trace, and observed behavior.
   - Identify the specific code location mentioned in the error or stack trace.
   - Understand the context: What was the user trying to do? What was the expected outcome?

2. **Analyze Test Failures Analytically (If Applicable)**:
   - If the error originates from a test failure (`pytest`, `jest`, etc.):
     - Examine the specific assertion that failed and the expected vs. actual values.
     - Analyze the test setup, fixtures, and mocks involved. Is the test logic correct?
     - Review the code being tested by the failed test case.
     - Read the surrounding logs (`tee` output file) captured during the test run for context.

3. **Reflect on Possible Causes**:
   - Based on the error, context, and test analysis (if applicable), identify 5-7 potential root causes.
   - Consider common error types:
     - Syntax/Typos
     - Logic Errors (conditions, loops, algorithms)
     - Runtime Issues (null/undefined, type mismatches)
     - Dependency/Configuration Issues (versions, missing env vars, incorrect settings)
     - Environment Issues (OS, network, external services like DB/API down)
     - Mocking/Test Setup Errors (incorrect patches, wrong return values)
     - Concurrency/Threading Problems
   - Use project context (`@file package.json`, `@file pyproject.toml`, `@file src/config.py`) to inform hypotheses.

4. **Prioritize Likely Causes**:
   - Distill the list to the 1-2 most probable causes based on:
     - Error message specificity.
     - Test failure details (which assertion failed?).
     - Recent code changes (`@Commit`).
     - Patterns in similar issues or previous debugging steps.
   - Document the rationale for prioritization concisely (internal thought or comment).

5. **Check for Task Dependencies & Create Backlog**:
   - **Crucially, analyze if the likely cause relates to unimplemented functionality or known issues tracked in Task Master.**
   - **If the fix requires code or setup from a PENDING Task:**
     - **Do NOT attempt to implement the fix prematurely.**
     - **Identify the blocking Task ID(s).**
     - **Create or append to a `backlog.md` file** in the project root.
     - **Log the failed test, the identified root cause, and the blocking Task ID(s) in `backlog.md`.** Example entry:
       ```markdown
       ## Test Failures Backlog

       - **File/Test:** `tests/ingestion/test_ingestion.py::test_get_embedding_api_error`
         - **Root Cause:** Test assumes specific error handling for embedding API failures, but the exact handling might depend on Task 7's implementation of robust error strategies.
         - **Blocking Task(s):** Task 7 (Implement Robust Error Handling)
         - **Date Logged:** YYYY-MM-DD
       ```
     - Inform the user you've logged the issue and its dependency, and will return to it after the blocking task is done. Proceed to the next independent task or ask the user.
   - **If the fix seems independent of other tasks, proceed to the next step.**

6. **Add Targeted Logging (If Needed)**:
   - If the cause is still unclear after analysis and isn't blocked by other tasks, *then* consider adding logs.
   - Add minimal, precise logs (`console.log`, `print`) targeting variables or execution flow around the suspected area.
   - For test runs, ensure output is captured: `pytest [options] | tee pytest_<context>_<iteration>.log`.
   - Use file read tool to ensure full log access.

7. **Analyze Logs (If Step 6 Performed)**:
   - Run the code/tests again.
   - Provide log output for analysis.
   - If logs confirm the cause, proceed to fix. If not, revisit step 3 (Reflect on Possible Causes) with new insights.

8. **Implement a Simple, Independent Fix**:
   - **Only if the fix is independent of pending tasks (see Step 5).**
   - Design a solution based on first principles: minimal changes, aligned with project standards (`@file .eslintrc.json`, `@file pyproject.toml`).
   - Include a comment explaining the fix.

9. **Verify the Fix**:
   - Re-run the specific failing test(s) or the application.
   - Capture test output again using `tee`.
   - Check for side effects. If new issues arise, revert and restart from step 3.

10. **Clean Up**:
    - Remove temporary logs unless requested.
    - Ensure code adheres to style guides/linting.
    - Suggest refactoring only if necessary and approved.

## Common Pitfalls to Avoid
- **Fixing Symptoms, Not Causes**: Ensure the fix addresses the root cause identified in the analysis.
- **Implementing Dependent Fixes**: Do not fix issues blocked by pending tasks; log them to `backlog.md` instead.
- **Overcomplicating Fixes**: Prefer minimal, local changes.
- **Ignoring Context/Test Details**: Use `@Commit`, `@file`, test failure details, and logs.
- **Excessive Logging**: Use logging strategically *after* initial analysis fails.
- **Assuming Single Cause**: Iterate if necessary.

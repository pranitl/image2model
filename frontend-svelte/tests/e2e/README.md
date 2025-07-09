# E2E Tests for Image2Model Frontend

This directory contains end-to-end tests for the Image2Model Svelte frontend using Playwright.

## Setup

1. **Install Playwright browsers** (first time only):
   ```bash
   npm run test:e2e:install
   ```

2. **Ensure environment variables are set**:
   The tests require an `API_KEY` in your `.env` file at the project root.

3. **Generate test images**:
   ```bash
   node tests/e2e/utils/create-test-files.js
   ```

## Running Tests

### Run all E2E tests:
```bash
npm run test:e2e
```

### Run tests with UI mode (recommended for development):
```bash
npm run test:e2e:ui
```

### Run tests in headed mode (see browser):
```bash
npm run test:e2e:headed
```

### Debug a specific test:
```bash
npm run test:e2e:debug tests/e2e/upload.spec.js
```

### Generate test code using recorder:
```bash
npm run test:e2e:codegen
```

### View test report after run:
```bash
npm run test:e2e:report
```

## Test Structure

```
tests/e2e/
├── fixtures/
│   ├── test-fixtures.js    # Test fixtures and page object setup
│   └── images/             # Test image files
├── pages/                  # Page Object Models
│   ├── upload.page.js      # Upload page interactions
│   ├── processing.page.js  # Processing page interactions
│   └── results.page.js     # Results page interactions
├── utils/
│   └── create-test-files.js # Utility to generate test images
├── upload.spec.js          # Upload page tests
├── processing.spec.js      # Processing page tests
├── results.spec.js         # Results page tests
├── complete-workflow.spec.js # Full workflow tests
└── global-setup.js         # Global test setup
```

## Test Categories

### Upload Tests (`upload.spec.js`)
- File upload validation
- Drag and drop functionality
- Face limit controls
- Error handling
- File type/size validation

### Processing Tests (`processing.spec.js`)
- Progress tracking
- Real-time updates via SSE
- Error handling
- Cancel functionality
- Connection recovery

### Results Tests (`results.spec.js`)
- Model display
- Download functionality
- Thumbnail loading
- Statistics display
- Navigation

### Workflow Tests (`complete-workflow.spec.js`)
- Complete upload-to-download flow
- Batch processing
- State persistence
- Error recovery
- Network resilience

## Writing New Tests

1. **Use Page Object Models**:
   ```javascript
   test('should upload files', async ({ uploadPage }) => {
     await uploadPage.goto();
     await uploadPage.uploadFiles(['path/to/file.jpg']);
     await uploadPage.submitUpload();
   });
   ```

2. **Use test fixtures for common setup**:
   ```javascript
   import { test, expect } from './fixtures/test-fixtures.js';
   ```

3. **Mock API responses**:
   ```javascript
   test('should handle upload', async ({ mockApi }) => {
     await mockApi.mockSuccessfulUpload();
     // ... test code
   });
   ```

## Debugging Tips

1. **Use `page.pause()` to stop execution**:
   ```javascript
   await page.pause(); // Opens Playwright Inspector
   ```

2. **Take screenshots on failure**:
   Screenshots are automatically saved in `test-results/` when tests fail.

3. **Use `--debug` flag**:
   ```bash
   npx playwright test --debug tests/e2e/upload.spec.js
   ```

4. **Check traces**:
   Traces are saved on retry and can be viewed with:
   ```bash
   npx playwright show-trace trace.zip
   ```

## CI/CD Integration

To run in CI:

```yaml
- name: Install dependencies
  run: npm ci
  
- name: Install Playwright
  run: npx playwright install --with-deps
  
- name: Run E2E tests
  run: npm run test:e2e
  env:
    API_KEY: ${{ secrets.API_KEY }}
```

## Mock Strategies

The tests use several mocking strategies:

1. **API Route Mocking**: Intercept and mock API responses
2. **SSE Stream Mocking**: Simulate server-sent events
3. **File Upload Mocking**: Use minimal test images
4. **Download Mocking**: Simulate file downloads

## Best Practices

1. Keep tests independent and idempotent
2. Use descriptive test names
3. Mock external dependencies
4. Use page objects for reusability
5. Keep selectors maintainable
6. Test both happy paths and error cases
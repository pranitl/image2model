# Testing Guide

## Playwright E2E Testing

This project uses Playwright for end-to-end testing to ensure UI components work correctly across different browsers and devices.

### Setup

Playwright is already configured and installed. The MCP server is set up for live testing during development.

### Running Tests

```bash
# Run all tests headlessly
npm run test:e2e

# Run tests with UI (interactive mode)
npm run test:e2e:ui

# Run tests in debug mode
npm run test:e2e:debug

# View test reports
npm run test:e2e:report
```

### Test Structure

Tests are organized in `tests/e2e/`:

- `component-showcase.spec.ts` - Tests for UI component functionality and accessibility
- `upload-workflow.spec.ts` - Tests for file upload functionality 
- `navigation.spec.ts` - Tests for page navigation and responsive design

### Writing Tests

When implementing new features, follow these guidelines:

1. **Component Testing**: Test all interactive elements, states, and accessibility features
2. **User Workflows**: Test complete user journeys from start to finish
3. **Responsive Design**: Test across mobile, tablet, and desktop viewports
4. **Accessibility**: Ensure keyboard navigation and screen reader compatibility

### Example Test Pattern

```typescript
test('should test feature functionality', async ({ page }) => {
  // Navigate to page
  await page.goto('/feature-page');
  
  // Test element visibility
  await expect(page.getByRole('button', { name: 'Submit' })).toBeVisible();
  
  // Test interactions
  await page.getByRole('button', { name: 'Submit' }).click();
  
  // Test results
  await expect(page.getByText('Success!')).toBeVisible();
});
```

### Test Data

Test fixtures are stored in `tests/fixtures/` for consistent test data.

### Continuous Testing

Tests run automatically in CI/CD and can be run locally during development for immediate feedback on UI changes.

### Live Testing with MCP

The Playwright MCP server enables live testing and interaction with the application during development, allowing for real-time validation of UI components and workflows.
# Visibility Testing Utilities

This directory contains generic, reusable utilities for testing element visibility across the application. These utilities were created to address common visibility issues with animations and provide a scalable testing approach.

## Why These Utilities?

1. **Animation Failures**: Elements with scroll animations were not visible due to JavaScript errors
2. **jsdom Limitations**: Standard visibility checks like `offsetParent` don't work in jsdom
3. **Scalability**: Need consistent visibility testing across different pages and components
4. **Maintenance**: Reduce code duplication and make tests more readable

## Available Utilities

### `isElementVisible(element)`
Checks if an element is visible, working around jsdom limitations.

```javascript
const element = container.querySelector('.my-element');
expect(isElementVisible(element)).toBe(true);
```

### `expectSectionsToBeVisible(container, selectorArray)`
Verifies multiple sections are visible using CSS selectors.

```javascript
expectSectionsToBeVisible(container, [
  '#header',
  '#main-content',
  '#footer'
]);
```

### `expectContentToBeAccessible(container, textArray)`
Ensures text content exists in the DOM (even if parent is hidden).

```javascript
expectContentToBeAccessible(container, [
  'Welcome to our site',
  'Sign up now',
  'Learn more'
]);
```

### `expectAnimationSetup(container, options)`
Validates animation setup on elements.

```javascript
expectAnimationSetup(container, {
  staggedAttribute: 'data-stagger',
  shouldStartVisible: true
});
```

### `testIntersectionObserverSetup(Component, render)`
Tests IntersectionObserver-based animations.

```javascript
const { observerCalls, triggerIntersection } = testIntersectionObserverSetup(Page, render);
// Simulate elements coming into view
triggerIntersection(true);
```

### `testAnimationErrorResilience(Component, render)`
Ensures content remains visible even when animations fail.

```javascript
const { errorContainer, noIOContainer } = testAnimationErrorResilience(Page, render);
// Both containers should have visible content
expectContentToBeAccessible(errorContainer, ['Critical content']);
```

## Usage Examples

### Basic Page Visibility Test

```javascript
import { expectSectionsToBeVisible, expectContentToBeAccessible } from '../lib/visibility-test-utils.js';

it('should display all page sections', () => {
  const { container } = render(MyPage);
  
  expectSectionsToBeVisible(container, [
    '#hero',
    '#features',
    '#testimonials'
  ]);
  
  expectContentToBeAccessible(container, [
    'Welcome to Our Product',
    'Key Features',
    'What Our Users Say'
  ]);
});
```

### Component with Animations

```javascript
it('should handle animations gracefully', () => {
  const { container } = render(AnimatedComponent);
  
  // Check staggered animations
  const cards = container.querySelectorAll('.card');
  cards.forEach(card => {
    expect(isElementVisible(card)).toBe(true);
  });
  
  // Test error resilience
  const { errorContainer } = testAnimationErrorResilience(AnimatedComponent, render);
  expect(isElementVisible(errorContainer.querySelector('.card'))).toBe(true);
});
```

### Conditional Rendering

```javascript
it('should show/hide content based on state', () => {
  const { container } = render(ConditionalComponent);
  
  const loadingState = container.querySelector('.loading');
  const contentState = container.querySelector('.content');
  const errorState = container.querySelector('.error');
  
  // Check current state
  expect(isElementVisible(loadingState)).toBe(true);
  expect(isElementVisible(contentState)).toBe(false);
  expect(isElementVisible(errorState)).toBe(false);
});
```

## Best Practices

1. **Use Generic Utilities First**: Before writing custom visibility checks, see if existing utilities work
2. **Test Error Cases**: Always test what happens when animations or JavaScript fails
3. **Check Content Accessibility**: Ensure important text is in the DOM even if animations haven't triggered
4. **Batch Selectors**: Use arrays with `expectSectionsToBeVisible` for cleaner tests
5. **Document Special Cases**: If you need custom visibility logic, document why

## Common Pitfalls

1. **Svelte Directives**: `use:` directives don't appear in DOM - test their effects instead
2. **Animation Timing**: Elements might start hidden for animations - use `isElementVisible` which handles this
3. **Hidden vs Not Rendered**: `expectContentToBeAccessible` finds hidden text, use `isElementVisible` for strict visibility
4. **jsdom Limitations**: Some CSS properties don't work - our utilities work around these

## Extending the Utilities

When adding new utilities:

1. Keep them generic and reusable
2. Handle edge cases (null elements, missing styles)
3. Work around jsdom limitations
4. Add JSDoc comments
5. Create examples in the examples/ directory

## Related Files

- `visibility-test-utils.js` - The main utilities
- `examples/` - Example usage for different scenarios
- Animation tests that use these utilities
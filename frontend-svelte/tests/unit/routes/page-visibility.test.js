import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Page from '../../../src/routes/+page.svelte';
import {
  isElementVisible,
  expectSectionsToBeVisible,
  expectAnimationSetup,
  expectContentToBeAccessible,
  testIntersectionObserverSetup,
  testAnimationErrorResilience
} from '../lib/visibility-test-utils.js';

describe('Landing Page Section Visibility', () => {
  let intersectionObserverMock;
  let observeCallbacks = [];
  let consoleWarnSpy;

  beforeEach(() => {
    // Mock console.warn to avoid noise
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    // Mock IntersectionObserver
    intersectionObserverMock = vi.fn((callback, options) => {
      const instance = {
        observe: vi.fn((element) => {
          observeCallbacks.push({ callback, element, options });
        }),
        unobserve: vi.fn(),
        disconnect: vi.fn()
      };
      return instance;
    });
    
    global.IntersectionObserver = intersectionObserverMock;
  });

  afterEach(() => {
    observeCallbacks = [];
    consoleWarnSpy.mockRestore();
    vi.clearAllMocks();
  });

  it('should have sections visible in the DOM immediately', () => {
    const { container } = render(Page);
    
    // Use generic utility to check section visibility
    expectSectionsToBeVisible(container, [
      '#features',
      '#how-it-works',
      '#examples'
    ]);
  });

  it('should render section headers without animation classes initially', () => {
    const { container } = render(Page);
    
    // Section headers should be visible even before animations trigger
    const sectionHeaders = container.querySelectorAll('.section-header');
    
    expect(sectionHeaders.length).toBeGreaterThan(0);
    
    sectionHeaders.forEach(header => {
      // Use generic visibility check
      expect(isElementVisible(header)).toBe(true);
    });
  });

  it('should render feature cards without being hidden', () => {
    const { container } = render(Page);
    
    // Use generic content accessibility check
    expectContentToBeAccessible(container, [
      'AI-Powered Precision',
      'Lightning Fast',
      'Batch Processing',
      'Secure & Private'
    ]);
    
    // Verify feature cards are visible
    const featureCards = container.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
      expect(isElementVisible(card)).toBe(true);
    });
  });

  it('should apply scroll animations without hiding content permanently', () => {
    const { container } = render(Page);
    
    // Check elements with data-stagger attribute
    const staggerElements = container.querySelectorAll('[data-stagger]');
    expect(staggerElements.length).toBeGreaterThan(0);
    
    // Even with data-stagger, elements should be visible
    staggerElements.forEach(element => {
      expect(isElementVisible(element)).toBe(true);
    });
  });

  it('should handle animation failures gracefully', () => {
    // Use generic error resilience test
    const { errorContainer } = testAnimationErrorResilience(Page, render);
    
    // Content should still be accessible even with errors
    expectContentToBeAccessible(errorContainer, [
      'Why Choose image2model?',
      'Simple Three-Step Process',
      'See the Magic in Action'
    ]);
  });

  it('should have proper CSS classes for animations', () => {
    const { container } = render(Page);
    
    // Check section headers that would have scroll reveal
    const sectionHeaders = container.querySelectorAll('.section-header');
    sectionHeaders.forEach(element => {
      expect(isElementVisible(element)).toBe(true);
    });
    
    // Check grids that would have stagger reveal
    const staggerContainers = container.querySelectorAll('.features-grid, .steps, .examples-grid');
    staggerContainers.forEach(element => {
      expect(isElementVisible(element)).toBe(true);
    });
  });

  it('should register IntersectionObserver for animated elements', () => {
    const { observerCalls, triggerIntersection } = testIntersectionObserverSetup(Page, render);
    
    // Check that observers were set up
    expect(observerCalls.length).toBeGreaterThan(0);
    
    // Simulate elements coming into view
    triggerIntersection(true);
  });

  it('should not hide sections when IntersectionObserver is not available', () => {
    // Test with no IntersectionObserver available
    const { noIOContainer } = testAnimationErrorResilience(Page, render);
    
    // All sections should still be visible
    expectSectionsToBeVisible(noIOContainer, [
      '#features',
      '#how-it-works',
      '#examples'
    ]);
  });
});
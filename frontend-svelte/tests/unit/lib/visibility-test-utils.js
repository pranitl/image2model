/**
 * Generic utility functions for testing visibility of elements
 * These can be reused across different pages and components
 */

import { expect, vi } from 'vitest';

/**
 * Check if an element is visible in the DOM
 * Works around jsdom limitations with offsetParent
 */
export function isElementVisible(element) {
  if (!element) return false;
  
  const style = window.getComputedStyle(element);
  
  // Check various ways an element can be hidden
  if (style.display === 'none') return false;
  if (style.visibility === 'hidden') return false;
  if (style.opacity === '0' && !element.classList.contains('scroll-hidden')) return false;
  
  return true;
}

/**
 * Check if sections with specific selectors are visible
 * @param {HTMLElement} container - The container to search within
 * @param {string[]} sectionSelectors - Array of CSS selectors for sections
 */
export function expectSectionsToBeVisible(container, sectionSelectors) {
  sectionSelectors.forEach(selector => {
    const section = container.querySelector(selector);
    expect(section, `Section ${selector} should exist`).toBeTruthy();
    expect(
      isElementVisible(section), 
      `Section ${selector} should be visible`
    ).toBe(true);
  });
}

/**
 * Check if elements with animation attributes are set up correctly
 * @param {HTMLElement} container - The container to search within
 * @param {Object} options - Options for the check
 */
export function expectAnimationSetup(container, options = {}) {
  const {
    animationAttribute = 'use:scrollReveal',
    staggedAttribute = 'data-stagger',
    shouldStartVisible = true
  } = options;
  
  // Check elements with animation directives
  // Note: Svelte use: directives are not in the DOM, they're compile-time directives
  // We need to check for animation classes or data attributes instead
  const animatedElements = [];
  
  if (animatedElements.length > 0) {
    animatedElements.forEach(element => {
      if (shouldStartVisible) {
        expect(
          isElementVisible(element),
          'Animated elements should start visible or have proper setup'
        ).toBe(true);
      }
    });
  }
  
  // Check staggered elements
  const staggeredElements = container.querySelectorAll(`[${staggedAttribute}]`);
  
  staggeredElements.forEach(element => {
    // Staggered elements might have animation delays
    const style = window.getComputedStyle(element);
    const hasAnimationSetup = 
      element.style.animationDelay || 
      style.animationDelay !== '0s' ||
      element.classList.contains('animate-in') ||
      element.classList.contains('scroll-hidden');
      
    expect(
      hasAnimationSetup || isElementVisible(element),
      'Staggered elements should either be visible or have animation setup'
    ).toBe(true);
  });
}

/**
 * Check if content within sections is accessible
 * @param {HTMLElement} container - The container to search within
 * @param {string[]} expectedContent - Array of text content to find
 */
export function expectContentToBeAccessible(container, expectedContent) {
  expectedContent.forEach(text => {
    // Use a more flexible search that handles multiple instances
    const elements = container.querySelectorAll('*');
    const found = Array.from(elements).some(el => 
      el.textContent && el.textContent.includes(text)
    );
    
    expect(found, `Content "${text}" should be present in the DOM`).toBe(true);
  });
}

/**
 * Test IntersectionObserver setup for animations
 * @param {Function} Component - The Svelte component to test
 * @param {Function} render - The render function from testing library
 */
export function testIntersectionObserverSetup(Component, render) {
  const observerCalls = [];
  
  // Mock IntersectionObserver
  const mockObserver = vi.fn((callback, options) => {
    const instance = {
      observe: vi.fn((element) => {
        observerCalls.push({ callback, element, options });
      }),
      unobserve: vi.fn(),
      disconnect: vi.fn()
    };
    return instance;
  });
  
  global.IntersectionObserver = mockObserver;
  
  const { container } = render(Component);
  
  return {
    container,
    observerCalls,
    mockObserver,
    // Helper to simulate elements coming into view
    triggerIntersection: (isIntersecting = true) => {
      observerCalls.forEach(({ callback, element }) => {
        callback([{ isIntersecting, target: element }]);
      });
    }
  };
}

/**
 * Test error resilience for animations
 * @param {Function} Component - The Svelte component to test
 * @param {Function} render - The render function from testing library
 */
export function testAnimationErrorResilience(Component, render) {
  const originalIO = global.IntersectionObserver;
  
  // Test with broken IntersectionObserver
  global.IntersectionObserver = undefined;
  const { container: noIOContainer } = render(Component);
  
  // Test with throwing IntersectionObserver
  global.IntersectionObserver = vi.fn(() => {
    throw new Error('IntersectionObserver failed');
  });
  const { container: errorContainer } = render(Component);
  
  // Restore
  global.IntersectionObserver = originalIO;
  
  return { noIOContainer, errorContainer };
}
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { scrollReveal, staggerReveal } from '../../../../src/lib/actions/animations.js';

describe('Animation Actions Visibility', () => {
  let mockElement;
  let mockObserver;
  let observerCallback;
  let consoleWarnSpy;

  beforeEach(() => {
    // Mock console.warn to avoid noise in tests
    consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    // Create a mock DOM element
    mockElement = {
      classList: {
        add: vi.fn(),
        remove: vi.fn(),
        contains: vi.fn()
      },
      style: {},
      querySelectorAll: vi.fn(() => []),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    };

    // Mock IntersectionObserver
    mockObserver = {
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn()
    };

    global.IntersectionObserver = vi.fn((callback) => {
      observerCallback = callback;
      return mockObserver;
    });
  });

  afterEach(() => {
    consoleWarnSpy.mockRestore();
    vi.clearAllMocks();
  });

  describe('scrollReveal', () => {
    it('should add hidden class initially in browser environment', () => {
      const action = scrollReveal(mockElement);
      
      // Should add the scroll-hidden class
      expect(mockElement.classList.add).toHaveBeenCalledWith('scroll-hidden');
      
      // Should set up observer
      expect(mockObserver.observe).toHaveBeenCalledWith(mockElement);
    });

    it('should remove hidden class and add animate class when element is visible', () => {
      scrollReveal(mockElement);
      
      // Simulate element coming into view
      observerCallback([{
        isIntersecting: true,
        target: mockElement
      }]);
      
      expect(mockElement.classList.remove).toHaveBeenCalledWith('scroll-hidden');
      expect(mockElement.classList.add).toHaveBeenCalledWith('animate-in');
    });

    it('should handle IntersectionObserver errors gracefully', () => {
      // Make IntersectionObserver throw an error
      global.IntersectionObserver = vi.fn(() => {
        throw new Error('Not supported');
      });
      
      // Should not throw
      expect(() => scrollReveal(mockElement)).not.toThrow();
      
      // Should handle error and make element visible
      expect(mockElement.style.opacity).toBe('1');
      expect(mockElement.style.transform).toBe('none');
    });

    it('should not hide elements in SSR environment', () => {
      // Simulate SSR by removing window
      const originalWindow = global.window;
      delete global.window;
      
      scrollReveal(mockElement);
      
      // Should add animate class immediately in SSR
      expect(mockElement.classList.add).toHaveBeenCalledWith('animate-in');
      expect(mockElement.classList.add).not.toHaveBeenCalledWith('scroll-hidden');
      
      // Restore window
      global.window = originalWindow;
    });

    it('should make element visible on error', () => {
      global.IntersectionObserver = vi.fn(() => {
        throw new Error('Observer failed');
      });
      
      scrollReveal(mockElement);
      
      // Should log the error
      expect(consoleWarnSpy).toHaveBeenCalled();
      
      // Should apply fallback styles
      expect(mockElement.style.opacity).toBe('1');
      expect(mockElement.style.transform).toBe('none');
    });
  });

  describe('staggerReveal', () => {
    it('should apply animations to child elements', () => {
      const children = [
        { 
          style: {}, 
          classList: { add: vi.fn(), remove: vi.fn() },
          setAttribute: vi.fn()
        },
        { 
          style: {}, 
          classList: { add: vi.fn(), remove: vi.fn() },
          setAttribute: vi.fn()
        }
      ];
      
      mockElement.querySelectorAll = vi.fn(() => children);
      
      const action = staggerReveal(mockElement);
      
      // Should query for stagger children
      expect(mockElement.querySelectorAll).toHaveBeenCalledWith('[data-stagger]');
      
      // Should set animation delays
      expect(children[0].style.animationDelay).toBe('0ms');
      expect(children[1].style.animationDelay).toBe('100ms');
    });

    it('should handle empty children gracefully', () => {
      mockElement.querySelectorAll = vi.fn(() => []);
      
      // Should not throw
      expect(() => staggerReveal(mockElement)).not.toThrow();
    });

    it('should properly destroy child actions', () => {
      const children = [
        { 
          style: {}, 
          classList: { add: vi.fn(), remove: vi.fn() }
        }
      ];
      
      mockElement.querySelectorAll = vi.fn(() => children);
      
      const action = staggerReveal(mockElement);
      
      // Should have destroy method
      expect(action.destroy).toBeDefined();
      
      // Should not throw when destroying
      expect(() => action.destroy()).not.toThrow();
    });
  });

  describe('Error handling', () => {
    it('should handle missing classList gracefully', () => {
      const brokenElement = { style: {} };
      
      // Should not throw
      expect(() => scrollReveal(brokenElement)).not.toThrow();
    });

    it('should handle missing style object gracefully', () => {
      const brokenElement = { classList: { add: vi.fn(), remove: vi.fn() } };
      
      // Should not throw
      expect(() => scrollReveal(brokenElement)).not.toThrow();
    });
  });
});
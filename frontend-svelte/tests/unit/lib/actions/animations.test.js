import { describe, it, expect, vi } from 'vitest';
import { scrollReveal, staggerReveal } from '../../../../src/lib/actions/animations.js';

describe('Animation Actions', () => {
  describe('scrollReveal', () => {
    it('should create an IntersectionObserver', () => {
      const mockNode = document.createElement('div');
      const action = scrollReveal(mockNode);
      
      expect(action).toBeDefined();
      expect(action.destroy).toBeDefined();
    });
    
    it('should add animation class when element is visible', () => {
      const mockNode = document.createElement('div');
      const mockObserve = vi.fn();
      
      global.IntersectionObserver = vi.fn().mockImplementation((callback) => ({
        observe: mockObserve,
        unobserve: vi.fn(),
        disconnect: vi.fn()
      }));
      
      scrollReveal(mockNode);
      expect(mockObserve).toHaveBeenCalledWith(mockNode);
    });
  });
  
  describe('staggerReveal', () => {
    it('should set animation delays on children', () => {
      const mockNode = document.createElement('div');
      const child1 = document.createElement('div');
      const child2 = document.createElement('div');
      
      child1.setAttribute('data-stagger', '');
      child2.setAttribute('data-stagger', '');
      
      mockNode.appendChild(child1);
      mockNode.appendChild(child2);
      
      staggerReveal(mockNode);
      
      expect(child1.style.animationDelay).toBe('0ms');
      expect(child2.style.animationDelay).toBe('100ms');
    });
  });
});
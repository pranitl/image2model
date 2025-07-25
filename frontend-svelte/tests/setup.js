// Test setup file
import '@testing-library/jest-dom';

// Mock IntersectionObserver for animation tests
global.IntersectionObserver = class IntersectionObserver {
  constructor(callback) {
    this.callback = callback;
  }
  
  observe() {
    // Mock implementation
  }
  
  unobserve() {
    // Mock implementation
  }
  
  disconnect() {
    // Mock implementation
  }
};
import { browser } from '$app/environment';

// Error types
export const ErrorTypes = {
  ANIMATION: 'animation',
  NETWORK: 'network',
  VALIDATION: 'validation',
  GENERAL: 'general'
};

// Error severity levels
export const ErrorSeverity = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
};

// Global error handler
class ErrorHandler {
  constructor() {
    this.errors = [];
    this.listeners = new Set();
    
    if (browser) {
      this.setupGlobalHandlers();
    }
  }
  
  setupGlobalHandlers() {
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.logError({
        type: ErrorTypes.GENERAL,
        severity: ErrorSeverity.HIGH,
        message: event.reason?.message || 'Unhandled promise rejection',
        stack: event.reason?.stack,
        timestamp: new Date()
      });
      
      // Prevent default browser behavior
      event.preventDefault();
    });
    
    // Handle global errors
    window.addEventListener('error', (event) => {
      this.logError({
        type: ErrorTypes.GENERAL,
        severity: ErrorSeverity.HIGH,
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack,
        timestamp: new Date()
      });
    });
  }
  
  logError(error) {
    this.errors.push(error);
    
    // Keep only last 50 errors
    if (this.errors.length > 50) {
      this.errors.shift();
    }
    
    // Notify listeners
    this.listeners.forEach(listener => {
      try {
        listener(error);
      } catch (e) {
        console.error('Error in error listener:', e);
      }
    });
    
    // Log to console in development
    if (import.meta.env.DEV) {
      console.error(`[${error.type}] ${error.message}`, error);
    }
  }
  
  addListener(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
  
  getErrors(type = null, severity = null) {
    return this.errors.filter(error => {
      if (type && error.type !== type) return false;
      if (severity && error.severity !== severity) return false;
      return true;
    });
  }
  
  clearErrors() {
    this.errors = [];
  }
}

// Create singleton instance
export const errorHandler = new ErrorHandler();

// Utility function to safely execute code with error handling
export async function safeExecute(fn, options = {}) {
  const {
    type = ErrorTypes.GENERAL,
    severity = ErrorSeverity.MEDIUM,
    fallback = null,
    onError = null
  } = options;
  
  try {
    return await fn();
  } catch (error) {
    errorHandler.logError({
      type,
      severity,
      message: error.message,
      stack: error.stack,
      timestamp: new Date()
    });
    
    if (onError) {
      onError(error);
    }
    
    return fallback;
  }
}

// Animation-specific error handler
export function handleAnimationError(error, element) {
  errorHandler.logError({
    type: ErrorTypes.ANIMATION,
    severity: ErrorSeverity.LOW,
    message: `Animation failed: ${error.message}`,
    element: element?.tagName,
    timestamp: new Date()
  });
  
  // Fallback: show element without animation
  if (element) {
    element.style.opacity = '1';
    element.style.transform = 'none';
  }
}

// Network error handler
export function handleNetworkError(error, url) {
  errorHandler.logError({
    type: ErrorTypes.NETWORK,
    severity: ErrorSeverity.HIGH,
    message: `Network request failed: ${error.message}`,
    url,
    timestamp: new Date()
  });
}

// Form validation error handler
export function handleValidationError(errors, formName) {
  errorHandler.logError({
    type: ErrorTypes.VALIDATION,
    severity: ErrorSeverity.LOW,
    message: 'Form validation failed',
    formName,
    errors,
    timestamp: new Date()
  });
}
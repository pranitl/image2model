/**
 * Frontend error handling utilities for Image2Model application.
 * 
 * Provides error classification, user-friendly message mapping,
 * retry logic, and integration with backend error responses.
 */

export interface APIErrorResponse {
  error: boolean;
  error_code: string;
  message: string;
  status_code: number;
  details: Record<string, any>;
}

export interface ErrorContext {
  component?: string;
  action?: string;
  metadata?: Record<string, any>;
}

export class APIError extends Error {
  public readonly status: number;
  public readonly errorCode: string;
  public readonly details: Record<string, any>;
  public readonly isRetryable: boolean;
  public readonly retryAfter?: number;

  constructor(
    status: number, 
    message: string, 
    errorCode?: string,
    details?: Record<string, any>,
    isRetryable: boolean = false,
    retryAfter?: number
  ) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.errorCode = errorCode || `HTTP_${status}`;
    this.details = details || {};
    this.isRetryable = isRetryable;
    this.retryAfter = retryAfter;
  }

  static fromResponse(response: APIErrorResponse): APIError {
    const isRetryable = response.status_code >= 500 || 
                       response.status_code === 429 ||
                       response.error_code === 'NETWORK_ERROR' ||
                       response.error_code === 'FAL_API_RATE_LIMITED';
    
    const retryAfter = response.details?.retry_after || 
                      (response.status_code === 429 ? 60 : undefined);

    return new APIError(
      response.status_code,
      response.message,
      response.error_code,
      response.details,
      isRetryable,
      retryAfter
    );
  }
}

export class NetworkError extends Error {
  public readonly isRetryable = true;
  public readonly retryAfter = 5; // 5 seconds default

  constructor(message: string = 'Network error occurred') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends Error {
  public readonly field?: string;
  public readonly validationErrors: Array<{
    field: string;
    message: string;
    type: string;
  }>;

  constructor(message: string, validationErrors: any[] = [], field?: string) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
    this.validationErrors = validationErrors;
  }
}

/**
 * Parse and classify errors from various sources
 */
export function parseError(error: any, context?: ErrorContext): APIError | NetworkError | ValidationError | Error {
  // Network errors (fetch failures, connection issues)
  if (!navigator.onLine) {
    return new NetworkError('No internet connection. Please check your network and try again.');
  }

  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return new NetworkError('Unable to connect to server. Please try again.');
  }

  if (error.name === 'AbortError') {
    return new NetworkError('Request was cancelled or timed out.');
  }

  // API response errors
  if (error.response?.data) {
    const responseData = error.response.data;
    
    // Validation errors
    if (responseData.status_code === 422 && responseData.details?.validation_errors) {
      return new ValidationError(
        responseData.message || 'Validation failed',
        responseData.details.validation_errors
      );
    }

    // Standard API errors
    return APIError.fromResponse(responseData);
  }

  // Axios errors
  if (error.response) {
    const status = error.response.status;
    const message = error.response.data?.message || error.message || 'An error occurred';
    
    return new APIError(status, message, `HTTP_${status}`, {}, status >= 500 || status === 429);
  }

  // Request setup errors
  if (error.request) {
    return new NetworkError('Request failed. Please check your connection and try again.');
  }

  // Already processed errors
  if (error instanceof APIError || error instanceof NetworkError || error instanceof ValidationError) {
    return error;
  }

  // Unknown errors
  console.error('Unknown error type:', error, context);
  return new Error(error.message || 'An unexpected error occurred');
}

/**
 * Get user-friendly error message based on error type and code
 */
export function getUserFriendlyMessage(error: any): string {
  if (error instanceof NetworkError) {
    return error.message;
  }

  if (error instanceof ValidationError) {
    if (error.validationErrors.length > 0) {
      return `Validation error: ${error.validationErrors[0].message}`;
    }
    return error.message;
  }

  if (error instanceof APIError) {
    // Specific error code mappings
    switch (error.errorCode) {
      case 'FILE_VALIDATION_ERROR':
        return `File validation failed: ${error.message}`;
      
      case 'FAL_API_RATE_LIMITED':
        const retryMinutes = Math.ceil((error.retryAfter || 60) / 60);
        return `Processing limit reached. Please try again in ${retryMinutes} minute${retryMinutes > 1 ? 's' : ''}.`;
      
      case 'FAL_API_ERROR':
        return 'AI processing service is temporarily unavailable. Please try again later.';
      
      case 'PROCESSING_ERROR':
        return 'Unable to process your request. Please try again or contact support.';
      
      case 'NETWORK_ERROR':
        return 'Connection issue detected. Please check your internet and try again.';
      
      case 'AUTHENTICATION_ERROR':
        return 'Authentication failed. Please refresh the page and try again.';
      
      case 'AUTHORIZATION_ERROR':
        return 'You do not have permission to perform this action.';
      
      case 'DATABASE_ERROR':
        return 'A server error occurred. Please try again later.';
      
      case 'RATE_LIMIT_ERROR':
        return 'Too many requests. Please wait a moment before trying again.';
      
      default:
        // Status-based fallbacks
        switch (error.status) {
          case 400:
            return 'Invalid request. Please check your input and try again.';
          case 401:
            return 'Authentication required. Please refresh the page.';
          case 403:
            return 'Access denied. You do not have permission for this action.';
          case 404:
            return 'The requested resource was not found.';
          case 413:
            return 'File too large. Maximum size is 10MB per file.';
          case 429:
            return 'Too many requests. Please wait a moment before trying again.';
          case 500:
            return 'Server error. Please try again later.';
          case 502:
          case 503:
          case 504:
            return 'Service temporarily unavailable. Please try again later.';
          default:
            return error.message || 'An unexpected error occurred. Please try again.';
        }
    }
  }

  // Generic error fallback
  return error.message || 'An unexpected error occurred. Please try again.';
}

/**
 * Get retry information for an error
 */
export function getRetryInfo(error: any): { canRetry: boolean; retryAfter?: number; suggestedAction?: string } {
  if (error instanceof APIError) {
    return {
      canRetry: error.isRetryable,
      retryAfter: error.retryAfter,
      suggestedAction: error.isRetryable ? 'Please try again' : 'Please contact support if this persists'
    };
  }

  if (error instanceof NetworkError) {
    return {
      canRetry: true,
      retryAfter: error.retryAfter,
      suggestedAction: 'Check your internet connection and try again'
    };
  }

  if (error instanceof ValidationError) {
    return {
      canRetry: false,
      suggestedAction: 'Please correct the validation errors and try again'
    };
  }

  // Default for unknown errors
  return {
    canRetry: true,
    retryAfter: 5,
    suggestedAction: 'Please try again'
  };
}

/**
 * Log error with context for debugging
 */
export function logError(error: any, context?: ErrorContext): void {
  const errorInfo = {
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack,
      ...(error instanceof APIError ? {
        status: error.status,
        errorCode: error.errorCode,
        details: error.details
      } : {})
    },
    context,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
    url: window.location.href
  };

  console.error('Error logged:', errorInfo);

  // In production, you might want to send this to an error tracking service
  if (process.env.NODE_ENV === 'production') {
    // Example: Send to error tracking service
    // sendToErrorTrackingService(errorInfo);
  }
}

/**
 * Enhanced error handler that combines parsing, logging, and user messaging
 */
export function handleError(
  error: any, 
  context?: ErrorContext
): {
  parsedError: Error;
  userMessage: string;
  retryInfo: { canRetry: boolean; retryAfter?: number; suggestedAction?: string };
} {
  const parsedError = parseError(error, context);
  logError(parsedError, context);
  
  return {
    parsedError,
    userMessage: getUserFriendlyMessage(parsedError),
    retryInfo: getRetryInfo(parsedError)
  };
}

/**
 * Create an error boundary error for React components
 */
export function createErrorBoundaryError(error: Error, errorInfo: any) {
  return {
    error,
    errorInfo,
    timestamp: new Date().toISOString(),
    componentStack: errorInfo.componentStack
  };
}

/**
 * Utility to check if an error is retryable
 */
export function isRetryableError(error: any): boolean {
  return getRetryInfo(error).canRetry;
}

/**
 * Utility to get suggested wait time before retry
 */
export function getRetryDelay(error: any, attemptCount: number = 1): number {
  const baseDelay = getRetryInfo(error).retryAfter || 5;
  
  // Exponential backoff with jitter for retries
  const backoffDelay = Math.min(baseDelay * Math.pow(2, attemptCount - 1), 300); // Cap at 5 minutes
  const jitter = Math.random() * 0.1 * backoffDelay; // Add up to 10% jitter
  
  return Math.round(backoffDelay + jitter);
}
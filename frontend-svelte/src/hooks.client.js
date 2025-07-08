import { errorHandler, ErrorTypes, ErrorSeverity } from '$lib/utils/error-handler.js';

/** @type {import('@sveltejs/kit').HandleClientError} */
export function handleError({ error, event, status, message }) {
  // Determine severity based on status code
  let severity = ErrorSeverity.MEDIUM;
  if (status >= 500) severity = ErrorSeverity.CRITICAL;
  else if (status >= 400) severity = ErrorSeverity.HIGH;
  
  // Log the error with our error handler
  errorHandler.logError({
    type: ErrorTypes.GENERAL,
    severity,
    message: message || error?.message || 'Unknown error',
    stack: error?.stack,
    url: event?.url?.href,
    status,
    code: error?.code,
    timestamp: new Date()
  });
  
  // Log to console in development
  if (import.meta.env.DEV) {
    console.error('Client error:', error);
  }
  
  // Return a safe error message for the user
  return {
    message: import.meta.env.DEV 
      ? (message || error?.message || 'An unexpected error occurred')
      : 'An unexpected error occurred. Please try again.',
    code: error?.code ?? 'UNKNOWN'
  };
};
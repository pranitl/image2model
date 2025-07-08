import { handleError } from '@sveltejs/kit';

// Client-side error handling
export const handleError = ({ error, event }) => {
  // Log errors to console in development
  if (import.meta.env.DEV) {
    console.error('Client error:', error);
  }
  
  // You could send errors to a logging service here
  // Example: sendToLoggingService(error, event);
  
  // Return a safe error message for the user
  return {
    message: 'An unexpected error occurred. Please try again.',
    code: error?.code ?? 'UNKNOWN'
  };
};
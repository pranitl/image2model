// Server-side error handling
export async function handleError({ error, event }) {
  // Log errors to console in development
  if (import.meta.env.DEV) {
    console.error('Server error:', error);
  }
  
  // You could send errors to a logging service here
  // Example: await sendToLoggingService(error, event);
  
  // Return a safe error message for the user
  const message = error?.message || 'An unexpected error occurred';
  
  return {
    message: import.meta.env.PROD ? 'Internal Server Error' : message,
    code: error?.code ?? 'UNKNOWN'
  };
}
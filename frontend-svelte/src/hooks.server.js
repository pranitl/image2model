import { env } from '$env/dynamic/private';

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
  // Get API key from runtime environment
  const API_KEY = env.API_KEY || process.env.API_KEY;
  
  // Make API key available to all routes
  event.locals.apiKey = API_KEY;
  
  if (!API_KEY) {
    console.error('API_KEY not found in environment variables');
    throw new Error('API_KEY environment variable is required');
  }
  
  const response = await resolve(event);
  
  // Add security headers
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  
  // Content Security Policy
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://fonts.googleapis.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: blob: https:",
    "connect-src 'self' ws: wss: http://localhost:* http://backend:*",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'"
  ].join('; ');
  
  // Only apply strict CSP in production
  if (import.meta.env.PROD) {
    response.headers.set('Content-Security-Policy', csp);
  }
  
  return response;
}

/** @type {import('@sveltejs/kit').HandleServerError} */
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
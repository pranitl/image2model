export function load({ url }) {
  // Pre-fetch task ID from URL for SSR
  const taskId = url.searchParams.get('batch');
  
  return {
    taskId
  };
}
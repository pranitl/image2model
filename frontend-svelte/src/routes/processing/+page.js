export function load({ url }) {
  // Pre-fetch task ID from URL for SSR - support both 'taskId' and 'batch'
  const taskId = url.searchParams.get('taskId') || url.searchParams.get('batch');
  
  return {
    taskId
  };
}
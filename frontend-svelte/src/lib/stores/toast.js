import { writable } from 'svelte/store';

// Toast types
export const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
};

// Toast store
function createToastStore() {
  const { subscribe, update } = writable([]);
  
  let nextId = 1;
  
  function add(message, type = TOAST_TYPES.INFO, duration = 5000) {
    const id = nextId++;
    const toast = {
      id,
      message,
      type,
      timestamp: Date.now()
    };
    
    update(toasts => [...toasts, toast]);
    
    // Auto-remove after duration
    if (duration > 0) {
      setTimeout(() => {
        remove(id);
      }, duration);
    }
    
    return id;
  }
  
  function remove(id) {
    update(toasts => toasts.filter(t => t.id !== id));
  }
  
  function clear() {
    update(() => []);
  }
  
  return {
    subscribe,
    success: (message, duration) => add(message, TOAST_TYPES.SUCCESS, duration),
    error: (message, duration) => add(message, TOAST_TYPES.ERROR, duration || 8000),
    warning: (message, duration) => add(message, TOAST_TYPES.WARNING, duration),
    info: (message, duration) => add(message, TOAST_TYPES.INFO, duration),
    remove,
    clear
  };
}

export const toast = createToastStore();
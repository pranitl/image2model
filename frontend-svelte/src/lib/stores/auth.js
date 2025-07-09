import { writable } from 'svelte/store';

// Store for managing API key state
export const apiKey = writable(null);

// Helper to check if API key is available
export function hasApiKey() {
  let hasKey = false;
  apiKey.subscribe(value => {
    hasKey = !!value;
  })();
  return hasKey;
}
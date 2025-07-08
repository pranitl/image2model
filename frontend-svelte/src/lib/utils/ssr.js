// SSR-safe utility functions

/**
 * Check if code is running in browser
 */
export const isBrowser = typeof window !== 'undefined';

/**
 * Check if code is running on server
 */
export const isServer = !isBrowser;

/**
 * Safe window access
 */
export const safeWindow = isBrowser ? window : undefined;

/**
 * Safe document access
 */
export const safeDocument = isBrowser ? document : undefined;

/**
 * Run function only in browser
 */
export function onlyInBrowser(fn) {
  if (isBrowser) {
    return fn();
  }
  return null;
}

/**
 * Get safe localStorage
 */
export const safeLocalStorage = {
  getItem: (key) => {
    if (isBrowser && window.localStorage) {
      return window.localStorage.getItem(key);
    }
    return null;
  },
  setItem: (key, value) => {
    if (isBrowser && window.localStorage) {
      window.localStorage.setItem(key, value);
    }
  },
  removeItem: (key) => {
    if (isBrowser && window.localStorage) {
      window.localStorage.removeItem(key);
    }
  }
};

/**
 * Safe matchMedia
 */
export function safeMatchMedia(query) {
  if (isBrowser && window.matchMedia) {
    return window.matchMedia(query);
  }
  return {
    matches: false,
    addListener: () => {},
    removeListener: () => {}
  };
}
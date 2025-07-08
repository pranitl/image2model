<script>
  import { fly } from 'svelte/transition';
  import { toast, TOAST_TYPES } from '$lib/stores/toast.js';
  
  // Icons for different toast types
  const icons = {
    [TOAST_TYPES.SUCCESS]: `<svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
    </svg>`,
    [TOAST_TYPES.ERROR]: `<svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
    </svg>`,
    [TOAST_TYPES.WARNING]: `<svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
    </svg>`,
    [TOAST_TYPES.INFO]: `<svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
    </svg>`
  };
</script>

<div class="toast-container" aria-live="polite" aria-atomic="true">
  {#each $toast as item (item.id)}
    <div
      class="toast toast-{item.type}"
      transition:fly={{ y: 100, duration: 300 }}
    >
      <div class="toast-icon">
        {@html icons[item.type]}
      </div>
      <div class="toast-message">
        {item.message}
      </div>
      <button
        class="toast-close"
        on:click={() => toast.remove(item.id)}
        aria-label="Close notification"
      >
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
        </svg>
      </button>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    bottom: 1rem;
    right: 1rem;
    z-index: 9999;
    pointer-events: none;
  }
  
  .toast {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: white;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    max-width: 400px;
    pointer-events: auto;
    border-left: 4px solid;
  }
  
  .toast-success {
    border-left-color: #27AE60;
  }
  
  .toast-success .toast-icon {
    color: #27AE60;
  }
  
  .toast-error {
    border-left-color: #E74C3C;
  }
  
  .toast-error .toast-icon {
    color: #E74C3C;
  }
  
  .toast-warning {
    border-left-color: #F39C12;
  }
  
  .toast-warning .toast-icon {
    color: #F39C12;
  }
  
  .toast-info {
    border-left-color: #3498DB;
  }
  
  .toast-info .toast-icon {
    color: #3498DB;
  }
  
  .toast-icon {
    flex-shrink: 0;
  }
  
  .toast-message {
    flex: 1;
    color: #2c3e50;
    font-size: 0.875rem;
    line-height: 1.5;
  }
  
  .toast-close {
    flex-shrink: 0;
    background: none;
    border: none;
    padding: 0.25rem;
    cursor: pointer;
    color: #95a5a6;
    transition: color 0.2s;
  }
  
  .toast-close:hover {
    color: #2c3e50;
  }
  
  @media (max-width: 640px) {
    .toast-container {
      left: 1rem;
      right: 1rem;
    }
    
    .toast {
      max-width: none;
    }
  }
</style>
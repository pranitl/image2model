<script>
  import { onMount, onDestroy } from 'svelte';
  import { errorHandler } from '$lib/utils/error-handler.js';
  
  export let fallback = null;
  export let onError = null;
  
  let hasError = false;
  let error = null;
  let unsubscribe;
  
  onMount(() => {
    // Listen for errors
    unsubscribe = errorHandler.addListener((err) => {
      hasError = true;
      error = err;
      
      if (onError) {
        onError(err);
      }
    });
  });
  
  onDestroy(() => {
    if (unsubscribe) {
      unsubscribe();
    }
  });
  
  function retry() {
    hasError = false;
    error = null;
  }
</script>

{#if hasError}
  {#if fallback}
    <svelte:component this={fallback} {error} {retry} />
  {:else}
    <div class="error-boundary">
      <div class="error-content">
        <h2>Something went wrong</h2>
        <p>We encountered an unexpected error. Please try again.</p>
        <button class="btn btn-primary" on:click={retry}>
          Try Again
        </button>
        {#if import.meta.env.DEV}
          <details class="error-details">
            <summary>Error Details</summary>
            <pre>{JSON.stringify(error, null, 2)}</pre>
          </details>
        {/if}
      </div>
    </div>
  {/if}
{:else}
  <slot />
{/if}

<style>
  .error-boundary {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    padding: 2rem;
  }
  
  .error-content {
    text-align: center;
    max-width: 500px;
  }
  
  .error-content h2 {
    color: var(--color-danger);
    margin-bottom: 1rem;
  }
  
  .error-content p {
    margin-bottom: 2rem;
    color: var(--color-text-secondary);
  }
  
  .error-details {
    margin-top: 2rem;
    text-align: left;
  }
  
  .error-details summary {
    cursor: pointer;
    color: var(--color-text-secondary);
    margin-bottom: 0.5rem;
  }
  
  .error-details pre {
    background: var(--color-background-secondary);
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 0.875rem;
  }
</style>
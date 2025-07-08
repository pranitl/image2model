<script>
  import { createEventDispatcher } from 'svelte';
  
  /**
   * @type {'primary'|'secondary'|'ghost'|'ghost-light'} variant - Visual style variant
   * @default 'primary'
   */
  export let variant = 'primary';
  
  /**
   * @type {'sm'|'md'|'lg'} size - Button size
   * @default 'md'
   */
  export let size = 'md';
  
  /**
   * @type {boolean} disabled - Whether the button is disabled
   * @default false
   */
  export let disabled = false;
  
  /**
   * @type {string} type - HTML button type attribute
   * @default 'button'
   */
  export let type = 'button';
  
  /**
   * @type {string|null} href - If provided, renders as an anchor link instead of button
   * @default null
   */
  export let href = null;
  
  /**
   * @type {boolean} fullWidth - Whether button should take full container width
   * @default false
   */
  export let fullWidth = false;
  
  /**
   * @type {boolean} loading - Shows loading spinner and disables interaction
   * @default false
   */
  export let loading = false;
  
  const dispatch = createEventDispatcher();
  
  // Extract class from $$restProps to avoid unknown prop warning
  let className = '';
  $: className = $$restProps.class || '';
  
  function handleClick(e) {
    if (!disabled && !loading) {
      dispatch('click', e);
    }
  }
  
  $: classes = [
    'btn',
    `btn-${variant}`,
    `btn-${size}`,
    fullWidth && 'btn-full',
    (disabled || loading) && 'btn-disabled',
    'hover-lift',
    className
  ].filter(Boolean).join(' ');
</script>

{#if href && !disabled && !loading}
  <a {href} class={classes} {...$$restProps}>
    {#if loading}
      <span class="btn-spinner"></span>
    {/if}
    <slot name="icon" />
    <slot />
  </a>
{:else}
  <button 
    {type}
    class={classes}
    disabled={disabled || loading}
    on:click={handleClick}
    {...$$restProps}
  >
    {#if loading}
      <span class="btn-spinner"></span>
    {/if}
    <slot name="icon" />
    <slot />
  </button>
{/if}

<style>
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1rem;
    line-height: 1;
    position: relative;
    overflow: hidden;
  }

  /* Sizes */
  .btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }

  .btn-md {
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
  }

  .btn-lg {
    padding: 1rem 2rem;
    font-size: 1.125rem;
  }

  /* Variants */
  .btn-primary {
    background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
    color: white;
    box-shadow: 0 4px 14px 0 rgba(33, 150, 243, 0.25);
  }

  .btn-primary:hover:not(.btn-disabled) {
    background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(33, 150, 243, 0.35);
  }

  .btn-secondary {
    background: #f3f4f6;
    color: #1a202c;
    border: 1px solid #e5e7eb;
  }

  .btn-secondary:hover:not(.btn-disabled) {
    background: #e5e7eb;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }

  .btn-ghost {
    background: transparent;
    color: #4b5563;
    border: 1px solid #e5e7eb;
  }

  .btn-ghost:hover:not(.btn-disabled) {
    background: #f9fafb;
    border-color: #d1d5db;
    transform: translateY(-1px);
  }

  /* Ghost variant for dark backgrounds */
  .btn-ghost-light {
    background: transparent;
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
  }

  .btn-ghost-light:hover:not(.btn-disabled) {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-1px);
    color: white;
  }

  /* States */
  .btn-disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-full {
    width: 100%;
  }

  /* Loading spinner */
  .btn-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Hover lift effect */
  .hover-lift {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }

  .hover-lift:hover:not(.btn-disabled) {
    transform: translateY(-2px);
  }

  /* Active state */
  .btn:active:not(.btn-disabled) {
    transform: translateY(0);
  }

  /* Focus state */
  .btn:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
  }

  /* Global icon styles within buttons */
  :global(.btn svg) {
    width: 1.25em;
    height: 1.25em;
    flex-shrink: 0;
  }
</style>
<script>
  import { staggerReveal } from '$lib/actions/animations';
  import Icon from './Icon.svelte';
  
  export let items = [];
  export let onRemove = null; // Optional remove handler
  export let showOverlay = false; // For processing state
  export let overlayContent = null; // Custom overlay content
  
  // Grid sizing classes
  export let gridSize = 'medium'; // small, medium, large
  
  const gridClasses = {
    small: 'grid-small',
    medium: 'grid-medium',
    large: 'grid-large'
  };
</script>

<div class="image-grid {gridClasses[gridSize]}" use:staggerReveal>
  {#each items as item (item.id)}
    <div class="image-tile" data-stagger>
      <div class="tile-content">
        <img 
          src={item.preview || item.image} 
          alt={item.name || item.filename} 
          class="tile-image" 
          loading="lazy"
        />
        
        {#if showOverlay && item.showOverlay !== false}
          <div class="tile-overlay">
            {#if overlayContent}
              {@html overlayContent}
            {:else if item.status === 'processing' || item.processing}
              <div class="spinner"></div>
            {:else if item.status === 'completed'}
              <Icon name="check-circle" size={32} color="white" />
            {:else if item.status === 'failed'}
              <Icon name="x-circle" size={32} color="white" />
            {/if}
          </div>
        {/if}
        
        {#if onRemove && !showOverlay}
          <button 
            type="button" 
            class="tile-remove" 
            on:click={() => onRemove(item.id)}
            aria-label="Remove {item.name || item.filename}"
          >
            <Icon name="x" size={20} />
          </button>
        {/if}
      </div>
      
      {#if item.name || item.filename}
        <div class="tile-footer">
          <span class="tile-name">{item.name || item.filename}</span>
          {#if item.status}
            <span class="tile-status status-{item.status}">{item.statusText || item.status}</span>
          {/if}
        </div>
      {/if}
      
      <slot name="tile-content" {item} />
    </div>
  {/each}
</div>

<style>
  .image-grid {
    display: grid;
    gap: 1rem;
    width: 100%;
  }

  /* Grid sizes */
  .grid-small {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }

  .grid-medium {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }

  .grid-large {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }

  @media (max-width: 768px) {
    .grid-medium,
    .grid-large {
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    }
  }

  .image-tile {
    position: relative;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .image-tile:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }

  .tile-content {
    position: relative;
    aspect-ratio: 1;
    overflow: hidden;
    background: #f8f9fa;
  }

  .tile-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }

  .image-tile:hover .tile-image {
    transform: scale(1.05);
  }

  /* Overlay for processing/status */
  .tile-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.2s ease;
  }

  /* Remove button */
  .tile-remove {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.6);
    border: none;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s ease, background-color 0.2s ease;
  }

  .image-tile:hover .tile-remove {
    opacity: 1;
  }

  .tile-remove:hover {
    background: rgba(239, 68, 68, 0.8);
  }

  .tile-remove:focus {
    outline: 2px solid white;
    outline-offset: -4px;
    opacity: 1;
  }

  /* Footer with name and status */
  .tile-footer {
    padding: 0.75rem;
    background: white;
    border-top: 1px solid #f1f5f9;
  }

  .tile-name {
    display: block;
    font-size: 0.875rem;
    color: #1e293b;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .tile-status {
    display: block;
    font-size: 0.75rem;
    margin-top: 0.25rem;
    font-weight: 500;
  }

  .status-pending {
    color: #94a3b8;
  }

  .status-processing {
    color: #5dade2;
  }

  .status-completed {
    color: #22c55e;
  }

  .status-failed {
    color: #ef4444;
  }

  /* Spinner for processing state */
  .spinner {
    width: 2.5rem;
    height: 2.5rem;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spinner 0.8s linear infinite;
  }

  @keyframes spinner {
    to { transform: rotate(360deg); }
  }

  /* Support for slots */
  :global(.image-tile slot) {
    display: contents;
  }
</style>
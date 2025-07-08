<script>
  export let items = [];
  export let current = '';
</script>

<section class="breadcrumb-section">
  <div class="container">
    <nav aria-label="Breadcrumb" class="breadcrumb animate-fade-in">
      {#each items as item, i}
        <div class="breadcrumb-item">
          {#if item.href && !item.current}
            <a href={item.href}>{item.label}</a>
          {:else if item.current}
            <span class="breadcrumb-current">{item.label}</span>
          {:else}
            <span>{item.label}</span>
          {/if}
          {#if i < items.length - 1}
            <span class="breadcrumb-separator">→</span>
          {/if}
        </div>
      {/each}
    </nav>
  </div>
</section>

<style>
  .breadcrumb-section {
    background: #f8f9fa;
    padding: 1rem 0;
    margin-top: 70px; /* Account for fixed navbar */
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  .breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .breadcrumb-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
  }

  .breadcrumb-item a {
    color: #4b5563;
    text-decoration: none;
    transition: color 0.3s ease;
  }

  .breadcrumb-item a:hover {
    color: #2196f3;
  }

  .breadcrumb-item span:not(.breadcrumb-separator) {
    color: #6b7280;
  }

  .breadcrumb-current {
    color: #2196f3 !important;
    font-weight: 600;
  }

  .breadcrumb-separator {
    color: #d1d5db;
    font-size: 0.75rem;
  }

  /* Mobile responsiveness */
  @media (max-width: 640px) {
    .breadcrumb {
      font-size: 0.8125rem;
    }
    
    .breadcrumb-separator {
      margin: 0 0.25rem;
    }
  }

  /* Animation */
  :global(.animate-fade-in) {
    animation: fadeIn 0.6s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
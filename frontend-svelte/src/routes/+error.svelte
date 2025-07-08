<script>
  import { page } from '$app/stores';
</script>

<div class="error-container">
  <div class="error-content">
    <h1 class="error-title">
      {$page.status === 404 ? 'Page Not Found' : 'Oops! Something went wrong'}
    </h1>
    
    <p class="error-code">{$page.status}</p>
    
    <p class="error-message">
      {#if $page.status === 404}
        The page you're looking for doesn't exist.
      {:else if $page.status === 500}
        We encountered an internal server error. Please try again later.
      {:else}
        {$page.error?.message || 'An unexpected error occurred.'}
      {/if}
    </p>
    
    <div class="error-actions">
      <a href="/" class="btn btn-primary">Go to Homepage</a>
      <button class="btn btn-secondary" on:click={() => window.history.back()}>
        Go Back
      </button>
    </div>
  </div>
</div>

<style>
  .error-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);
  }
  
  .error-content {
    text-align: center;
    max-width: 600px;
    padding: 3rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }
  
  .error-title {
    color: #ffffff;
    font-size: 2rem;
    margin-bottom: 1rem;
    font-weight: 700;
  }
  
  .error-code {
    font-size: 5rem;
    color: #5dade2;
    font-weight: 700;
    margin: 1rem 0;
    line-height: 1;
  }
  
  .error-message {
    color: #ecf0f1;
    font-size: 1.125rem;
    margin-bottom: 2rem;
  }
  
  .error-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .btn {
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    display: inline-block;
    border: none;
    cursor: pointer;
    font-size: 1rem;
  }
  
  .btn-primary {
    background: linear-gradient(135deg, #5dade2 0%, #3498db 100%);
    color: #ffffff;
  }
  
  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(93, 173, 226, 0.4);
  }
  
  .btn-secondary {
    background-color: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    border: 2px solid rgba(255, 255, 255, 0.3);
  }
  
  .btn-secondary:hover {
    background-color: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.5);
  }
  
  @media (max-width: 640px) {
    .error-title {
      font-size: 1.5rem;
    }
    
    .error-code {
      font-size: 4rem;
    }
    
    .error-actions {
      flex-direction: column;
    }
    
    .btn {
      width: 100%;
    }
  }
</style>
<script>
  import { onMount } from 'svelte';
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import { toast } from '$lib/stores/toast.js';
  
  // Demo toast states
  let showStaticToasts = true;
  
  function showSuccessToast() {
    toast.success('Operation completed successfully!');
  }
  
  function showErrorToast() {
    toast.error('An error occurred while processing your request.');
  }
  
  function showInfoToast() {
    toast.info('This is an informational message.');
  }
  
  function showWarningToast() {
    toast.warning('Please review your settings before continuing.');
  }
  
  function showLongToast() {
    toast.success('This is a longer toast message that demonstrates how the toast component handles multiline text content. It will wrap nicely and maintain proper spacing.', 5000);
  }
  
  function showCustomToast() {
    toast.show({
      message: 'Custom toast with action',
      type: 'info',
      duration: 10000,
      action: {
        label: 'Undo',
        onClick: () => {
          toast.success('Action undone!');
        }
      }
    });
  }
  
  function showMultipleToasts() {
    toast.success('First toast message');
    setTimeout(() => toast.info('Second toast message'), 300);
    setTimeout(() => toast.warning('Third toast message'), 600);
  }
  
  function showPersistentToast() {
    toast.show({
      message: 'This toast will not auto-dismiss',
      type: 'info',
      duration: 0 // 0 means persistent
    });
  }
</script>

<Navbar />

<main class="component-gallery">
  <Hero 
    title="Toast Components Gallery"
    subtitle="Toast notifications and alert messages"
  />
  
  <section class="gallery-content">
    <div class="container">
      <!-- Toast Types -->
      <div class="component-section">
        <h2>Toast Types</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Success Toast</h3>
            <div class="demo-area">
              <div class="toast toast-success">
                <div class="toast-icon">
                  <Icon name="check-circle" size={20} />
                </div>
                <div class="toast-content">
                  <p class="toast-message">Your changes have been saved successfully!</p>
                </div>
                <button class="toast-close">
                  <Icon name="x" size={16} />
                </button>
              </div>
            </div>
            <div class="demo-actions">
              <Button variant="primary" size="sm" on:click={showSuccessToast}>
                Show Live Toast
              </Button>
            </div>
          </div>

          <div class="component-demo">
            <h3>Error Toast</h3>
            <div class="demo-area">
              <div class="toast toast-error">
                <div class="toast-icon">
                  <Icon name="x-circle" size={20} />
                </div>
                <div class="toast-content">
                  <p class="toast-message">Failed to upload file. Please try again.</p>
                </div>
                <button class="toast-close">
                  <Icon name="x" size={16} />
                </button>
              </div>
            </div>
            <div class="demo-actions">
              <Button variant="primary" size="sm" on:click={showErrorToast}>
                Show Live Toast
              </Button>
            </div>
          </div>

          <div class="component-demo">
            <h3>Info Toast</h3>
            <div class="demo-area">
              <div class="toast toast-info">
                <div class="toast-icon">
                  <Icon name="info" size={20} />
                </div>
                <div class="toast-content">
                  <p class="toast-message">New features are available in settings.</p>
                </div>
                <button class="toast-close">
                  <Icon name="x" size={16} />
                </button>
              </div>
            </div>
            <div class="demo-actions">
              <Button variant="primary" size="sm" on:click={showInfoToast}>
                Show Live Toast
              </Button>
            </div>
          </div>

          <div class="component-demo">
            <h3>Warning Toast</h3>
            <div class="demo-area">
              <div class="toast toast-warning">
                <div class="toast-icon">
                  <Icon name="alert-triangle" size={20} />
                </div>
                <div class="toast-content">
                  <p class="toast-message">Your session will expire in 5 minutes.</p>
                </div>
                <button class="toast-close">
                  <Icon name="x" size={16} />
                </button>
              </div>
            </div>
            <div class="demo-actions">
              <Button variant="primary" size="sm" on:click={showWarningToast}>
                Show Live Toast
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Toast Variations -->
      <div class="component-section">
        <h2>Toast Variations</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Toast with Action</h3>
            <div class="demo-area">
              <div class="toast toast-info">
                <div class="toast-icon">
                  <Icon name="info" size={20} />
                </div>
                <div class="toast-content">
                  <p class="toast-message">File deleted from your library.</p>
                </div>
                <button class="toast-action">Undo</button>
                <button class="toast-close">
                  <Icon name="x" size={16} />
                </button>
              </div>
            </div>
            <div class="demo-actions">
              <Button variant="primary" size="sm" on:click={showCustomToast}>
                Show Live Toast
              </Button>
            </div>
          </div>

          <div class="component-demo">
            <h3>Long Message Toast</h3>
            <div class="demo-area">
              <div class="toast toast-success">
                <div class="toast-icon">
                  <Icon name="check-circle" size={20} />
                </div>
                <div class="toast-content">
                  <p class="toast-message">
                    Your 3D models have been generated successfully. 
                    You can now download them or continue editing in the viewer.
                  </p>
                </div>
                <button class="toast-close">
                  <Icon name="x" size={16} />
                </button>
              </div>
            </div>
            <div class="demo-actions">
              <Button variant="primary" size="sm" on:click={showLongToast}>
                Show Live Toast
              </Button>
            </div>
          </div>

          <div class="component-demo">
            <h3>Loading Toast</h3>
            <div class="demo-area">
              <div class="toast toast-info">
                <div class="toast-icon spinning">
                  <Icon name="loader" size={20} />
                </div>
                <div class="toast-content">
                  <p class="toast-message">Processing your request...</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Toast Stack -->
      <div class="component-section">
        <h2>Toast Stacking</h2>
        <div class="component-grid large">
          <div class="component-demo">
            <h3>Multiple Toasts</h3>
            <div class="demo-area">
              <div class="toast-stack">
                <div class="toast toast-success">
                  <div class="toast-icon">
                    <Icon name="check-circle" size={20} />
                  </div>
                  <div class="toast-content">
                    <p class="toast-message">First notification</p>
                  </div>
                  <button class="toast-close">
                    <Icon name="x" size={16} />
                  </button>
                </div>
                <div class="toast toast-info">
                  <div class="toast-icon">
                    <Icon name="info" size={20} />
                  </div>
                  <div class="toast-content">
                    <p class="toast-message">Second notification</p>
                  </div>
                  <button class="toast-close">
                    <Icon name="x" size={16} />
                  </button>
                </div>
                <div class="toast toast-warning">
                  <div class="toast-icon">
                    <Icon name="alert-triangle" size={20} />
                  </div>
                  <div class="toast-content">
                    <p class="toast-message">Third notification</p>
                  </div>
                  <button class="toast-close">
                    <Icon name="x" size={16} />
                  </button>
                </div>
              </div>
            </div>
            <div class="demo-actions">
              <Button variant="primary" size="sm" on:click={showMultipleToasts}>
                Show Multiple Toasts
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Alert Boxes -->
      <div class="component-section">
        <h2>Alert Boxes (Static)</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Success Alert</h3>
            <div class="demo-area">
              <div class="alert alert-success">
                <div class="alert-icon">
                  <Icon name="check-circle" size={24} />
                </div>
                <div class="alert-content">
                  <h4 class="alert-title">Success!</h4>
                  <p class="alert-message">Your payment has been processed successfully.</p>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Error Alert</h3>
            <div class="demo-area">
              <div class="alert alert-error">
                <div class="alert-icon">
                  <Icon name="x-circle" size={24} />
                </div>
                <div class="alert-content">
                  <h4 class="alert-title">Error</h4>
                  <p class="alert-message">Unable to connect to the server. Please check your connection.</p>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Info Alert</h3>
            <div class="demo-area">
              <div class="alert alert-info">
                <div class="alert-icon">
                  <Icon name="info" size={24} />
                </div>
                <div class="alert-content">
                  <h4 class="alert-title">Information</h4>
                  <p class="alert-message">System maintenance scheduled for tonight at 2:00 AM EST.</p>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Warning Alert</h3>
            <div class="demo-area">
              <div class="alert alert-warning">
                <div class="alert-icon">
                  <Icon name="alert-triangle" size={24} />
                </div>
                <div class="alert-content">
                  <h4 class="alert-title">Warning</h4>
                  <p class="alert-message">Your storage is almost full. Consider upgrading your plan.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Interactive Demo -->
      <div class="component-section">
        <h2>Interactive Demo</h2>
        <div class="demo-panel">
          <h3>Try Different Toast Types</h3>
          <div class="button-grid">
            <Button variant="success" on:click={showSuccessToast}>
              Success Toast
            </Button>
            <Button variant="danger" on:click={showErrorToast}>
              Error Toast
            </Button>
            <Button variant="primary" on:click={showInfoToast}>
              Info Toast
            </Button>
            <Button variant="warning" on:click={showWarningToast}>
              Warning Toast
            </Button>
            <Button variant="secondary" on:click={showLongToast}>
              Long Toast
            </Button>
            <Button variant="secondary" on:click={showCustomToast}>
              Toast with Action
            </Button>
            <Button variant="secondary" on:click={showMultipleToasts}>
              Multiple Toasts
            </Button>
            <Button variant="secondary" on:click={showPersistentToast}>
              Persistent Toast
            </Button>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Back to Dev -->
  <section class="dev-nav">
    <div class="container">
      <Button href="/dev" variant="ghost">← Back to Dev Dashboard</Button>
    </div>
  </section>
</main>

<Footer />

<style>
  .component-gallery {
    min-height: 100vh;
    background-color: #f8f9fa;
  }

  .gallery-content {
    padding: 4rem 0;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }

  .component-section {
    margin-bottom: 4rem;
  }

  .component-section h2 {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e2e8f0;
  }

  .component-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 2rem;
  }

  .component-grid.large {
    grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
  }

  .component-demo {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .component-demo h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 1rem;
  }

  .demo-area {
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 1rem;
    min-height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .demo-actions {
    display: flex;
    justify-content: center;
    padding-top: 0.5rem;
  }

  /* Toast styles */
  .toast {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    max-width: 400px;
    position: relative;
  }

  .toast-icon {
    flex-shrink: 0;
  }

  .toast-icon.spinning {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .toast-content {
    flex: 1;
  }

  .toast-message {
    margin: 0;
    font-size: 0.875rem;
    line-height: 1.5;
    color: #1e293b;
  }

  .toast-close {
    flex-shrink: 0;
    background: none;
    border: none;
    padding: 0.25rem;
    cursor: pointer;
    color: #94a3b8;
    transition: color 0.2s;
  }

  .toast-close:hover {
    color: #475569;
  }

  .toast-action {
    flex-shrink: 0;
    background: none;
    border: none;
    padding: 0.25rem 0.75rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: #5dade2;
    cursor: pointer;
    transition: color 0.2s;
  }

  .toast-action:hover {
    color: #3498db;
  }

  /* Toast variants */
  .toast-success {
    border-left: 4px solid #22c55e;
  }

  .toast-success .toast-icon {
    color: #22c55e;
  }

  .toast-error {
    border-left: 4px solid #ef4444;
  }

  .toast-error .toast-icon {
    color: #ef4444;
  }

  .toast-info {
    border-left: 4px solid #5dade2;
  }

  .toast-info .toast-icon {
    color: #5dade2;
  }

  .toast-warning {
    border-left: 4px solid #f59e0b;
  }

  .toast-warning .toast-icon {
    color: #f59e0b;
  }

  /* Toast stack */
  .toast-stack {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    align-items: center;
  }

  /* Alert styles */
  .alert {
    display: flex;
    gap: 1rem;
    padding: 1.25rem;
    border-radius: 8px;
    width: 100%;
  }

  .alert-icon {
    flex-shrink: 0;
  }

  .alert-content {
    flex: 1;
  }

  .alert-title {
    margin: 0 0 0.25rem 0;
    font-size: 1rem;
    font-weight: 600;
  }

  .alert-message {
    margin: 0;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  /* Alert variants */
  .alert-success {
    background: #dcfce7;
    color: #14532d;
  }

  .alert-success .alert-icon {
    color: #22c55e;
  }

  .alert-error {
    background: #fee2e2;
    color: #7f1d1d;
  }

  .alert-error .alert-icon {
    color: #ef4444;
  }

  .alert-info {
    background: #dbeafe;
    color: #1e3a8a;
  }

  .alert-info .alert-icon {
    color: #3b82f6;
  }

  .alert-warning {
    background: #fef3c7;
    color: #78350f;
  }

  .alert-warning .alert-icon {
    color: #f59e0b;
  }

  /* Demo panel */
  .demo-panel {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .demo-panel h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 1.5rem;
    text-align: center;
  }

  .button-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .dev-nav {
    padding: 2rem 0;
    border-top: 1px solid #e2e8f0;
  }

  /* Override hero gradient text */
  :global(.component-gallery .hero h1) {
    background: none !important;
    -webkit-text-fill-color: white !important;
    color: white !important;
  }
</style>
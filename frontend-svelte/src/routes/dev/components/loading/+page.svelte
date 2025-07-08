<script>
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import ProgressIndicator from '$lib/components/ProgressIndicator.svelte';
  
  // Demo states
  let progressValue = 65;
  let indeterminateProgress = true;
</script>

<Navbar />

<main class="component-gallery">
  <Hero 
    title="Loading States Gallery"
    subtitle="Loading indicators, spinners, and progress components"
  />
  
  <section class="gallery-content">
    <div class="container">
      <!-- Spinners -->
      <div class="component-section">
        <h2>Spinners</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Basic Spinner</h3>
            <div class="demo-area">
              <div class="spinner"></div>
            </div>
            <div class="code-snippet">
              <code>{`<div class="spinner"></div>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Spinner Sizes</h3>
            <div class="demo-area">
              <div class="spinner-group">
                <div class="spinner spinner-sm"></div>
                <div class="spinner"></div>
                <div class="spinner spinner-lg"></div>
              </div>
            </div>
            <div class="code-snippet">
              <code>{`<div class="spinner spinner-sm"></div>
<div class="spinner"></div>
<div class="spinner spinner-lg"></div>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Spinner Colors</h3>
            <div class="demo-area">
              <div class="spinner-group">
                <div class="spinner"></div>
                <div class="spinner spinner-primary"></div>
                <div class="spinner spinner-success"></div>
                <div class="spinner spinner-warning"></div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Spinner with Text</h3>
            <div class="demo-area">
              <div class="loading-wrapper">
                <div class="spinner"></div>
                <span class="loading-text">Loading...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Progress Bars -->
      <div class="component-section">
        <h2>Progress Bars</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Basic Progress Bar</h3>
            <div class="demo-area">
              <div class="progress">
                <div class="progress-bar" style="width: 65%"></div>
              </div>
            </div>
            <div class="code-snippet">
              <code>{`<div class="progress">
  <div class="progress-bar" style="width: 65%"></div>
</div>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Progress with Label</h3>
            <div class="demo-area">
              <div class="progress">
                <div class="progress-bar" style="width: 65%">
                  <span class="progress-label">65%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Striped Progress</h3>
            <div class="demo-area">
              <div class="progress">
                <div class="progress-bar progress-bar-striped" style="width: 65%"></div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Animated Progress</h3>
            <div class="demo-area">
              <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 65%"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Progress Indicators Component -->
      <div class="component-section">
        <h2>Progress Indicator Component</h2>
        <div class="component-grid large">
          <div class="component-demo">
            <h3>Default Size</h3>
            <div class="demo-area">
              <ProgressIndicator 
                progress={progressValue} 
                message="Processing your images..."
              />
            </div>
          </div>

          <div class="component-demo">
            <h3>Large Size</h3>
            <div class="demo-area">
              <ProgressIndicator 
                progress={progressValue} 
                message="Processing your images..."
                size="large"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Skeleton Loaders -->
      <div class="component-section">
        <h2>Skeleton Loaders</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Text Skeleton</h3>
            <div class="demo-area">
              <div class="skeleton skeleton-text"></div>
              <div class="skeleton skeleton-text" style="width: 80%"></div>
              <div class="skeleton skeleton-text" style="width: 60%"></div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Card Skeleton</h3>
            <div class="demo-area">
              <div class="skeleton-card">
                <div class="skeleton skeleton-image"></div>
                <div class="skeleton-content">
                  <div class="skeleton skeleton-title"></div>
                  <div class="skeleton skeleton-text"></div>
                  <div class="skeleton skeleton-text" style="width: 80%"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>List Skeleton</h3>
            <div class="demo-area">
              <div class="skeleton-list">
                <div class="skeleton-list-item">
                  <div class="skeleton skeleton-avatar"></div>
                  <div class="skeleton-list-content">
                    <div class="skeleton skeleton-text" style="width: 60%"></div>
                    <div class="skeleton skeleton-text" style="width: 40%"></div>
                  </div>
                </div>
                <div class="skeleton-list-item">
                  <div class="skeleton skeleton-avatar"></div>
                  <div class="skeleton-list-content">
                    <div class="skeleton skeleton-text" style="width: 70%"></div>
                    <div class="skeleton skeleton-text" style="width: 50%"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading States -->
      <div class="component-section">
        <h2>Loading States</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Button Loading</h3>
            <div class="demo-area">
              <Button variant="primary" disabled>
                <span class="spinner spinner-sm"></span>
                Processing...
              </Button>
            </div>
          </div>

          <div class="component-demo">
            <h3>Overlay Loading</h3>
            <div class="demo-area" style="position: relative; height: 200px;">
              <div class="loading-overlay">
                <div class="spinner spinner-lg"></div>
                <p class="loading-message">Loading content...</p>
              </div>
              <div style="padding: 1rem;">
                <p>This content is behind the loading overlay</p>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Inline Loading</h3>
            <div class="demo-area">
              <div class="inline-loading">
                <Icon name="loader" size={16} class="spinning" />
                <span>Refreshing data...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pulse Animations -->
      <div class="component-section">
        <h2>Pulse & Dots Loaders</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Pulse Loader</h3>
            <div class="demo-area">
              <div class="pulse-loader">
                <div class="pulse"></div>
                <div class="pulse"></div>
                <div class="pulse"></div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Dots Loader</h3>
            <div class="demo-area">
              <div class="dots-loader">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Bouncing Dots</h3>
            <div class="demo-area">
              <div class="bouncing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- File Processing States -->
      <div class="component-section">
        <h2>File Processing States</h2>
        <div class="component-grid large">
          <div class="component-demo">
            <h3>File Upload Progress</h3>
            <div class="demo-area">
              <div class="file-progress-card">
                <div class="file-icon">
                  <Icon name="document" size={24} />
                </div>
                <div class="file-details">
                  <h4>image-file.jpg</h4>
                  <div class="progress progress-sm">
                    <div class="progress-bar" style="width: 45%"></div>
                  </div>
                  <span class="file-status">Uploading... 45%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Processing Animation</h3>
            <div class="demo-area">
              <div class="processing-animation">
                <div class="processing-icon">
                  <Icon name="cube" size={48} />
                  <div class="processing-ring"></div>
                </div>
                <h4>Generating 3D Model</h4>
                <p>This may take a few moments...</p>
              </div>
            </div>
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
    grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
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
    min-height: 120px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .code-snippet {
    background: #1e293b;
    border-radius: 6px;
    padding: 1rem;
    overflow-x: auto;
  }

  .code-snippet code {
    color: #e2e8f0;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.875rem;
    white-space: pre;
  }

  /* Spinner styles */
  .spinner {
    width: 2rem;
    height: 2rem;
    border: 3px solid #e2e8f0;
    border-top-color: #5dade2;
    border-radius: 50%;
    animation: spinner 0.8s linear infinite;
  }

  .spinner-sm {
    width: 1rem;
    height: 1rem;
    border-width: 2px;
  }

  .spinner-lg {
    width: 3rem;
    height: 3rem;
    border-width: 4px;
  }

  .spinner-primary {
    border-top-color: #5dade2;
  }

  .spinner-success {
    border-top-color: #22c55e;
  }

  .spinner-warning {
    border-top-color: #f59e0b;
  }

  @keyframes spinner {
    to { transform: rotate(360deg); }
  }

  .spinner-group {
    display: flex;
    align-items: center;
    gap: 2rem;
  }

  .loading-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .loading-text {
    color: #64748b;
    font-size: 0.875rem;
  }

  /* Progress bars */
  .progress {
    width: 100%;
    height: 1rem;
    background: #e2e8f0;
    border-radius: 0.5rem;
    overflow: hidden;
    position: relative;
  }

  .progress-sm {
    height: 0.5rem;
  }

  .progress-bar {
    height: 100%;
    background: #5dade2;
    transition: width 0.3s ease;
    position: relative;
  }

  .progress-label {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.75rem;
    color: white;
    font-weight: 500;
  }

  .progress-bar-striped {
    background-image: linear-gradient(
      45deg,
      rgba(255,255,255,.15) 25%,
      transparent 25%,
      transparent 50%,
      rgba(255,255,255,.15) 50%,
      rgba(255,255,255,.15) 75%,
      transparent 75%,
      transparent
    );
    background-size: 1rem 1rem;
  }

  .progress-bar-animated {
    animation: progress-bar-stripes 1s linear infinite;
  }

  @keyframes progress-bar-stripes {
    from { background-position: 1rem 0; }
    to { background-position: 0 0; }
  }

  /* Skeleton loaders */
  .skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
  }

  @keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  .skeleton-text {
    height: 1rem;
    border-radius: 0.25rem;
    margin-bottom: 0.5rem;
  }

  .skeleton-title {
    height: 1.5rem;
    width: 60%;
    border-radius: 0.25rem;
    margin-bottom: 1rem;
  }

  .skeleton-image {
    width: 100%;
    height: 150px;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
  }

  .skeleton-avatar {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
  }

  .skeleton-card {
    background: white;
    border-radius: 0.5rem;
    padding: 1rem;
  }

  .skeleton-list-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 0;
    border-bottom: 1px solid #f0f0f0;
  }

  .skeleton-list-content {
    flex: 1;
  }

  /* Loading overlay */
  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    border-radius: 8px;
    z-index: 10;
  }

  .loading-message {
    margin: 0;
    color: #64748b;
    font-size: 0.875rem;
  }

  /* Inline loading */
  .inline-loading {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    color: #64748b;
  }

  :global(.inline-loading .icon.spinning) {
    animation: spinner 1s linear infinite;
  }

  /* Pulse loader */
  .pulse-loader {
    display: flex;
    gap: 0.5rem;
  }

  .pulse {
    width: 12px;
    height: 12px;
    background: #5dade2;
    border-radius: 50%;
    animation: pulse 1.4s ease-in-out infinite both;
  }

  .pulse:nth-child(1) { animation-delay: -0.32s; }
  .pulse:nth-child(2) { animation-delay: -0.16s; }

  @keyframes pulse {
    0%, 80%, 100% {
      transform: scale(0);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }

  /* Dots loader */
  .dots-loader {
    display: flex;
    gap: 0.25rem;
  }

  .dots-loader span {
    width: 8px;
    height: 8px;
    background: #5dade2;
    border-radius: 50%;
    opacity: 0;
    animation: dots 1.4s infinite ease-in-out;
  }

  .dots-loader span:nth-child(1) { animation-delay: 0s; }
  .dots-loader span:nth-child(2) { animation-delay: 0.2s; }
  .dots-loader span:nth-child(3) { animation-delay: 0.4s; }

  @keyframes dots {
    0%, 60%, 100% { opacity: 0; }
    30% { opacity: 1; }
  }

  /* Bouncing dots */
  .bouncing-dots {
    display: flex;
    gap: 0.5rem;
  }

  .bouncing-dots span {
    width: 12px;
    height: 12px;
    background: #5dade2;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
  }

  .bouncing-dots span:nth-child(1) { animation-delay: -0.32s; }
  .bouncing-dots span:nth-child(2) { animation-delay: -0.16s; }

  @keyframes bounce {
    0%, 80%, 100% {
      transform: scale(0);
    }
    40% {
      transform: scale(1);
    }
  }

  /* File progress card */
  .file-progress-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .file-icon {
    color: #64748b;
  }

  .file-details {
    flex: 1;
  }

  .file-details h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    font-weight: 500;
    color: #1e293b;
  }

  .file-status {
    font-size: 0.75rem;
    color: #64748b;
  }

  /* Processing animation */
  .processing-animation {
    text-align: center;
  }

  .processing-icon {
    position: relative;
    display: inline-block;
    margin-bottom: 1rem;
    color: #5dade2;
  }

  .processing-ring {
    position: absolute;
    top: -8px;
    left: -8px;
    right: -8px;
    bottom: -8px;
    border: 3px solid #e2e8f0;
    border-top-color: #5dade2;
    border-radius: 50%;
    animation: spinner 1s linear infinite;
  }

  .processing-animation h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
  }

  .processing-animation p {
    margin: 0;
    color: #64748b;
    font-size: 0.875rem;
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
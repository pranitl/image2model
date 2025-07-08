<script>
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
</script>

<Navbar />

<main class="component-gallery">
  <Hero 
    title="Error States Showcase"
    subtitle="UI patterns for handling errors and failures"
  />
  
  <section class="gallery-content">
    <div class="container">
      <!-- Form Validation Errors -->
      <div class="component-section">
        <h2>Form Validation Errors</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Field Error</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="email-error">Email Address</label>
                <input 
                  id="email-error"
                  type="email" 
                  class="form-control is-invalid" 
                  value="invalid-email"
                />
                <div class="error-message">
                  <Icon name="x-circle" size={16} />
                  Please enter a valid email address
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Multiple Field Errors</h3>
            <div class="demo-area">
              <form class="error-form">
                <div class="form-group">
                  <label for="name-error">Name</label>
                  <input 
                    id="name-error"
                    type="text" 
                    class="form-control is-invalid" 
                    value=""
                  />
                  <div class="error-message">
                    <Icon name="x-circle" size={16} />
                    Name is required
                  </div>
                </div>
                <div class="form-group">
                  <label for="file-error">File</label>
                  <input 
                    id="file-error"
                    type="text" 
                    class="form-control is-invalid" 
                    value="document.exe"
                  />
                  <div class="error-message">
                    <Icon name="x-circle" size={16} />
                    File type not supported
                  </div>
                </div>
              </form>
            </div>
          </div>

          <div class="component-demo">
            <h3>Form Summary Error</h3>
            <div class="demo-area">
              <div class="error-summary">
                <div class="error-summary-header">
                  <Icon name="alert-triangle" size={20} />
                  <h4>Please fix the following errors:</h4>
                </div>
                <ul class="error-list">
                  <li>Email address is invalid</li>
                  <li>Password must be at least 8 characters</li>
                  <li>Terms of service must be accepted</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Upload Errors -->
      <div class="component-section">
        <h2>Upload & File Errors</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>File Too Large</h3>
            <div class="demo-area">
              <div class="file-error-card">
                <div class="file-error-icon">
                  <Icon name="document" size={32} />
                  <div class="error-badge">
                    <Icon name="x" size={12} />
                  </div>
                </div>
                <div class="file-error-content">
                  <h4>large-file.jpg</h4>
                  <p class="error-text">File size exceeds 10MB limit</p>
                  <Button variant="ghost" size="sm">Remove</Button>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Invalid File Type</h3>
            <div class="demo-area">
              <div class="file-error-card">
                <div class="file-error-icon">
                  <Icon name="document" size={32} />
                  <div class="error-badge">
                    <Icon name="x" size={12} />
                  </div>
                </div>
                <div class="file-error-content">
                  <h4>document.pdf</h4>
                  <p class="error-text">Only JPG, PNG files are allowed</p>
                  <Button variant="ghost" size="sm">Remove</Button>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Upload Failed</h3>
            <div class="demo-area">
              <div class="upload-error">
                <Icon name="cloud-off" size={48} color="#ef4444" />
                <h4>Upload Failed</h4>
                <p>Unable to upload files. Please check your connection and try again.</p>
                <Button variant="primary" size="sm">Retry Upload</Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Processing Errors -->
      <div class="component-section">
        <h2>Processing & Server Errors</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Processing Failed</h3>
            <div class="demo-area">
              <div class="processing-error">
                <div class="error-icon-wrapper">
                  <Icon name="x-circle" size={64} color="#ef4444" />
                </div>
                <h3>Processing Failed</h3>
                <p>An error occurred while generating your 3D models.</p>
                <div class="error-details">
                  <code>Error: Image resolution too low for 3D reconstruction</code>
                </div>
                <div class="button-group">
                  <Button variant="ghost">View Details</Button>
                  <Button variant="primary">Try Again</Button>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Server Error</h3>
            <div class="demo-area">
              <div class="server-error">
                <div class="error-code">500</div>
                <h3>Server Error</h3>
                <p>Something went wrong on our end. Please try again later.</p>
                <Button variant="primary">Refresh Page</Button>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Timeout Error</h3>
            <div class="demo-area">
              <div class="timeout-error">
                <Icon name="clock" size={48} color="#f59e0b" />
                <h3>Request Timeout</h3>
                <p>The operation took too long to complete.</p>
                <Button variant="primary" size="sm">Try Again</Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Network Errors -->
      <div class="component-section">
        <h2>Network & Connection Errors</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>No Internet Connection</h3>
            <div class="demo-area">
              <div class="network-error">
                <Icon name="wifi-off" size={64} color="#ef4444" />
                <h3>No Internet Connection</h3>
                <p>Please check your network settings and try again.</p>
                <Button variant="ghost">Retry</Button>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>API Error</h3>
            <div class="demo-area">
              <div class="api-error">
                <div class="api-error-header">
                  <Icon name="alert-triangle" size={24} />
                  <h4>API Error</h4>
                </div>
                <div class="api-error-details">
                  <div class="error-row">
                    <span class="error-label">Status:</span>
                    <span class="error-value">403 Forbidden</span>
                  </div>
                  <div class="error-row">
                    <span class="error-label">Message:</span>
                    <span class="error-value">Invalid API key</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Page-Level Errors -->
      <div class="component-section">
        <h2>Page-Level Errors</h2>
        <div class="component-grid large">
          <div class="component-demo">
            <h3>404 Not Found</h3>
            <div class="demo-area large">
              <div class="page-error">
                <div class="error-404">404</div>
                <h2>Page Not Found</h2>
                <p>The page you're looking for doesn't exist or has been moved.</p>
                <Button href="/" variant="primary">Go to Homepage</Button>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Access Denied</h3>
            <div class="demo-area large">
              <div class="page-error">
                <Icon name="lock" size={64} color="#ef4444" />
                <h2>Access Denied</h2>
                <p>You don't have permission to view this page.</p>
                <div class="button-group">
                  <Button variant="ghost">Go Back</Button>
                  <Button variant="primary">Sign In</Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Inline Error Messages -->
      <div class="component-section">
        <h2>Inline Error Messages</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Toast Error</h3>
            <div class="demo-area">
              <div class="toast toast-error">
                <div class="toast-icon">
                  <Icon name="x-circle" size={20} />
                </div>
                <div class="toast-content">
                  <p class="toast-message">Failed to save changes. Please try again.</p>
                </div>
                <button class="toast-close">
                  <Icon name="x" size={16} />
                </button>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Banner Error</h3>
            <div class="demo-area">
              <div class="error-banner">
                <Icon name="alert-triangle" size={20} />
                <span>System maintenance in progress. Some features may be unavailable.</span>
                <button class="banner-close">
                  <Icon name="x" size={16} />
                </button>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Inline Alert</h3>
            <div class="demo-area">
              <div class="alert alert-error">
                <div class="alert-icon">
                  <Icon name="x-circle" size={24} />
                </div>
                <div class="alert-content">
                  <h4 class="alert-title">Payment Failed</h4>
                  <p class="alert-message">Your card was declined. Please try a different payment method.</p>
                </div>
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
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
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
    min-height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .demo-area.large {
    min-height: 300px;
  }

  /* Form errors */
  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #475569;
    font-size: 0.875rem;
  }

  .form-control {
    display: block;
    width: 100%;
    padding: 0.625rem 1rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #1e293b;
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
  }

  .form-control.is-invalid {
    border-color: #ef4444;
  }

  .error-message {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    margin-top: 0.25rem;
    font-size: 0.875rem;
    color: #ef4444;
  }

  /* Error summary */
  .error-summary {
    background: #fee2e2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 1rem;
  }

  .error-summary-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
    color: #dc2626;
  }

  .error-summary-header h4 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
  }

  .error-list {
    margin: 0;
    padding-left: 1.5rem;
    color: #7f1d1d;
    font-size: 0.875rem;
  }

  .error-list li {
    margin-bottom: 0.25rem;
  }

  /* File errors */
  .file-error-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: white;
    border: 1px solid #fecaca;
    border-radius: 8px;
  }

  .file-error-icon {
    position: relative;
    color: #94a3b8;
  }

  .error-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    width: 20px;
    height: 20px;
    background: #ef4444;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .file-error-content h4 {
    margin: 0 0 0.25rem 0;
    font-size: 0.875rem;
    font-weight: 500;
    color: #1e293b;
  }

  .error-text {
    margin: 0 0 0.5rem 0;
    font-size: 0.875rem;
    color: #ef4444;
  }

  /* Upload error */
  .upload-error {
    text-align: center;
    padding: 2rem;
  }

  .upload-error h4 {
    margin: 1rem 0 0.5rem;
    font-size: 1.125rem;
    font-weight: 600;
    color: #dc2626;
  }

  .upload-error p {
    margin: 0 0 1rem;
    color: #64748b;
    font-size: 0.875rem;
  }

  /* Processing error */
  .processing-error {
    text-align: center;
    padding: 2rem;
    max-width: 400px;
  }

  .error-icon-wrapper {
    margin-bottom: 1rem;
  }

  .processing-error h3 {
    margin: 0 0 0.5rem;
    font-size: 1.25rem;
    font-weight: 600;
    color: #dc2626;
  }

  .processing-error p {
    margin: 0 0 1rem;
    color: #64748b;
  }

  .error-details {
    background: #1e293b;
    color: #e2e8f0;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.875rem;
    margin-bottom: 1.5rem;
  }

  /* Server error */
  .server-error {
    text-align: center;
    padding: 2rem;
  }

  .error-code {
    font-size: 4rem;
    font-weight: 700;
    color: #ef4444;
    line-height: 1;
    margin-bottom: 1rem;
  }

  .server-error h3 {
    margin: 0 0 0.5rem;
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
  }

  .server-error p {
    margin: 0 0 1.5rem;
    color: #64748b;
  }

  /* Network error */
  .network-error,
  .timeout-error {
    text-align: center;
    padding: 2rem;
  }

  .network-error h3,
  .timeout-error h3 {
    margin: 1rem 0 0.5rem;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
  }

  .network-error p,
  .timeout-error p {
    margin: 0 0 1.5rem;
    color: #64748b;
  }

  /* API error */
  .api-error {
    background: white;
    border: 1px solid #fecaca;
    border-radius: 8px;
    overflow: hidden;
  }

  .api-error-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: #fee2e2;
    color: #dc2626;
    border-bottom: 1px solid #fecaca;
  }

  .api-error-header h4 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
  }

  .api-error-details {
    padding: 1rem;
  }

  .error-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }

  .error-label {
    font-weight: 500;
    color: #64748b;
    min-width: 80px;
  }

  .error-value {
    color: #1e293b;
    font-family: 'Consolas', 'Monaco', monospace;
  }

  /* Page errors */
  .page-error {
    text-align: center;
    padding: 3rem;
  }

  .error-404 {
    font-size: 6rem;
    font-weight: 700;
    color: #e2e8f0;
    line-height: 1;
    margin-bottom: 1rem;
  }

  .page-error h2 {
    margin: 1rem 0;
    font-size: 2rem;
    font-weight: 600;
    color: #1e293b;
  }

  .page-error p {
    margin: 0 0 2rem;
    color: #64748b;
    font-size: 1.125rem;
  }

  /* Toast error */
  .toast {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    max-width: 400px;
  }

  .toast-error {
    border-left: 4px solid #ef4444;
  }

  .toast-icon {
    flex-shrink: 0;
    color: #ef4444;
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
  }

  /* Error banner */
  .error-banner {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: #fef3c7;
    color: #78350f;
    border-radius: 8px;
    font-size: 0.875rem;
  }

  .banner-close {
    margin-left: auto;
    background: none;
    border: none;
    padding: 0.25rem;
    cursor: pointer;
    color: #92400e;
  }

  /* Alert error */
  .alert {
    display: flex;
    gap: 1rem;
    padding: 1.25rem;
    border-radius: 8px;
  }

  .alert-error {
    background: #fee2e2;
    color: #7f1d1d;
  }

  .alert-icon {
    flex-shrink: 0;
    color: #ef4444;
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

  .button-group {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
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
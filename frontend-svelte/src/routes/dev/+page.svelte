<script>
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
</script>

<Navbar />

<main class="dev-page">
  <Hero 
    title="Development Dashboard"
    subtitle="View all pages and states for testing and development"
  />

  <section class="dev-sections">
    <div class="container">
      <!-- Page States Section -->
      <div class="dev-section">
        <h2><Icon name="document" size={24} /> Page States</h2>
        <div class="dev-grid">
          <div class="dev-card">
            <h3>Homepage</h3>
            <p>Landing page with all sections</p>
            <Button href="/" variant="primary">View Page</Button>
          </div>

          <div class="dev-card">
            <h3>Upload - Empty</h3>
            <p>Initial upload state</p>
            <Button href="/upload" variant="primary">View Page</Button>
          </div>

          <div class="dev-card">
            <h3>Upload - With Files</h3>
            <p>Upload page with files selected</p>
            <Button href="/dev/upload-with-files" variant="primary">View Page</Button>
          </div>

          <div class="dev-card">
            <h3>Processing - Active</h3>
            <p>Processing in progress (50% complete)</p>
            <Button href="/dev/processing-active" variant="primary">View Page</Button>
          </div>

          <div class="dev-card">
            <h3>Processing - Complete</h3>
            <p>Processing finished, showing results</p>
            <Button href="/dev/results" variant="primary">View Page</Button>
          </div>

          <div class="dev-card">
            <h3>Error Page</h3>
            <p>404 and error states</p>
            <Button href="/dev/nonexistent" variant="primary">View 404</Button>
          </div>
        </div>
      </div>

      <!-- Component Gallery Section -->
      <div class="dev-section">
        <h2><Icon name="cube" size={24} /> Component States</h2>
        <div class="dev-grid">
          <div class="dev-card">
            <h3>Buttons</h3>
            <p>All button variants and states</p>
            <Button href="/dev/components/buttons" variant="secondary">View Gallery</Button>
          </div>

          <div class="dev-card">
            <h3>Cards</h3>
            <p>Model cards, feature cards, etc.</p>
            <Button href="/dev/components/cards" variant="secondary">View Gallery</Button>
          </div>

          <div class="dev-card">
            <h3>Forms</h3>
            <p>Input fields, dropdowns, etc.</p>
            <Button href="/dev/components/forms" variant="secondary">View Gallery</Button>
          </div>

          <div class="dev-card">
            <h3>Toasts</h3>
            <p>Success, error, info messages</p>
            <Button href="/dev/components/toasts" variant="secondary">View Demo</Button>
          </div>

          <div class="dev-card">
            <h3>Loading States</h3>
            <p>Spinners, progress bars, etc.</p>
            <Button href="/dev/components/loading" variant="secondary">View Demo</Button>
          </div>

          <div class="dev-card">
            <h3>Icons</h3>
            <p>All available icons</p>
            <Button href="/dev/components/icons" variant="secondary">View Gallery</Button>
          </div>
        </div>
      </div>

      <!-- Test Scenarios Section -->
      <div class="dev-section">
        <h2><Icon name="warning" size={24} /> Test Scenarios</h2>
        <div class="dev-grid">
          <div class="dev-card">
            <h3>Empty States</h3>
            <p>No files, no results, etc.</p>
            <Button href="/dev/empty-states" variant="ghost">View Empty Upload</Button>
          </div>

          <div class="dev-card">
            <h3>Error States</h3>
            <p>Processing failed</p>
            <Button href="/dev/error-states" variant="ghost">View Error</Button>
          </div>

          <div class="dev-card">
            <h3>Edge Case: Many Files</h3>
            <p>50+ generated models</p>
            <Button href="/dev/edge-cases?case=manyFiles" variant="ghost">View 50 Files</Button>
          </div>
          
          <div class="dev-card">
            <h3>Edge Case: Large Files</h3>
            <p>Very large model files</p>
            <Button href="/dev/edge-cases?case=largeFiles" variant="ghost">View Large Files</Button>
          </div>
          
          <div class="dev-card">
            <h3>Edge Case: Slow Processing</h3>
            <p>Processing taking long time</p>
            <Button href="/dev/edge-cases?case=slowProcessing" variant="ghost">View Slow</Button>
          </div>
          
          <div class="dev-card">
            <h3>Edge Case: Mixed Results</h3>
            <p>Some files failed</p>
            <Button href="/dev/edge-cases?case=mixedResults" variant="ghost">View Mixed</Button>
          </div>
        </div>
      </div>
    </div>
  </section>
</main>

<Footer />

<style>
  .dev-page {
    min-height: 100vh;
    background-color: #f8f9fa;
  }

  .dev-sections {
    padding: 4rem 0;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }

  .dev-section {
    margin-bottom: 4rem;
  }

  .dev-section h2 {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .dev-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .dev-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
  }

  .dev-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .dev-card h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 0.5rem;
  }

  .dev-card p {
    color: #64748b;
    margin-bottom: 1rem;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  /* Icon styling */
  .dev-section h2 :global(.icon) {
    color: #5dade2;
  }

  /* Override hero gradient text */
  :global(.dev-page .hero h1) {
    background: none !important;
    -webkit-text-fill-color: white !important;
    color: white !important;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .dev-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
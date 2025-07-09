<script>
  import { onMount } from 'svelte';
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
  
  let showCode = {};
  
  function toggleCode(id) {
    showCode[id] = !showCode[id];
  }
</script>

<Navbar />

<main class="component-gallery">
  <Hero 
    title="Button Component Gallery"
    subtitle="All button variants, sizes, and states"
  />
  
  <section class="gallery-content">
    <div class="container">
      <!-- Button Variants -->
      <div class="component-section">
        <h2>Button Variants</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Primary Button</h3>
            <div class="demo-area">
              <Button variant="primary">Primary Button</Button>
              <Button variant="primary" disabled>Disabled Primary</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary">Primary Button</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Secondary Button</h3>
            <div class="demo-area">
              <Button variant="secondary">Secondary Button</Button>
              <Button variant="secondary" disabled>Disabled Secondary</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="secondary">Secondary Button</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Ghost Button</h3>
            <div class="demo-area dark-bg">
              <Button variant="ghost">Ghost Button</Button>
              <Button variant="ghost" disabled>Disabled Ghost</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="ghost">Ghost Button</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Ghost Light Button</h3>
            <div class="demo-area gradient-bg">
              <Button variant="ghost-light">Ghost Light</Button>
              <Button variant="ghost-light" disabled>Disabled</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="ghost-light">Ghost Light</Button>`}</code>
            </div>
          </div>
        </div>
      </div>

      <!-- Button Sizes -->
      <div class="component-section">
        <h2>Button Sizes</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Small Size</h3>
            <div class="demo-area">
              <Button variant="primary" size="sm">Small Primary</Button>
              <Button variant="secondary" size="sm">Small Secondary</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary" size="sm">Small</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Medium Size (Default)</h3>
            <div class="demo-area">
              <Button variant="primary" size="md">Medium Primary</Button>
              <Button variant="secondary" size="md">Medium Secondary</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary" size="md">Medium</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Large Size</h3>
            <div class="demo-area">
              <Button variant="primary" size="lg">Large Primary</Button>
              <Button variant="secondary" size="lg">Large Secondary</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary" size="lg">Large</Button>`}</code>
            </div>
          </div>
        </div>
      </div>

      <!-- Buttons with Icons -->
      <div class="component-section">
        <h2>Buttons with Icons</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Icon Left</h3>
            <div class="demo-area">
              <Button variant="primary">
                <Icon name="upload" size={16} />
                Upload Files
              </Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary">
  <Icon name="upload" size={16} />
  Upload Files
</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Icon Right</h3>
            <div class="demo-area">
              <Button variant="secondary">
                Download All
                <Icon name="download" size={16} />
              </Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="secondary">
  Download All
  <Icon name="download" size={16} />
</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Icon Only</h3>
            <div class="demo-area">
              <Button variant="primary" size="sm" title="Settings">
                <Icon name="cog" size={16} />
              </Button>
              <Button variant="secondary" size="sm" title="Close">
                <Icon name="x" size={16} />
              </Button>
              <Button variant="ghost" size="sm" title="Menu">
                <Icon name="chevron-down" size={16} />
              </Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary" size="sm" title="Settings">
  <Icon name="cog" size={16} />
</Button>`}</code>
            </div>
          </div>
        </div>
      </div>

      <!-- Button States & Animations -->
      <div class="component-section">
        <h2>Button States & Animations</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Hover Effects</h3>
            <div class="demo-area">
              <Button variant="primary" class="hover-lift">Hover Lift</Button>
              <Button variant="secondary" class="hover-scale">Hover Scale</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary" class="hover-lift">Hover Lift</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Loading State</h3>
            <div class="demo-area">
              <Button variant="primary" disabled>
                <span class="spinner"></span>
                Processing...
              </Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary" disabled>
  <span class="spinner"></span>
  Processing...
</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Full Width</h3>
            <div class="demo-area">
              <Button variant="primary" class="full-width">Full Width Button</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary" class="full-width">Full Width</Button>`}</code>
            </div>
          </div>
        </div>
      </div>

      <!-- Special Buttons -->
      <div class="component-section">
        <h2>Special Buttons</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Button as Link</h3>
            <div class="demo-area">
              <Button href="/upload" variant="primary">Go to Upload</Button>
              <Button href="/" variant="secondary">Back to Home</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button href="/upload" variant="primary">Go to Upload</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Button with Badge</h3>
            <div class="demo-area">
              <Button variant="primary">
                Download All
                <span class="badge">15.2MB</span>
              </Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary">
  Download All
  <span class="badge">15.2MB</span>
</Button>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Gradient Buttons</h3>
            <div class="demo-area">
              <Button variant="primary" class="gradient-animated">Animated Gradient</Button>
              <Button variant="primary" class="gradient-cool-ocean">Ocean Gradient</Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary" class="gradient-animated">Animated</Button>`}</code>
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
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
    min-height: 80px;
  }

  .demo-area.dark-bg {
    background: #1e293b;
  }

  .demo-area.gradient-bg {
    background: linear-gradient(135deg, #5dade2 0%, #3498db 100%);
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

  /* Button-specific styles for demos */
  :global(.demo-area .spinner) {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  :global(.demo-area .badge) {
    display: inline-block;
    background: rgba(255, 255, 255, 0.2);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    margin-left: 0.5rem;
  }

  :global(.demo-area .full-width) {
    width: 100%;
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
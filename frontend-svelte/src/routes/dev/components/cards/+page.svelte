<script>
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import ModelCard from '$lib/components/ModelCard.svelte';
  
  // Mock data for ModelCard
  const mockModelFile = {
    filename: 'example-model.glb',
    name: 'example-model.glb',
    size: 2457600, // 2.4MB
    downloadUrl: '#',
    mimeType: 'model/gltf-binary',
    createdTime: new Date().toISOString(),
    rendered_image: { url: 'https://placehold.co/400x300/5DADE2/white?text=3D+Model' }
  };

  const mockModelFileNoPreview = {
    filename: 'no-preview-model.glb',
    name: 'no-preview-model.glb',
    size: 3145728, // 3MB
    downloadUrl: '#',
    mimeType: 'model/gltf-binary',
    createdTime: new Date().toISOString(),
    rendered_image: null
  };
</script>

<Navbar />

<main class="component-gallery">
  <Hero 
    title="Card Components Gallery"
    subtitle="Various card components used throughout the application"
  />
  
  <section class="gallery-content">
    <div class="container">
      <!-- Model Cards -->
      <div class="component-section">
        <h2>Model Cards</h2>
        <div class="component-grid large">
          <div class="component-demo">
            <h3>Model Card with Preview</h3>
            <div class="demo-area">
              <ModelCard file={mockModelFile} jobId="test-job-123" />
            </div>
            <div class="code-snippet">
              <code>{`<ModelCard file={fileObject} jobId="job-123" />`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Model Card without Preview</h3>
            <div class="demo-area">
              <ModelCard file={mockModelFileNoPreview} jobId="test-job-456" />
            </div>
            <div class="code-snippet">
              <code>{`<ModelCard file={fileWithoutPreview} jobId="job-456" />`}</code>
            </div>
          </div>
        </div>
      </div>

      <!-- Feature Cards -->
      <div class="component-section">
        <h2>Feature Cards</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Basic Feature Card</h3>
            <div class="demo-area">
              <div class="feature-card card card-hover">
                <div class="feature-icon gradient-blue-medium">
                  <Icon name="cube" size={32} color="white" />
                </div>
                <h3 class="feature-title">Feature Title</h3>
                <p class="feature-description">This is a feature card used on the landing page to highlight key features.</p>
              </div>
            </div>
            <div class="code-snippet">
              <code>{`<div class="feature-card card card-hover">
  <div class="feature-icon gradient-blue-medium">
    <Icon name="cube" size={32} color="white" />
  </div>
  <h3 class="feature-title">Feature Title</h3>
  <p class="feature-description">Description text</p>
</div>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Step Card</h3>
            <div class="demo-area">
              <div class="step card card-lift">
                <div class="step-icon gradient-blue-medium">
                  <Icon name="upload" size={48} color="white" />
                </div>
                <span class="step-number gradient-animated">1</span>
                <h3 class="step-title">Upload Images</h3>
                <p class="step-description">Step-by-step process card with number badge.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Info Cards -->
      <div class="component-section">
        <h2>Info & Status Cards</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Summary Card</h3>
            <div class="demo-area">
              <div class="summary-card card">
                <div class="summary-item">
                  <div class="summary-icon">
                    <Icon name="document" size={24} />
                  </div>
                  <div>
                    <span class="summary-label">Models Generated</span>
                    <span class="summary-value">6</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>File Status Card</h3>
            <div class="demo-area">
              <div class="file-card">
                <div class="file-card-header">
                  <h3 class="file-name">example.jpg</h3>
                  <span class="file-status" style="color: #5DADE2">processing</span>
                </div>
                <div class="file-progress">
                  <div class="file-progress-bar">
                    <div class="file-progress-fill" style="width: 65%; background-color: #5DADE2"></div>
                  </div>
                  <span class="file-progress-text">65%</span>
                </div>
                <p class="file-message">Generating texture maps...</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Card Variations -->
      <div class="component-section">
        <h2>Card Styles & Effects</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Basic Card</h3>
            <div class="demo-area">
              <div class="card">
                <h4>Basic Card</h4>
                <p>Simple card with padding and shadow.</p>
              </div>
            </div>
            <div class="code-snippet">
              <code>{`<div class="card">
  <h4>Basic Card</h4>
  <p>Content here</p>
</div>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Hover Card</h3>
            <div class="demo-area">
              <div class="card card-hover">
                <h4>Hover Effect Card</h4>
                <p>Lifts up on hover with enhanced shadow.</p>
              </div>
            </div>
            <div class="code-snippet">
              <code>{`<div class="card card-hover">
  <h4>Hover Effect Card</h4>
  <p>Content here</p>
</div>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Lift Card</h3>
            <div class="demo-area">
              <div class="card card-lift">
                <h4>Always Lifted Card</h4>
                <p>Has elevation by default.</p>
              </div>
            </div>
            <div class="code-snippet">
              <code>{`<div class="card card-lift">
  <h4>Always Lifted Card</h4>
  <p>Content here</p>
</div>`}</code>
            </div>
          </div>
        </div>
      </div>

      <!-- Special Cards -->
      <div class="component-section">
        <h2>Special Purpose Cards</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Empty State Card</h3>
            <div class="demo-area">
              <div class="empty-state">
                <Icon name="info" size={64} color="#94a3b8" />
                <h3>No Results Found</h3>
                <p>Try adjusting your search criteria.</p>
                <Button href="#" variant="primary">Try Again</Button>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Next Step Card</h3>
            <div class="demo-area">
              <div class="next-step-card card hover-lift">
                <div class="step-icon">
                  <Icon name="eye" size={32} />
                </div>
                <h3>View in 3D</h3>
                <p>Preview your models using our 3D viewer.</p>
                <Button href="#" variant="ghost" size="sm">Coming Soon</Button>
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
  @import '/css/processing-page.css';
  @import '/css/results-page.css';
  @import '/css/upload-page.css';

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
    grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
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

  /* Basic card styles for demos */
  .card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .card h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
  }

  .card p {
    margin: 0;
    color: #64748b;
    line-height: 1.5;
  }

  /* Step card specific */
  .step {
    text-align: center;
    padding: 2rem;
    position: relative;
  }

  .step-icon {
    width: 100px;
    height: 100px;
    margin: 0 auto 1rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

  .step-number {
    position: absolute;
    top: -10px;
    right: -10px;
    width: 30px;
    height: 30px;
    background: linear-gradient(135deg, #5dade2 0%, #3498db 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
    font-weight: bold;
    color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .step-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }

  .step-description {
    color: #64748b;
    line-height: 1.5;
  }

  /* Feature icon gradient */
  .feature-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto 1rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .gradient-blue-medium {
    background: linear-gradient(135deg, #5DADE2 0%, #3498DB 100%);
  }

  /* Next step card */
  .next-step-card {
    text-align: center;
    padding: 2rem;
  }

  .next-step-card .step-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #5dade2;
  }

  .next-step-card h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }

  .next-step-card p {
    color: #64748b;
    margin-bottom: 1rem;
    line-height: 1.5;
  }

  /* Empty state */
  .empty-state {
    text-align: center;
    padding: 3rem;
  }

  .empty-state h3 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 1rem 0 0.5rem;
  }

  .empty-state p {
    color: #94a3b8;
    margin-bottom: 1.5rem;
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
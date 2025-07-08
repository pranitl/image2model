<script>
  import { onMount } from 'svelte';
  import { scrollReveal, staggerReveal } from '$lib/actions/animations';
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Breadcrumb from '$lib/components/Breadcrumb.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import ModelCard from '$lib/components/ModelCard.svelte';
  import api from '$lib/services/api';

  // Mock completed state
  let isCompleted = true;
  let isProcessing = false;
  let elapsedTime = 125; // 2 minutes 5 seconds
  let completedFiles = [
    {
      filename: 'chair_model.glb',
      name: 'chair_model.glb',
      size: 2457600, // 2.4 MB
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://placehold.co/400x300/5DADE2/white?text=Chair+3D+Model' }
    },
    {
      filename: 'table_model.glb',
      name: 'table_model.glb',
      size: 3145728, // 3 MB
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://placehold.co/400x300/7E5DE2/white?text=Table+3D+Model' }
    },
    {
      filename: 'lamp_model.glb',
      name: 'lamp_model.glb',
      size: 1572864, // 1.5 MB
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://placehold.co/400x300/F39C12/white?text=Lamp+3D+Model' }
    },
    {
      filename: 'sofa_model.glb',
      name: 'sofa_model.glb',
      size: 4194304, // 4 MB
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://placehold.co/400x300/52D252/white?text=Sofa+3D+Model' }
    },
    {
      filename: 'desk_model.glb',
      name: 'desk_model.glb',
      size: 2097152, // 2 MB
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://placehold.co/400x300/E74C3C/white?text=Desk+3D+Model' }
    },
    {
      filename: 'bookshelf_model.glb',
      name: 'bookshelf_model.glb',
      size: 2621440, // 2.5 MB
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: null // Test without preview
    }
  ];
  let jobId = 'test-job-123';
  let totalSize = completedFiles.reduce((sum, f) => sum + f.size, 0);
  let isLoadingResults = false;

  // Breadcrumb configuration
  let breadcrumbItems = [
    { name: 'Home', href: '/' },
    { name: 'Upload', href: '/upload' },
    { name: 'Processing', href: '#' },
    { name: 'Results', href: '#', current: true }
  ];

  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
  }

  async function downloadAll() {
    console.log('Download all clicked - would download', api.formatFileSize(totalSize));
    // In real app, this would trigger download
  }
</script>

<Navbar />

<main class="processing-page">
  <Hero 
    title="Your 3D Models Are Ready!"
    subtitle="Successfully generated 3D models from your images"
  />

  <Breadcrumb items={breadcrumbItems} />

  <!-- Results View -->
  <!-- Summary Section -->
  <section class="summary-section">
    <div class="container">
      <div class="summary-card card" use:scrollReveal>
        <div class="summary-item">
          <div class="summary-icon">
            <Icon name="document" size={24} />
          </div>
          <div>
            <span class="summary-label">Models Generated</span>
            <span class="summary-value">{completedFiles.length}</span>
          </div>
        </div>
        <div class="summary-item">
          <div class="summary-icon">
            <Icon name="clock" size={24} />
          </div>
          <div>
            <span class="summary-label">Processing Time</span>
            <span class="summary-value">{formatTime(elapsedTime)}</span>
          </div>
        </div>
        <div class="summary-item">
          <div class="summary-icon">
            <Icon name="arrow-down" size={24} />
          </div>
          <div>
            <span class="summary-label">Total Size</span>
            <span class="summary-value">{api.formatFileSize(totalSize)}</span>
          </div>
        </div>
      </div>
    </div>
  </section>
  
  <!-- Download Actions -->
  <section class="download-actions">
    <div class="container">
      <Button 
        id="downloadAllBtn"
        variant="primary"
        size="lg"
        on:click={downloadAll}
        class="hover-lift"
        disabled={completedFiles.length === 0}
      >
        <Icon name="cloud-download" size={20} />
        <span>Download All Models</span>
        <span class="badge">{api.formatFileSize(totalSize)}</span>
      </Button>
    </div>
  </section>
  
  <!-- Models Grid -->
  <section class="models-grid-section">
    <div class="container">
      <h2>Your 3D Models</h2>
      {#if isLoadingResults}
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Loading your models...</p>
        </div>
      {:else if completedFiles.length === 0}
        <div class="empty-state">
          <Icon name="info" size={64} color="#94a3b8" />
          <h3>No models generated</h3>
          <p>The processing completed but no 3D models were generated.</p>
          <Button href="/upload" variant="primary">Try Again</Button>
        </div>
      {:else}
        <div class="model-grid" use:staggerReveal>
          {#each completedFiles as file}
            <div data-stagger>
              <ModelCard {file} {jobId} />
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </section>
  
  <!-- What's Next Section -->
  <section class="whats-next-section">
    <div class="container">
      <h2>What's Next?</h2>
      <div class="next-steps-grid" use:staggerReveal>
        <div class="next-step-card card hover-lift" data-stagger>
          <div class="step-icon">
            <Icon name="eye" size={32} />
          </div>
          <h3>View in 3D</h3>
          <p>Preview your models using our online 3D viewer or download for use in your favorite 3D software.</p>
          <Button href="#" variant="ghost" size="sm">Coming Soon</Button>
        </div>
        <div class="next-step-card card hover-lift" data-stagger>
          <div class="step-icon">
            <Icon name="document" size={32} />
          </div>
          <h3>Import Guide</h3>
          <p>Learn how to import your 3D models into popular software like Blender, Unity, or Unreal Engine.</p>
          <Button href="#" variant="ghost" size="sm">View Guide</Button>
        </div>
        <div class="next-step-card card hover-lift" data-stagger>
          <div class="step-icon">
            <Icon name="external-link" size={32} />
          </div>
          <h3>Process More</h3>
          <p>Ready to create more 3D models? Upload new images and continue your creative journey.</p>
          <Button href="/upload" variant="ghost" size="sm">Upload More Images</Button>
        </div>
      </div>
    </div>
  </section>

  <!-- Dev Note -->
  <section class="dev-note">
    <div class="container">
      <div class="note-card">
        <Icon name="info" size={20} />
        <p>This is a development preview of the results view. In production, this appears after processing completes.</p>
        <Button href="/dev" variant="ghost" size="sm">Back to Dev Index</Button>
      </div>
    </div>
  </section>
</main>

<Footer />

<style>
  /* Import the processing page styles */
  @import '../../../css/processing-page.css';
  
  /* Override body background for consistency */
  :global(body) {
    background-color: #f8f9fa !important;
  }

  /* Override processing-page.css gradient text */
  :global(.hero h1) {
    background: none !important;
    -webkit-text-fill-color: white !important;
    color: white !important;
  }

  /* Dev note styles */
  .dev-note {
    padding: 2rem 0;
    background-color: #f8f9fa;
  }

  .note-card {
    background: #fef3c7;
    border: 1px solid #fbbf24;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    color: #92400e;
  }

  .note-card p {
    margin: 0;
    flex: 1;
  }

  .note-card :global(.icon) {
    color: #f59e0b;
  }
</style>
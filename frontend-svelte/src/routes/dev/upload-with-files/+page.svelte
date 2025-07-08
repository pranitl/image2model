<script>
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { scrollReveal, staggerReveal } from '$lib/actions/animations.js';
  import { toast } from '$lib/stores/toast.js';
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Breadcrumb from '$lib/components/Breadcrumb.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import ProgressIndicator from '$lib/components/ProgressIndicator.svelte';
  
  // Mock state with files already selected
  let files = [
    {
      id: 'file-1',
      file: new File([''], 'living-room.jpg', { type: 'image/jpeg' }),
      name: 'living-room.jpg',
      size: 2457600, // 2.4MB
      type: 'image/jpeg',
      preview: 'https://placehold.co/200x150/5DADE2/white?text=Living+Room'
    },
    {
      id: 'file-2',
      file: new File([''], 'kitchen-modern.png', { type: 'image/png' }),
      name: 'kitchen-modern.png',
      size: 3145728, // 3MB
      type: 'image/png',
      preview: 'https://placehold.co/200x150/7E5DE2/white?text=Kitchen'
    },
    {
      id: 'file-3',
      file: new File([''], 'bedroom-master.jpg', { type: 'image/jpeg' }),
      name: 'bedroom-master.jpg',
      size: 1572864, // 1.5MB
      type: 'image/jpeg',
      preview: 'https://placehold.co/200x150/F39C12/white?text=Bedroom'
    },
    {
      id: 'file-4',
      file: new File([''], 'office-space.jpg', { type: 'image/jpeg' }),
      name: 'office-space.jpg',
      size: 2097152, // 2MB
      type: 'image/jpeg',
      preview: 'https://placehold.co/200x150/52D252/white?text=Office'
    },
    {
      id: 'file-5',
      file: new File([''], 'dining-room.jpg', { type: 'image/jpeg' }),
      name: 'dining-room.jpg',
      size: 1887436, // 1.8MB
      type: 'image/jpeg',
      preview: 'https://placehold.co/200x150/E74C3C/white?text=Dining+Room'
    }
  ];
  
  let dragActive = false;
  let optionsExpanded = true; // Show options expanded
  let faceLimit = 10000;
  let isAuto = true;
  let uploading = false;
  let fileInput;
  
  // Constants
  const MAX_FILES = 25;
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png'];
  
  // Reactive statements
  $: fileCount = files.length;
  $: canGenerate = files.length > 0 && !uploading;
  $: faceLimitDisplay = faceLimit === 0 ? 'Auto' : faceLimit.toLocaleString();
  
  // Breadcrumb configuration
  let breadcrumbItems = [
    { name: 'Home', href: '/' },
    { name: 'Upload', href: '/upload', current: true }
  ];
  
  // File handling functions
  function removeFile(id) {
    files = files.filter(f => f.id !== id);
  }
  
  function handleDrop(e) {
    e.preventDefault();
    dragActive = false;
    // In real app, would process dropped files
  }
  
  function handleDragOver(e) {
    e.preventDefault();
    dragActive = true;
  }
  
  function handleDragLeave(e) {
    e.preventDefault();
    dragActive = false;
  }
  
  function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  function setFaceLimit(value) {
    faceLimit = parseInt(value);
    isAuto = false;
  }
  
  async function handleSubmit(e) {
    e.preventDefault();
    
    if (!canGenerate || uploading) return;
    
    uploading = true;
    
    // In dev mode, just navigate to processing page
    setTimeout(() => {
      goto('/dev/processing-active');
    }, 1000);
  }
</script>

<Navbar />

<main class="upload-page">
  <Hero 
    title="Upload Your Images"
    subtitle="Transform photos into professional 3D models in minutes"
  />
  
  <Breadcrumb items={breadcrumbItems} />
  
  <section class="upload-section">
    <div class="container">
      <form on:submit={handleSubmit} class="upload-form">
        <!-- File Preview Section (visible with files) -->
        <div class="file-preview-section animate-fade-in">
          <div class="preview-header">
            <h3>Selected Files ({files.length})</h3>
            <span class="preview-info">Total: {formatBytes(files.reduce((sum, f) => sum + f.size, 0))}</span>
          </div>
          <div class="file-preview-grid" use:staggerReveal>
            {#each files as file (file.id)}
              <div class="file-preview-item" data-stagger>
                <img src={file.preview} alt={file.name} class="file-preview-image" />
                <div class="file-info">
                  <span class="file-name">{file.name}</span>
                  <span class="file-size">{formatBytes(file.size)}</span>
                </div>
                <button type="button" class="remove-file" on:click={() => removeFile(file.id)}>
                  <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                  </svg>
                </button>
              </div>
            {/each}
          </div>
        </div>
        
        <!-- Upload Area (smaller when files present) -->
        <div class="upload-area {dragActive ? 'drag-over' : ''} {files.length > 0 ? 'compact' : ''}"
             on:drop={handleDrop}
             on:dragover={handleDragOver}
             on:dragleave={handleDragLeave}>
          <input 
            type="file" 
            id="file-input" 
            class="file-input" 
            multiple 
            accept=".jpg,.jpeg,.png,.heic"
            bind:this={fileInput}
          />
          <label for="file-input" class="upload-label">
            <div class="upload-icon">
              <svg width="48" height="48" fill="currentColor" viewBox="0 0 20 20">
                <path d="M16.88 9.1A4 4 0 0116 17H5a5 5 0 01-1-9.9V7a3 3 0 014.52-2.59A4.98 4.98 0 0117 8c0 .38-.04.74-.12 1.1zM11 11h3l-4-4-4 4h3v3h2v-3z"/>
              </svg>
            </div>
            <span class="upload-text">
              {files.length > 0 ? 'Add more images' : 'Drop images here or click to browse'}
            </span>
            <span class="upload-info">Supports JPEG, PNG • Max 10MB per file • Up to 25 images</span>
          </label>
        </div>
        
        <!-- Advanced Options -->
        <div class="options-section">
          <button type="button" 
                  class="options-toggle {optionsExpanded ? 'active' : ''}"
                  on:click={() => optionsExpanded = !optionsExpanded}>
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20" class="toggle-icon">
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
            </svg>
            Advanced Settings
          </button>
          
          <div class="options-content {optionsExpanded ? 'active' : ''}">
            <div class="option-group">
              <label class="option-label">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
                </svg>
                Face Limit Control
              </label>
              <p class="option-description">Higher values preserve more detail but take longer to process</p>
              
              <div class="face-limit-presets">
                <button type="button" 
                        class="preset-btn {isAuto ? 'active' : ''}"
                        on:click={() => { faceLimit = 0; isAuto = true; }}>
                  Auto
                </button>
                <button type="button" 
                        class="preset-btn {!isAuto && faceLimit === 5000 ? 'active' : ''}"
                        on:click={() => setFaceLimit(5000)}>
                  Low (5K)
                </button>
                <button type="button" 
                        class="preset-btn {!isAuto && faceLimit === 10000 ? 'active' : ''}"
                        on:click={() => setFaceLimit(10000)}>
                  Medium (10K)
                </button>
                <button type="button" 
                        class="preset-btn {!isAuto && faceLimit === 20000 ? 'active' : ''}"
                        on:click={() => setFaceLimit(20000)}>
                  High (20K)
                </button>
              </div>
              
              <div class="face-limit-slider">
                <input type="range" 
                       min="1000" 
                       max="50000" 
                       step="1000" 
                       bind:value={faceLimit}
                       on:input={() => isAuto = false}
                       disabled={isAuto}
                       class="slider">
                <span class="slider-value">{faceLimitDisplay}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Generate Button -->
        <div class="form-actions">
          <Button 
            type="submit" 
            variant="primary" 
            size="lg"
            disabled={!canGenerate}
            class="generate-btn hover-lift">
            {#if uploading}
              <span class="spinner"></span>
              Uploading...
            {:else}
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 1.414L10.586 9.5H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"/>
              </svg>
              Generate 3D Models
            {/if}
          </Button>
          <p class="form-hint">
            {files.length} {files.length === 1 ? 'file' : 'files'} selected • 
            Estimated time: {files.length * 15} seconds
          </p>
        </div>
      </form>
      
      <!-- Tips Section -->
      <div class="tips-section">
        <h3>
          <svg width="24" height="24" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"/>
          </svg>
          Tips for Best Results
        </h3>
        <div class="tips-grid">
          <div class="tip-card">
            <h4>Multiple Angles</h4>
            <p>Upload 3-8 photos from different angles for more accurate 3D reconstruction</p>
          </div>
          <div class="tip-card">
            <h4>Good Lighting</h4>
            <p>Use well-lit photos without harsh shadows for better texture mapping</p>
          </div>
          <div class="tip-card">
            <h4>Clear Background</h4>
            <p>Simple backgrounds help the AI focus on the main subject</p>
          </div>
        </div>
      </div>
    </div>
  </section>
  
  <!-- Dev Note -->
  <section class="dev-note">
    <div class="container">
      <div class="note-card">
        <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
        </svg>
        <p>Dev Mode: This shows the upload page with 5 files already selected. Advanced options are expanded.</p>
        <Button href="/dev" variant="ghost" size="sm">Back to Dev Index</Button>
      </div>
    </div>
  </section>
</main>

<Footer />

<style>
  @import '../../../css/upload-page.css';
  
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
</style>
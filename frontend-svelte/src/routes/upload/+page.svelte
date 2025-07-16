<script>
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { scrollReveal, staggerReveal } from '$lib/actions/animations.js';
  import { toast } from '$lib/stores/toast.js';
  import { page } from '$app/stores';
  import { apiKey } from '$lib/stores/auth.js';
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Breadcrumb from '$lib/components/Breadcrumb.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import ProgressIndicator from '$lib/components/ProgressIndicator.svelte';
  import ImageGrid from '$lib/components/ImageGrid.svelte';
  import Slider from '$lib/components/Slider.svelte';
  import api from '$lib/services/api';
  
  // Check if we're in dev mode
  $: isDevMode = $page.url.searchParams.get('dev') === 'true';
  
  // Dev mode mock files
  const mockFiles = [
    {
      id: 'dev-1',
      name: 'modern-chair-view1.jpg',
      size: 2457600,
      preview: 'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=400&h=400&fit=crop'
    },
    {
      id: 'dev-2',
      name: 'wooden-table-angle2.jpg',
      size: 3145728,
      preview: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop'
    },
    {
      id: 'dev-3',
      name: 'minimalist-lamp.jpg',
      size: 1572864,
      preview: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop'
    },
    {
      id: 'dev-4',
      name: 'velvet-sofa-front.jpg',
      size: 2097152,
      preview: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop'
    },
    {
      id: 'dev-5',
      name: 'office-desk-setup.jpg',
      size: 1887436,
      preview: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=400&h=400&fit=crop'
    },
    {
      id: 'dev-6',
      name: 'bookshelf-walnut.jpg',
      size: 2621440,
      preview: 'https://images.unsplash.com/photo-1594736797933-d0501ba2fe65?w=400&h=400&fit=crop'
    }
  ];
  
  // State management
  let files = [];
  let dragActive = false;
  let optionsExpanded = false;
  let uploading = false;
  let fileInput;
  
  // New state for model selection
  let selectedQuality = 'standard'; // 'standard' or 'max'
  let modelsInfo = {
    tripo3d: null,
    trellis: null
  };
  let advancedParams = {}; // Dynamic parameters based on selected model
  
  // Constants
  const MAX_FILES = 25;
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png'];
  
  // Object URLs for cleanup
  let objectUrls = [];
  
  // Reactive statements
  $: fileCount = files.length;
  $: canGenerate = files.length > 0 && !uploading;
  $: currentModelName = selectedQuality === 'standard' ? 'tripo3d' : 'trellis';
  $: currentModelInfo = modelsInfo[currentModelName];
  
  // Update advanced params when model changes
  $: if (currentModelInfo && currentModelInfo.param_schema) {
    advancedParams = getDefaultParams(currentModelInfo.param_schema);
  }
  
  // Helper functions
  function getDefaultParams(schema) {
    const params = {};
    if (schema && schema.properties) {
      Object.entries(schema.properties).forEach(([key, prop]) => {
        if (prop.default !== undefined) {
          params[key] = prop.default;
        }
      });
    }
    return params;
  }
  
  async function fetchModelParams(modelName) {
    try {
      const response = await api.getModelParams(modelName);
      if (response.success) {
        modelsInfo[modelName] = response.data;
      }
    } catch (error) {
      console.error(`Failed to fetch params for ${modelName}:`, error);
    }
  }
  
  // Lifecycle
  onMount(async () => {
    // Set API key if available
    if ($apiKey) {
      api.setApiKey($apiKey);
    }
    
    // Load mock files if in dev mode
    if (isDevMode) {
      files = mockFiles;
      optionsExpanded = true;
    }
    
    // Fetch model parameters for both models
    await Promise.all([
      fetchModelParams('tripo3d'),
      fetchModelParams('trellis')
    ]);
    
    return () => {
      // Cleanup object URLs on component destroy
      objectUrls.forEach(url => URL.revokeObjectURL(url));
    };
  });
  
  // File handling
  function handleFileSelect(e) {
    const selectedFiles = Array.from(e.target.files);
    processFiles(selectedFiles);
    // Reset input to allow re-selecting same files
    e.target.value = '';
  }
  
  function processFiles(newFiles) {
    const validFiles = [];
    const errors = [];
    
    newFiles.forEach(file => {
      // Validate file type
      if (!ALLOWED_TYPES.includes(file.type)) {
        errors.push(`${file.name}: Invalid file type. Only JPG and PNG allowed.`);
        return;
      }
      
      // Validate file size
      if (file.size > MAX_FILE_SIZE) {
        errors.push(`${file.name}: File too large. Maximum size is 10MB.`);
        return;
      }
      
      // Check total file count
      if (files.length + validFiles.length >= MAX_FILES) {
        errors.push(`Maximum ${MAX_FILES} files allowed.`);
        return;
      }
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      objectUrls.push(url);
      
      validFiles.push({
        id: Date.now() + Math.random(),
        file,
        name: file.name,
        size: file.size,
        url,
        uploading: false,
        progress: 0
      });
    });
    
    // Update files array
    files = [...files, ...validFiles];
    
    // Show errors if any
    if (errors.length > 0) {
      errors.forEach(error => toast.error(error));
    }
  }
  
  // Drag and drop handlers
  function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dragActive = true;
  }
  
  function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    if (e.currentTarget.contains(e.relatedTarget)) return;
    dragActive = false;
  }
  
  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dragActive = false;
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    processFiles(droppedFiles);
  }
  
  // File management
  function removeFile(id) {
    const fileToRemove = files.find(f => f.id === id);
    if (fileToRemove) {
      URL.revokeObjectURL(fileToRemove.url);
      files = files.filter(f => f.id !== id);
    }
  }
  
  function clearAll() {
    files.forEach(f => URL.revokeObjectURL(f.url));
    files = [];
  }
  
  // Options handling
  function toggleOptions() {
    optionsExpanded = !optionsExpanded;
  }
  
  // Form submission with retry logic
  async function handleSubmit(e) {
    e.preventDefault();
    
    // Validate upload state
    
    if (!canGenerate || uploading) {
      return;
    }
    
    // Check if API key is available
    if (!$apiKey) {
      toast.error('Application is still loading. Please try again in a moment.');
      return;
    }
    
    // Make sure API service has the key
    if (!api.API_KEY || api.API_KEY !== $apiKey) {
      api.setApiKey($apiKey);
    }
    
    uploading = true;
    
    try {
      // Store file info in session for processing page
      if (browser) {
        const fileNames = files.map(f => f.name);
        sessionStorage.setItem('processingFiles', JSON.stringify({
          files: fileNames,
          taskId: null // Will be updated after upload
        }));
      }
      
      // Use the API service with retry logic
      let result;
      try {
        // Call uploadBatch with model type and params
        result = await api.uploadBatch(files, currentModelName, advancedParams);
      } catch (uploadError) {
        throw uploadError;
      }
      
      // Process upload result
      
      if (result.success) {
        // Update session storage with task ID
        if (browser) {
          const data = JSON.parse(sessionStorage.getItem('processingFiles') || '{}');
          data.taskId = result.taskId || result.batchId || result.jobId;
          sessionStorage.setItem('processingFiles', JSON.stringify(data));
        }
        
        toast.success('Files uploaded successfully!');
        
        // Navigate to processing page
        const taskId = result.taskId || result.batchId || result.jobId;
        
        if (taskId && browser) {
          await goto(`/processing?taskId=${taskId}`);
        }
      } else {
        throw new Error(result.error || 'Upload failed');
      }
    } catch (error) {
      toast.error(`Failed to upload files: ${error.message || error}`);
    } finally {
      uploading = false;
    }
  }
  
  // Helper functions
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
</script>

<!-- Navigation Bar -->
<Navbar />

<!-- Breadcrumb Navigation -->
<Breadcrumb 
  items={[
    { label: 'Home', href: '/' },
    { label: 'Upload', current: true },
    { label: 'Processing' },
    { label: 'Results' }
  ]}
/>

<!-- Hero Section -->
<Hero 
  title="Upload Your Images"
  subtitle="Transform photos into professional 3D models in minutes"
>
  <div slot="content" class="animate-fade-in-scale delay-400">
    <ProgressIndicator currentStep={1} />
  </div>
</Hero>

<!-- Main Content -->
<main>
  <!-- Upload Section -->
  <section class="upload-section">
    <div class="container">
      <div class="upload-wrapper">
        <form on:submit={handleSubmit}>
          <!-- Upload Zone -->
          <div class="upload-zone-wrapper animate-fade-in-up delay-400">
            <label 
              class="upload-area {dragActive ? 'drag-over' : ''}"
              on:dragover={handleDragOver}
              on:dragleave={handleDragLeave}
              on:drop={handleDrop}
              on:dragenter|preventDefault
            >
              <input 
                bind:this={fileInput}
                type="file" 
                multiple 
                accept=".jpg,.jpeg,.png" 
                on:change={handleFileSelect}
                class="file-input"
              >
              <div class="upload-content">
                <svg class="upload-icon" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M5.5 13a3.5 3.5 0 01-.369-6.98 4 4 0 117.753-1.977A4.5 4.5 0 1113.5 13H11V9.413l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13H5.5z"/>
                  <path d="M9 13h2v5a1 1 0 11-2 0v-5z"/>
                </svg>
                <h3 class="upload-title">Drop images here or click to browse</h3>
                <p class="upload-info">
                  Supports JPEG, PNG • Max 10MB per file • Up to 25 images
                </p>
              </div>
            </label>
          </div>

          <!-- File Preview Gallery -->
          {#if files.length > 0}
            <div class="file-preview-section animate-fade-in">
              <div class="file-preview-header">
                <div class="file-count">
                  <span>{fileCount}</span> {fileCount === 1 ? 'image' : 'images'} selected
                </div>
                <div class="file-actions">
                  <button type="button" class="btn btn-ghost btn-sm" on:click={clearAll}>
                    Clear All
                  </button>
                  <button type="button" class="btn btn-secondary btn-sm" on:click={() => fileInput.click()}>
                    Add More Images
                  </button>
                </div>
              </div>
              <ImageGrid 
                items={files.map(f => ({ ...f, preview: f.url || f.preview }))} 
                onRemove={removeFile}
                gridSize="medium"
              />
            </div>
          {/if}

          <!-- Quality Selection -->
          <div class="quality-selection animate-fade-in delay-600">
            <h3 class="quality-title">Choose Quality</h3>
            <div class="quality-options">
              <label class="quality-option {selectedQuality === 'standard' ? 'selected' : ''}">
                <input 
                  type="radio" 
                  name="quality" 
                  value="standard" 
                  bind:group={selectedQuality}
                  class="quality-radio"
                >
                <div class="quality-content">
                  <div class="quality-header">
                    <span class="quality-name">Standard</span>
                    <span class="quality-badge">Tripo3D</span>
                  </div>
                  <div class="quality-info">
                    <span class="quality-credits">0.5 credits per image</span>
                  </div>
                </div>
              </label>
              
              <label class="quality-option {selectedQuality === 'max' ? 'selected' : ''}">
                <input 
                  type="radio" 
                  name="quality" 
                  value="max" 
                  bind:group={selectedQuality}
                  class="quality-radio"
                >
                <div class="quality-content">
                  <div class="quality-header">
                    <span class="quality-name">Max</span>
                    <span class="quality-badge">Trellis</span>
                  </div>
                  <div class="quality-info">
                    <span class="quality-credits">2 credits per image</span>
                  </div>
                </div>
              </label>
            </div>
            <div class="credit-info">
              <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
              </svg>
              <span>Credits are deducted per image processed</span>
            </div>
          </div>

          <!-- Advanced Options Panel -->
          <div class="advanced-options animate-fade-in delay-700">
            <button type="button" class="options-toggle" class:active={optionsExpanded} on:click={toggleOptions}>
              <div class="options-toggle-text">
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/>
                </svg>
                <span>Advanced Settings</span>
              </div>
              <svg class="options-toggle-icon" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
              </svg>
            </button>
            
            {#if optionsExpanded && currentModelInfo}
              <div class="options-content active" use:scrollReveal>
                {#if currentModelInfo.param_schema && currentModelInfo.param_schema.properties}
                  {#each Object.entries(currentModelInfo.param_schema.properties) as [key, prop]}
                    <div class="param-control">
                      {#if prop.type === 'boolean'}
                        <label class="param-checkbox-label">
                          <input 
                            type="checkbox" 
                            bind:checked={advancedParams[key]}
                            class="param-checkbox"
                          >
                          <span class="param-label">{prop.title || key}</span>
                        </label>
                        {#if prop.description}
                          <p class="param-description">{prop.description}</p>
                        {/if}
                      {:else if prop.type === 'integer' || prop.type === 'number'}
                        <Slider
                          bind:value={advancedParams[key]}
                          min={prop.minimum || 0}
                          max={prop.maximum || 100}
                          step={prop.type === 'integer' ? 1 : 0.1}
                          label={prop.title || key}
                          description={prop.description}
                        />
                      {:else if prop.enum}
                        <div class="param-select-group">
                          <label for={key} class="param-label">
                            {prop.title || key}
                          </label>
                          <select 
                            id={key}
                            bind:value={advancedParams[key]}
                            class="param-select"
                          >
                            {#each prop.enum as option}
                              <option value={option}>{option}</option>
                            {/each}
                          </select>
                          {#if prop.description}
                            <p class="param-description">{prop.description}</p>
                          {/if}
                        </div>
                      {:else}
                        <div class="param-input-group">
                          <label for={key} class="param-label">
                            {prop.title || key}
                          </label>
                          <input 
                            type="text" 
                            id={key}
                            bind:value={advancedParams[key]}
                            class="param-input"
                          >
                          {#if prop.description}
                            <p class="param-description">{prop.description}</p>
                          {/if}
                        </div>
                      {/if}
                    </div>
                  {/each}
                {:else}
                  <p class="no-params">No advanced settings available for {currentModelName}.</p>
                {/if}
              </div>
            {/if}
          </div>

          <!-- Action Section -->
          <div class="upload-actions animate-fade-in delay-800">
            <div class="upload-actions-primary">
              <Button 
                type="submit" 
                variant="primary"
                size="lg"
                disabled={!canGenerate}
                loading={uploading}
              >
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zM4 6h12v10H4V6z" clip-rule="evenodd"/>
                </svg>
                {uploading ? 'Uploading...' : 'Generate 3D Models'}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </section>

  <!-- Help Section -->
  <section class="help-tips-section">
    <div class="container">
      <div class="help-section animate-fade-in delay-1000">
        <div class="help-header">
          <h2 class="help-title">Tips for Best Results</h2>
        </div>
        <div class="help-grid" use:staggerReveal>
          <div class="help-card hover-lift" data-stagger>
            <div class="help-card-icon">
              <svg fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"/>
              </svg>
            </div>
            <h3 class="help-card-title">Use Well-Lit Photos</h3>
            <p class="help-card-text">
              Good lighting helps our AI better understand the shape and details of your subject.
            </p>
          </div>
          <div class="help-card hover-lift" data-stagger>
            <div class="help-card-icon">
              <svg fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
              </svg>
            </div>
            <h3 class="help-card-title">Avoid Blurry Images</h3>
            <p class="help-card-text">
              Sharp, focused images produce cleaner 3D models with better defined edges.
            </p>
          </div>
          <div class="help-card hover-lift" data-stagger>
            <div class="help-card-icon">
              <svg fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"/>
              </svg>
            </div>
            <h3 class="help-card-title">Multiple Angles</h3>
            <p class="help-card-text">
              Upload photos from different angles for more complete 3D reconstruction.
            </p>
          </div>
        </div>
        <div class="example-images">
          <h3 class="example-images-title">Example Images That Work Well</h3>
          <div class="example-images-grid">
            <img src="/assets/examples/jordan1s-before.jpg" alt="Good example - Sneakers" class="example-image hover-scale" loading="lazy">
            <img src="/assets/examples/jacket-before.png" alt="Good example - Jacket" class="example-image hover-scale" loading="lazy">
            <img src="/assets/examples/chair-before.png" alt="Good example - Chair" class="example-image hover-scale" loading="lazy">
          </div>
        </div>
      </div>
    </div>
  </section>
</main>

<!-- Footer -->
<Footer />

<style>
  /* Import upload page specific styles */
  @import '/css/upload-page.css';
  
  :global(.navbar) {
    background-color: rgba(26, 35, 50, 0.98);
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  }
  
  :global(.btn-primary) {
    background: linear-gradient(135deg, #5dade2 0%, #3498db 100%) !important;
    color: #ffffff !important;
    font-weight: 600;
    border: none;
  }
  
  :global(.btn-primary:hover:not(:disabled)) {
    background: linear-gradient(135deg, #3498db 0%, #2874a6 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 14px 0 rgba(93, 173, 226, 0.4);
  }
  
  :global(.btn-primary:disabled) {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  :global(.upload-section) {
    background-color: #f8f9fa;
  }
  
  :global(.help-tips-section) {
    background-color: #ffffff;
  }
  
  /* File preview section visibility */
  .file-preview-section {
    display: block !important;
    margin-top: 2rem;
  }
  
  /* New upload area styles */
  :global(.upload-area) {
    display: block;
    width: 100%;
    padding: 3rem 2rem;
    background: white;
    border: 2px dashed #e0e0e0;
    border-radius: 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
  }
  
  :global(.upload-area:hover) {
    border-color: #2196f3;
    background: #f5f5f5;
  }
  
  :global(.upload-area.drag-over) {
    border-color: #2196f3;
    background: #e3f2fd;
  }
  
  :global(.file-input) {
    position: absolute;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
  }
  
  :global(.upload-content) {
    pointer-events: none;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  
  :global(.upload-icon) {
    width: 48px;
    height: 48px;
    color: #2196f3;
    margin-bottom: 1rem;
  }
  
  :global(.upload-title) {
    font-size: 1.25rem;
    color: #1a202c;
    margin-bottom: 0.5rem;
    font-weight: 600;
    text-align: center;
  }
  
  :global(.upload-info) {
    color: #666;
    font-size: 0.875rem;
    margin: 0;
    text-align: center;
    width: 100%;
  }
  
  /* Quality Selection Styles */
  :global(.quality-selection) {
    margin-bottom: 2rem;
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }
  
  :global(.quality-title) {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1a202c;
    margin-bottom: 1rem;
  }
  
  :global(.quality-options) {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
  }
  
  :global(.quality-option) {
    display: block;
    position: relative;
    cursor: pointer;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    padding: 1rem;
    transition: all 0.3s ease;
    background: white;
  }
  
  :global(.quality-option:hover) {
    border-color: #2196f3;
    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.15);
  }
  
  :global(.quality-option.selected) {
    border-color: #2196f3;
    background: #e3f2fd;
  }
  
  :global(.quality-radio) {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
  }
  
  :global(.quality-content) {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  :global(.quality-header) {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  :global(.quality-name) {
    font-size: 1rem;
    font-weight: 600;
    color: #1a202c;
  }
  
  :global(.quality-badge) {
    font-size: 0.75rem;
    font-weight: 500;
    color: #2196f3;
    background: rgba(33, 150, 243, 0.1);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }
  
  :global(.quality-info) {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  :global(.quality-credits) {
    font-size: 0.875rem;
    color: #666;
  }
  
  :global(.credit-info) {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #666;
  }
  
  :global(.credit-info svg) {
    color: #2196f3;
  }
  
  /* Parameter Control Styles */
  :global(.param-control) {
    margin-bottom: 1.5rem;
  }
  
  :global(.param-checkbox-label) {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }
  
  :global(.param-checkbox) {
    width: 1.25rem;
    height: 1.25rem;
    cursor: pointer;
  }
  
  :global(.param-label) {
    font-size: 0.875rem;
    font-weight: 600;
    color: #334155;
  }
  
  :global(.param-description) {
    font-size: 0.8125rem;
    color: #666;
    margin-top: 0.25rem;
    line-height: 1.5;
  }
  
  :global(.param-select-group),
  :global(.param-input-group) {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  :global(.param-select),
  :global(.param-input) {
    padding: 0.5rem 0.75rem;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    font-size: 0.875rem;
    transition: all 0.2s ease;
  }
  
  :global(.param-select:focus),
  :global(.param-input:focus) {
    outline: none;
    border-color: #2196f3;
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
  }
  
  :global(.no-params) {
    text-align: center;
    color: #666;
    font-size: 0.875rem;
    padding: 2rem;
  }
  
  /* Face limit preset buttons */
  :global(.preset-btn) {
    flex: 1;
    padding: 0.5rem 1rem;
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    color: #666;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  :global(.preset-btn:hover) {
    border-color: #2196f3;
    color: #2196f3;
    background: #e3f2fd;
  }
  
  :global(.preset-btn.active) {
    background: #2196f3;
    color: white;
    border-color: #2196f3;
    box-shadow: 0 2px 4px rgba(33, 150, 243, 0.2);
  }
  
  :global(.preset-btn.active:hover) {
    background: #1976d2;
    border-color: #1976d2;
  }
</style>
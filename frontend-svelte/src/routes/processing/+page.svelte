<script>
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { toast } from '$lib/stores/toast';
  import { scrollReveal, staggerReveal } from '$lib/actions/animations';
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Breadcrumb from '$lib/components/Breadcrumb.svelte';
  import Button from '$lib/components/Button.svelte';

  // State management
  let taskId = '';
  let files = [];
  let overallProgress = 0;
  let filesCompleted = 0;
  let totalFiles = 0;
  let startTime = Date.now();
  let elapsedTime = 0;
  let eventSource = null;
  let isProcessing = true;
  let elapsedInterval = null;
  let currentView = 'grid'; // 'grid' or 'list'
  let currentTipIndex = 0;

  // Tips for carousel
  const tips = [
    {
      icon: '💡',
      text: 'Our AI analyzes each image from multiple angles to create the most accurate 3D representation possible.'
    },
    {
      icon: '🚀',
      text: 'Processing time varies based on image complexity and detail level selected. Higher detail takes longer but produces better results.'
    },
    {
      icon: '🎯',
      text: 'The generated 3D models are compatible with most 3D software including Blender, Unity, and Unreal Engine.'
    }
  ];

  // Breadcrumb items
  const breadcrumbItems = [
    { label: 'Home', href: '/' },
    { label: 'Upload', href: '/upload' },
    { label: 'Processing', current: true },
    { label: 'Results' }
  ];

  // Parse task ID from URL
  $: {
    taskId = $page.url.searchParams.get('batch') || '';
    if (!taskId && typeof window !== 'undefined') {
      toast.error('No batch ID provided');
      goto('/upload');
    }
  }

  // Initialize processing
  onMount(async () => {
    if (!taskId) return;

    // Start elapsed time counter
    elapsedInterval = setInterval(() => {
      elapsedTime = Math.floor((Date.now() - startTime) / 1000);
    }, 1000);

    // Start tips carousel
    const tipsInterval = setInterval(() => {
      currentTipIndex = (currentTipIndex + 1) % tips.length;
    }, 5000);

    // Try to get file information from sessionStorage
    try {
      const storedData = sessionStorage.getItem('processingFiles');
      if (storedData) {
        const data = JSON.parse(storedData);
        if (data.taskId === taskId && data.files) {
          // We have the actual filenames!
          totalFiles = data.files.length;
          files = data.files.map((name, i) => ({
            id: `file-${i}`,
            name: name,
            status: 'pending',
            progress: 0,
            message: 'Waiting to start...'
          }));
        }
      }
    } catch (e) {
      console.log('Could not retrieve file information from session');
    }

    // If we don't have file info, we'll get it from SSE
    if (files.length === 0) {
      totalFiles = 1; // Will be updated from SSE
      files = [];
    }

    // Connect to SSE for real-time updates
    connectToSSE();

    return () => {
      clearInterval(tipsInterval);
    };
  });

  onDestroy(() => {
    if (eventSource) {
      eventSource.close();
    }
    if (elapsedInterval) {
      clearInterval(elapsedInterval);
    }
  });

  // Connect to Server-Sent Events
  function connectToSSE() {
    if (!taskId) return;

    eventSource = new EventSource(`/api/v1/status/tasks/${taskId}/stream`);

    eventSource.addEventListener('task_progress', (event) => {
      const data = JSON.parse(event.data);
      handleProgressUpdate(data);
    });

    eventSource.addEventListener('task_completed', (event) => {
      const data = JSON.parse(event.data);
      handleCompletion(data);
    });

    eventSource.addEventListener('task_failed', (event) => {
      const data = JSON.parse(event.data);
      isProcessing = false;
      toast.error(`Processing failed: ${data.error || 'Unknown error'}`);
    });

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      if (eventSource.readyState === EventSource.CLOSED) {
        // Attempt to reconnect after 5 seconds
        setTimeout(connectToSSE, 5000);
      }
    };
  }

  // Handle progress updates
  function handleProgressUpdate(data) {
    // Update overall progress from SSE data
    if (data.progress !== undefined) {
      overallProgress = Math.round(data.progress);
    }

    // Update file counts if provided
    if (data.total_files !== undefined) {
      totalFiles = data.total_files;
    }
    if (data.total !== undefined && data.total > 0) {
      totalFiles = data.total;
    }

    // Update current/completed count
    if (data.current !== undefined) {
      filesCompleted = data.current;
    }

    // For now, show a simple message about progress
    // Later this will show individual file progress
    if (data.message || overallProgress > 0) {
      // Update the files array to show some progress
      if (files.length === 0 && totalFiles > 0) {
        // Create placeholder files only if we don't have actual names
        files = Array.from({ length: totalFiles }, (_, i) => ({
          id: `file-${i}`,
          name: `Image ${i + 1}`,
          status: i < filesCompleted ? 'completed' : 'processing',
          progress: i < filesCompleted ? 100 : Math.round((overallProgress / totalFiles)),
          message: i < filesCompleted ? 'Completed' : data.message || 'Processing...'
        }));
      } else if (files.length > 0) {
        // Update existing files (preserving actual names)
        files = files.map((file, i) => ({
          ...file,
          status: i < filesCompleted ? 'completed' : (filesCompleted === i ? 'processing' : 'pending'),
          progress: i < filesCompleted ? 100 : (filesCompleted === i ? Math.round((overallProgress / totalFiles)) : 0),
          message: i < filesCompleted ? 'Completed' : (filesCompleted === i ? (data.message || 'Processing...') : 'Waiting...')
        }));
      }
    }
  }

  // Handle batch completion
  function handleCompletion(data) {
    isProcessing = false;
    if (eventSource) {
      eventSource.close();
    }
    
    toast.success('Processing complete!');
    // Redirect disabled for testing
    // setTimeout(() => {
    //   goto(`/results?batch=${taskId}`);
    // }, 2000);
  }

  // Cancel processing
  async function cancelProcessing() {
    const confirmed = confirm('Are you sure you want to cancel processing? This action cannot be undone.');
    if (!confirmed) return;

    try {
      // For now, just close the connection and navigate away
      // TODO: Implement proper cancellation when backend endpoint is available
      if (eventSource) {
        eventSource.close();
      }
      
      toast.info('Leaving processing page');
      goto('/upload');
    } catch (error) {
      console.error('Error cancelling processing:', error);
      toast.error('Failed to cancel processing');
    }
  }

  // Format elapsed time
  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
  }

  // Format start time
  function formatStartTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
  }

  // Get status color
  function getStatusColor(status) {
    switch (status) {
      case 'completed': return '#22c55e';
      case 'processing': return '#5DADE2';
      case 'failed': return '#ef4444';
      default: return '#94a3b8';
    }
  }

  // Toggle view
  function toggleView(view) {
    currentView = view;
  }
</script>

<svelte:head>
  <title>Processing - image2model</title>
  <meta name="description" content="Processing your images into 3D models using AI technology." />
</svelte:head>

<Navbar variant="default" />

<!-- Breadcrumb Navigation -->
<section class="breadcrumb-section">
  <div class="container">
    <Breadcrumb items={breadcrumbItems} />
  </div>
</section>

<!-- Hero Section -->
<section class="processing-hero">
  <div class="geometric-pattern"></div>
  <div class="container">
    <div class="processing-hero-content" use:scrollReveal>
      <h1 class="animate-fade-in-up">Processing Your Images</h1>
      <p class="processing-hero-subtitle animate-fade-in-up delay-200">
        Your 3D models are being generated
      </p>
      <div class="progress-indicator animate-fade-in-scale delay-400">
        <div class="progress-step complete">
          <span class="progress-step-number">✓</span>
          <span class="progress-step-text">Upload</span>
        </div>
        <div class="progress-step active">
          <span class="progress-step-number">2</span>
          <span class="progress-step-text">Process</span>
        </div>
        <div class="progress-step">
          <span class="progress-step-number">3</span>
          <span class="progress-step-text">Download</span>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Main Content -->
<main>
  <!-- Batch Information Section -->
  <section class="batch-info-section">
    <div class="container">
      <div class="batch-details card" use:scrollReveal>
        <div class="batch-item">
          <div class="batch-icon">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 8a6 6 0 01-7.743 5.743L10 14l-1 1-1 1H6v2H2v-4l4.257-4.257A6 6 0 1118 8zm-6-4a1 1 0 100 2 2 2 0 012 2 1 1 0 102 0 4 4 0 00-4-4z" clip-rule="evenodd"/>
            </svg>
          </div>
          <div>
            <span class="batch-label">Task ID</span>
            <span class="batch-value">{taskId || '-'}</span>
          </div>
        </div>
        <div class="batch-item">
          <div class="batch-icon">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/>
            </svg>
          </div>
          <div>
            <span class="batch-label">Files</span>
            <span class="batch-value">{totalFiles}</span>
          </div>
        </div>
        <div class="batch-item">
          <div class="batch-icon">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
            </svg>
          </div>
          <div>
            <span class="batch-label">Started</span>
            <span class="batch-value">{formatStartTime(startTime)}</span>
          </div>
        </div>
        <div class="batch-item">
          <div class="batch-icon">
            <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.707-10.293a1 1 0 00-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L9.414 11H13a1 1 0 100-2H9.414l1.293-1.293z" clip-rule="evenodd"/>
            </svg>
          </div>
          <div>
            <span class="batch-label">Elapsed</span>
            <span class="batch-value">{formatTime(elapsedTime)}</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Overall Progress Section -->
  <section class="overall-progress-section">
    <div class="container">
      <div class="progress-header" use:scrollReveal>
        <h2>Overall Progress</h2>
        <div class="progress-stats">
          {filesCompleted} of {totalFiles} files completed
        </div>
      </div>
      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-bar-fill" style="width: {overallProgress}%">
            <span class="progress-text">{overallProgress}%</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- File Processing Grid -->
  <section class="files-grid-section">
    <div class="container">
      <div class="section-header" use:scrollReveal>
        <h2>Processing Status</h2>
        <div class="grid-view-toggle">
          <button 
            class="view-btn {currentView === 'grid' ? 'active' : ''}" 
            on:click={() => toggleView('grid')}
            title="Grid view"
          >
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
            </svg>
          </button>
          <button 
            class="view-btn {currentView === 'list' ? 'active' : ''}" 
            on:click={() => toggleView('list')}
            title="List view"
          >
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="file-grid {currentView}" use:staggerReveal>
        {#each files as file (file.id)}
          <div class="file-card">
            <div class="file-card-header">
              <h3 class="file-name">{file.name}</h3>
              <span class="file-status" style="color: {getStatusColor(file.status)}">
                {file.status}
              </span>
            </div>
            <div class="file-progress">
              <div class="file-progress-bar">
                <div 
                  class="file-progress-fill" 
                  style="width: {file.progress}%; background-color: {getStatusColor(file.status)}"
                ></div>
              </div>
              <span class="file-progress-text">{file.progress}%</span>
            </div>
            <p class="file-message">{file.message}</p>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Tips Section -->
  <section class="tips-section">
    <div class="container">
      <div class="tips-content" use:scrollReveal>
        <h3>Did You Know?</h3>
        <div class="tips-carousel">
          {#each tips as tip, index}
            <div class="tip-card {index === currentTipIndex ? 'active' : ''}">
              <div class="tip-icon">{tip.icon}</div>
              <p>{tip.text}</p>
            </div>
          {/each}
        </div>
      </div>
    </div>
  </section>

  <!-- Action Buttons -->
  <section class="action-section">
    <div class="container">
      {#if isProcessing}
        <Button 
          variant="secondary" 
          on:click={cancelProcessing}
          class="hover-lift"
        >
          <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor" slot="icon">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
          Cancel Processing
        </Button>
      {:else}
        <Button 
          href="/results?batch={taskId}"
          class="hover-lift"
        >
          View Results
        </Button>
      {/if}
    </div>
  </section>
</main>

<Footer />

<style>
  /* Override body background for consistency */
  :global(body) {
    background-color: #f8f9fa !important;
  }

  /* Breadcrumb section */
  .breadcrumb-section {
    background-color: #f8f9fa;
    padding: 1rem 0;
  }

  /* Processing Hero */
  .processing-hero {
    background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);
    color: white;
    padding: 4rem 0 5rem;
    position: relative;
    overflow: hidden;
  }

  .geometric-pattern {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    opacity: 0.5;
  }

  .processing-hero-content {
    position: relative;
    z-index: 1;
    text-align: center;
  }

  .processing-hero-content h1 {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
  }

  .processing-hero-subtitle {
    font-size: 1.25rem;
    opacity: 0.9;
    margin-bottom: 2rem;
  }

  /* Progress Indicator */
  .progress-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 2rem;
    margin-top: 3rem;
  }

  .progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    position: relative;
  }

  .progress-step:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 1rem;
    left: 100%;
    width: 2rem;
    height: 2px;
    background: rgba(255, 255, 255, 0.3);
  }

  .progress-step.complete::after,
  .progress-step.active::after {
    background: white;
  }

  .progress-step-number {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
  }

  .progress-step.complete .progress-step-number {
    background: white;
    color: #2c3e50;
    border-color: white;
  }

  .progress-step.active .progress-step-number {
    background: white;
    color: #2c3e50;
    border-color: white;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7);
    }
    70% {
      box-shadow: 0 0 0 10px rgba(255, 255, 255, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
    }
  }

  .progress-step-text {
    font-size: 0.875rem;
    opacity: 0.9;
  }

  /* Batch Information */
  .batch-info-section {
    background-color: #f8f9fa;
    padding: 3rem 0;
  }

  .batch-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    padding: 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .batch-item {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .batch-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .batch-label {
    display: block;
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 0.25rem;
  }

  .batch-value {
    display: block;
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
  }

  /* Overall Progress */
  .overall-progress-section {
    background-color: #f8f9fa;
    padding: 0 0 3rem;
  }

  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .progress-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
  }

  .progress-stats {
    color: #64748b;
  }

  .progress-container {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .progress-bar {
    width: 100%;
    height: 30px;
    background: #e2e8f0;
    border-radius: 15px;
    overflow: hidden;
    position: relative;
  }

  .progress-bar-fill {
    height: 100%;
    background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);
    border-radius: 15px;
    transition: width 0.5s ease;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .progress-text {
    color: white;
    font-weight: 600;
    font-size: 0.875rem;
  }

  /* Files Grid */
  .files-grid-section {
    background-color: #f8f9fa;
    padding: 0 0 3rem;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .section-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
  }

  .grid-view-toggle {
    display: flex;
    gap: 0.5rem;
  }

  .view-btn {
    padding: 0.5rem;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    color: #64748b;
  }

  .view-btn:hover {
    background: #f1f5f9;
  }

  .view-btn.active {
    background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);
    color: white;
    border-color: transparent;
  }

  .file-grid {
    display: grid;
    gap: 1.5rem;
  }

  .file-grid.grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }

  .file-grid.list {
    grid-template-columns: 1fr;
  }

  .file-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .file-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  }

  .file-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .file-name {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .file-status {
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: capitalize;
  }

  .file-progress {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.5rem;
  }

  .file-progress-bar {
    flex: 1;
    height: 8px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
  }

  .file-progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
  }

  .file-progress-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: #64748b;
    min-width: 40px;
  }

  .file-message {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0;
  }

  /* Tips Section */
  .tips-section {
    background-color: #f8f9fa;
    padding: 0 0 3rem;
  }

  .tips-content {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    text-align: center;
  }

  .tips-content h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 1.5rem;
  }

  .tips-carousel {
    position: relative;
    height: 100px;
  }

  .tip-card {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    opacity: 0;
    transition: opacity 0.5s ease;
    padding: 0 2rem;
  }

  .tip-card.active {
    opacity: 1;
  }

  .tip-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  .tip-card p {
    color: #64748b;
    line-height: 1.6;
    margin: 0;
  }

  /* Action Section */
  .action-section {
    background-color: #f8f9fa;
    padding: 0 0 4rem;
    text-align: center;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .processing-hero-content h1 {
      font-size: 2rem;
    }

    .progress-indicator {
      gap: 1rem;
    }

    .progress-step:not(:last-child)::after {
      width: 1rem;
    }

    .batch-details {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    .file-grid.grid {
      grid-template-columns: 1fr;
    }

    .section-header {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }
  }
</style>
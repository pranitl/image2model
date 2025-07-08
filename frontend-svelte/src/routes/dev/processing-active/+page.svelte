<script>
  import { onMount, onDestroy } from 'svelte';
  import { scrollReveal, staggerReveal } from '$lib/actions/animations';
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Breadcrumb from '$lib/components/Breadcrumb.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import ProgressIndicator from '$lib/components/ProgressIndicator.svelte';
  import Icon from '$lib/components/Icon.svelte';
  
  // Mock processing state
  let taskId = 'demo-task-123';
  let overallProgress = 55;
  let filesCompleted = 3;
  let totalFiles = 5;
  let startTime = Date.now() - 45000; // Started 45 seconds ago
  let elapsedTime = 45;
  let isProcessing = true;
  let isCompleted = false;
  let currentView = 'grid';
  let currentTipIndex = 0;
  
  // Mock files with different states
  let files = [
    {
      id: 'file-1',
      name: 'living-room.jpg',
      status: 'completed',
      progress: 100,
      message: 'Completed - 3D model generated'
    },
    {
      id: 'file-2',
      name: 'kitchen-modern.png',
      status: 'completed',
      progress: 100,
      message: 'Completed - 3D model generated'
    },
    {
      id: 'file-3',
      name: 'bedroom-master.jpg',
      status: 'completed',
      progress: 100,
      message: 'Completed - 3D model generated'
    },
    {
      id: 'file-4',
      name: 'office-space.jpg',
      status: 'processing',
      progress: 75,
      message: 'Processing - Generating texture maps...'
    },
    {
      id: 'file-5',
      name: 'dining-room.jpg',
      status: 'pending',
      progress: 0,
      message: 'Queued - Waiting to process'
    }
  ];
  
  // Breadcrumb configuration
  let breadcrumbItems = [
    { name: 'Home', href: '/' },
    { name: 'Upload', href: '/upload' },
    { name: 'Processing', href: '#', current: true }
  ];
  
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
      text: 'The generated 3D models are compatible with most 3D software including Rhino, Vectorworks, Blender, Unity, and Unreal Engine.'
    }
  ];
  
  // Simulate progress updates
  let progressInterval;
  onMount(() => {
    progressInterval = setInterval(() => {
      elapsedTime++;
      
      // Update file progress
      files = files.map(file => {
        if (file.status === 'processing' && file.progress < 95) {
          return { ...file, progress: file.progress + Math.random() * 5 };
        }
        return file;
      });
      
      // Update overall progress
      const totalProgress = files.reduce((sum, f) => sum + f.progress, 0);
      overallProgress = Math.round(totalProgress / files.length);
    }, 1000);
    
    // Rotate tips
    const tipInterval = setInterval(() => {
      currentTipIndex = (currentTipIndex + 1) % tips.length;
    }, 5000);
    
    return () => {
      clearInterval(progressInterval);
      clearInterval(tipInterval);
    };
  });
  
  onDestroy(() => {
    if (progressInterval) clearInterval(progressInterval);
  });
  
  // Helper functions
  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
  }
  
  function formatStartTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
  }
  
  function getStatusColor(status) {
    switch (status) {
      case 'completed': return '#22c55e';
      case 'processing': return '#5DADE2';
      case 'failed': return '#ef4444';
      default: return '#94a3b8';
    }
  }
  
  function toggleView(view) {
    currentView = view;
  }
  
  async function cancelProcessing() {
    console.log('Cancel processing clicked');
  }
</script>

<Navbar />

<main class="processing-page">
  <Hero 
    title="Creating Your 3D Models"
    subtitle="Sit back and relax while our AI works its magic ✨"
  />
  
  <Breadcrumb items={breadcrumbItems} />
  
  {#if isProcessing}
    <!-- Processing View -->
    <section class="progress-header">
      <ProgressIndicator 
        progress={overallProgress} 
        message="Processing your images..."
        size="large"
      />
    </section>
    
    <!-- Batch Info Section -->
    <section class="batch-info-section">
      <div class="container">
        <div class="batch-info-card card" use:scrollReveal>
          <div class="batch-item">
            <div class="batch-icon">
              <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 1 1 0 000 2H6a2 2 0 00-2 2v6a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-1a1 1 0 100-2h1a4 4 0 014 4v6a4 4 0 01-4 4H6a4 4 0 01-4-4V7a4 4 0 014-4z" clip-rule="evenodd"/>
              </svg>
            </div>
            <div>
              <span class="batch-label">Batch ID</span>
              <span class="batch-value">{taskId}</span>
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
            <div class="file-card" data-stagger>
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
                <span class="file-progress-text">{Math.round(file.progress)}%</span>
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
          <div class="tip-icon">{tips[currentTipIndex].icon}</div>
          <p class="tip-text">{tips[currentTipIndex].text}</p>
        </div>
      </div>
    </section>
    
    <!-- Action Buttons -->
    <section class="action-section">
      <div class="container">
        <Button 
          variant="ghost"
          on:click={cancelProcessing}
          class="hover-lift"
        >
          <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor" slot="icon">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
          Cancel Processing
        </Button>
      </div>
    </section>
  {/if}
  
  <!-- Dev Note -->
  <section class="dev-note">
    <div class="container">
      <div class="note-card">
        <Icon name="info" size={20} />
        <p>Dev Mode: Shows active processing at 55% complete. 3 files done, 1 in progress, 1 pending.</p>
        <Button href="/dev" variant="ghost" size="sm">Back to Dev Index</Button>
      </div>
    </div>
  </section>
</main>

<Footer />

<style>
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
</style>
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
  import Hero from '$lib/components/Hero.svelte';
  import ProgressIndicator from '$lib/components/ProgressIndicator.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import ModelCard from '$lib/components/ModelCard.svelte';
  import ImageGrid from '$lib/components/ImageGrid.svelte';
  import api from '$lib/services/api';

  // Check if we're in dev mode
  $: isDevMode = $page.url.searchParams.get('dev') === 'true';
  $: showResults = $page.url.searchParams.get('results') === 'true';
  $: showError = $page.url.searchParams.get('error') === 'true';
  $: edgeCase = $page.url.searchParams.get('edgeCase');
  
  // Dev mode mock data for results
  const mockCompletedFiles = [
    {
      filename: 'modern-chair-model.glb',
      name: 'modern-chair-model.glb',
      size: 2457600,
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=400&h=400&fit=crop' }
    },
    {
      filename: 'wooden-table-model.glb',
      name: 'wooden-table-model.glb',
      size: 3145728,
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop' }
    },
    {
      filename: 'minimalist-lamp-model.glb',
      name: 'minimalist-lamp-model.glb',
      size: 1572864,
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop' }
    },
    {
      filename: 'velvet-sofa-model.glb',
      name: 'velvet-sofa-model.glb',
      size: 4194304,
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop' }
    },
    {
      filename: 'office-desk-model.glb',
      name: 'office-desk-model.glb',
      size: 2097152,
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=400&h=400&fit=crop' }
    },
    {
      filename: 'bookshelf-model.glb',
      name: 'bookshelf-model.glb',
      size: 2621440,
      downloadUrl: '#',
      mimeType: 'model/gltf-binary',
      createdTime: new Date().toISOString(),
      rendered_image: { url: 'https://images.unsplash.com/photo-1594736797933-d0501ba2fe65?w=400&h=400&fit=crop' }
    }
  ];
  
  // Dev mode mock data
  const mockProcessingFiles = [
    {
      id: 'file-1',
      name: 'modern-chair-view1.jpg',
      preview: 'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=400&h=400&fit=crop',
      status: 'completed',
      progress: 100,
      message: 'Completed - 3D model generated'
    },
    {
      id: 'file-2',
      name: 'wooden-table-angle2.jpg',
      preview: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop',
      status: 'completed',
      progress: 100,
      message: 'Completed - 3D model generated'
    },
    {
      id: 'file-3',
      name: 'minimalist-lamp.jpg',
      preview: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop',
      status: 'completed',
      progress: 100,
      message: 'Completed - 3D model generated'
    },
    {
      id: 'file-4',
      name: 'velvet-sofa-front.jpg',
      preview: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop',
      status: 'processing',
      progress: 75,
      message: 'Processing - Generating texture maps...'
    },
    {
      id: 'file-5',
      name: 'office-desk-setup.jpg',
      preview: 'https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=400&h=400&fit=crop',
      status: 'pending',
      progress: 0,
      message: 'Queued - Waiting to process'
    },
    {
      id: 'file-6',
      name: 'bookshelf-walnut.jpg',
      preview: 'https://images.unsplash.com/photo-1594736797933-d0501ba2fe65?w=400&h=400&fit=crop',
      status: 'pending',
      progress: 0,
      message: 'Queued - Waiting to process'
    }
  ];
  
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
  
  // Completion state
  let isCompleted = false;
  let completedFiles = [];
  let jobId = null;
  let totalSize = 0;
  let isLoadingResults = false;

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

  // Breadcrumb items
  let breadcrumbItems = [
    { label: 'Home', href: '/' },
    { label: 'Upload', href: '/upload' },
    { label: 'Processing', current: true },
    { label: 'Results' }
  ];

  // Parse task ID from URL - support both 'taskId' and 'batch' for compatibility
  $: {
    taskId = $page.url.searchParams.get('taskId') || $page.url.searchParams.get('batch') || '';
    if (!taskId && !isDevMode && typeof window !== 'undefined') {
      toast.error('No task ID provided');
      goto('/upload');
    }
  }

  // Initialize processing
  onMount(async () => {
    // Handle dev mode
    if (isDevMode) {
      taskId = 'dev-task-123';
      jobId = 'dev-job-123';
      
      if (showError) {
        // Show error state
        isCompleted = true;
        isProcessing = false;
        completedFiles = [];
        totalFiles = 6;
        filesCompleted = 0;
        elapsedTime = 45;
        // Error will be shown in the results section
      } else if (edgeCase === 'manyFiles') {
        // Edge case: Many files
        isCompleted = true;
        isProcessing = false;
        // Generate 50 mock completed files
        completedFiles = Array.from({ length: 50 }, (_, i) => ({
          filename: `model-${i + 1}.glb`,
          name: `model-${i + 1}.glb`,
          size: Math.floor(Math.random() * 5000000) + 1000000,
          downloadUrl: '#',
          mimeType: 'model/gltf-binary',
          createdTime: new Date().toISOString(),
          rendered_image: { 
            url: `https://images.unsplash.com/photo-${1590000000000 + i * 1000000}?w=400&h=400&fit=crop` 
          }
        }));
        totalSize = completedFiles.reduce((sum, f) => sum + f.size, 0);
        filesCompleted = completedFiles.length;
        totalFiles = completedFiles.length;
        elapsedTime = 890;
      } else if (edgeCase === 'slowProcessing') {
        // Edge case: Very slow processing
        files = mockProcessingFiles.map((f, i) => ({
          ...f,
          status: i === 0 ? 'processing' : 'pending',
          progress: i === 0 ? 5 : 0,
          message: i === 0 ? 'Processing - This is taking longer than expected...' : 'Queued'
        }));
        totalFiles = files.length;
        filesCompleted = 0;
        overallProgress = 5;
        elapsedTime = 300; // 5 minutes
      } else if (edgeCase === 'largeFiles') {
        // Edge case: Very large files
        isCompleted = true;
        isProcessing = false;
        completedFiles = [
          {
            filename: 'ultra-hd-furniture-model.glb',
            name: 'ultra-hd-furniture-model.glb',
            size: 524288000, // 500MB
            downloadUrl: '#',
            mimeType: 'model/gltf-binary',
            createdTime: new Date().toISOString(),
            rendered_image: { url: 'https://images.unsplash.com/photo-1592078615290-033ee584e267?w=400&h=400&fit=crop' }
          },
          {
            filename: 'complex-architectural-model.glb',
            name: 'complex-architectural-model.glb',
            size: 1073741824, // 1GB
            downloadUrl: '#',
            mimeType: 'model/gltf-binary',
            createdTime: new Date().toISOString(),
            rendered_image: { url: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=400&h=400&fit=crop' }
          }
        ];
        totalSize = completedFiles.reduce((sum, f) => sum + f.size, 0);
        filesCompleted = completedFiles.length;
        totalFiles = completedFiles.length;
        elapsedTime = 1800; // 30 minutes
      } else if (edgeCase === 'mixedResults') {
        // Edge case: Mixed results - some succeeded, some failed
        isCompleted = true;
        isProcessing = false;
        completedFiles = mockCompletedFiles.slice(0, 3); // Only 3 succeeded
        totalSize = completedFiles.reduce((sum, f) => sum + f.size, 0);
        filesCompleted = 3;
        totalFiles = 6; // But 6 were submitted
        elapsedTime = 180;
      } else if (edgeCase === 'singleFile') {
        // Edge case: Single file
        isCompleted = true;
        isProcessing = false;
        completedFiles = [mockCompletedFiles[0]];
        totalSize = completedFiles[0].size;
        filesCompleted = 1;
        totalFiles = 1;
        elapsedTime = 45;
      } else if (showResults) {
        // Show results view
        isCompleted = true;
        isProcessing = false;
        completedFiles = mockCompletedFiles;
        totalSize = mockCompletedFiles.reduce((sum, f) => sum + f.size, 0);
        filesCompleted = mockCompletedFiles.length;
        totalFiles = mockCompletedFiles.length;
        elapsedTime = 125;
      } else {
        // Show processing view
        files = mockProcessingFiles;
        totalFiles = mockProcessingFiles.length;
        filesCompleted = 3;
        overallProgress = 55;
        elapsedTime = 45;
        
        // Simulate progress updates
        const progressInterval = setInterval(() => {
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
        
        return () => clearInterval(progressInterval);
      }
      
      return;
    }
    
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

    const stream = api.createProgressStream(taskId, {
      onProgress: handleProgressUpdate,
      onComplete: handleCompletion,
      onError: (error) => {
        isProcessing = false;
        toast.error(`Processing failed: ${error}`);
      },
      onFileUpdate: (data) => {
        // Handle individual file updates if needed
        console.log('File update:', data);
      }
    });

    eventSource = stream.eventSource;
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
  async function handleCompletion(data) {
    isProcessing = false;
    isCompleted = true;
    jobId = data.result?.job_id || data.job_id || taskId;
    
    if (eventSource) {
      eventSource.close();
    }
    
    // Update breadcrumb to show we're on results
    breadcrumbItems = breadcrumbItems.map((item, index) => ({
      ...item,
      current: index === 3 // Results is the 4th item (0-indexed)
    }));
    
    toast.success('Processing complete! Loading your models...');
    
    // Fetch the completed files
    await fetchCompletedFiles();
  }
  
  // New function to fetch completed files
  async function fetchCompletedFiles() {
    isLoadingResults = true;
    
    try {
      const response = await api.getJobFiles(jobId);
      
      if (response.success) {
        completedFiles = response.files;
        totalSize = response.files.reduce((sum, f) => sum + (f.size || 0), 0);
        
        // Update files array to show completion
        files = files.map((file) => ({
          ...file,
          status: 'completed',
          progress: 100,
          message: 'Completed'
        }));
      } else {
        toast.error('Failed to load completed files');
      }
    } catch (error) {
      console.error('Error fetching completed files:', error);
      toast.error('Error loading results');
    } finally {
      isLoadingResults = false;
    }
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
  
  // Download all files
  async function downloadAll() {
    const downloadBtn = document.querySelector('#downloadAllBtn');
    if (downloadBtn) downloadBtn.disabled = true;
    
    let downloadCount = 0;
    
    // Download each file sequentially
    for (const file of completedFiles) {
      try {
        const link = document.createElement('a');
        
        if (api.isExternalUrl(file.downloadUrl)) {
          link.href = file.downloadUrl;
          link.target = '_blank';
          link.rel = 'noopener noreferrer';
        } else {
          link.href = file.downloadUrl || api.getDownloadUrl(jobId, file.filename);
          link.download = file.filename;
        }
        
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        downloadCount++;
        
        // Small delay between downloads to prevent browser blocking
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (error) {
        console.error(`Failed to download ${file.filename}:`, error);
      }
    }
    
    if (downloadBtn) downloadBtn.disabled = false;
    
    // Show completion message
    if (downloadCount === completedFiles.length) {
      toast.success('All files downloaded successfully!');
    } else {
      toast.warning(`Downloaded ${downloadCount} of ${completedFiles.length} files.`);
    }
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
<Hero 
  title={showError ? "Processing Failed" : (isCompleted ? "Success!" : "Processing Your Images")} 
  subtitle={showError ? "We encountered an error while processing your images" : (isCompleted ? "Your 3D models are ready for download" : "Your 3D models are being generated")}
>
  <div slot="content" class="animate-fade-in-scale delay-400" use:scrollReveal>
    {#if isCompleted && !showError}
      <div class="success-icon animate-bounce-in">
        <Icon name="check-circle" size={80} color="white" />
      </div>
    {:else if showError}
      <div class="error-icon animate-bounce-in">
        <Icon name="x-circle" size={80} color="white" />
      </div>
    {/if}
    <ProgressIndicator currentStep={isCompleted ? 3 : 2} />
  </div>
</Hero>

<!-- Main Content -->
<main>
  {#if !isCompleted}
    <!-- Processing View -->
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
      <ImageGrid 
        items={files.map(f => ({ 
          ...f, 
          statusText: f.status === 'processing' ? `${f.progress}%` : f.status
        }))} 
        showOverlay={true}
        gridSize="medium"
      />
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
  
  {:else}
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
              <span class="summary-value">{completedFiles.length}{#if edgeCase === 'mixedResults'} of {totalFiles}{/if}</span>
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
    {#if !showError && completedFiles.length > 0}
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
    {/if}
    
    <!-- Models Grid -->
    <section class="models-grid-section">
      <div class="container">
        <h2>Your 3D Models</h2>
        {#if isLoadingResults}
          <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading your models...</p>
          </div>
        {:else if showError}
          <div class="empty-state error">
            <Icon name="x-circle" size={64} color="#ef4444" />
            <h3>Processing Failed</h3>
            <p>Unable to generate 3D models from your images.</p>
            <Button href="/upload" variant="primary">Upload New Images</Button>
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
    {#if !showError && completedFiles.length > 0}
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
    {/if}
  {/if}
</main>

<Footer />

<style>
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

  :global(.hero p) {
    color: white !important;
  }

  /* Breadcrumb section */
  .breadcrumb-section {
    background-color: #f8f9fa;
    padding: 1rem 0;
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
    max-width: 800px;
    margin: 0 auto;
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

  /* Success Icon Animation */
  .success-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto 1.5rem;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  @keyframes bounceIn {
    0% {
      opacity: 0;
      transform: scale(0.3);
    }
    50% {
      transform: scale(1.05);
    }
    70% {
      transform: scale(0.9);
    }
    100% {
      opacity: 1;
      transform: scale(1);
    }
  }

  :global(.animate-bounce-in) {
    animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  }

  /* Summary Section */
  .summary-section {
    background-color: #f8f9fa;
    padding: 3rem 0;
  }

  .summary-card {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    padding: 2rem;
  }

  .summary-item {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .summary-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .summary-label {
    display: block;
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 0.25rem;
  }

  .summary-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
  }

  /* Download Actions */
  .download-actions {
    background-color: #f8f9fa;
    text-align: center;
    padding: 0 0 3rem;
  }

  :global(.badge) {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.25rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    margin-left: 0.5rem;
  }

  /* Models Grid */
  .models-grid-section {
    background-color: #f8f9fa;
    padding: 0 0 3rem;
  }

  .models-grid-section h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 2rem;
  }

  .model-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  /* Loading & Empty States */
  .loading-state,
  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }

  .spinner {
    width: 48px;
    height: 48px;
    border: 3px solid #e2e8f0;
    border-top-color: #3498db;
    border-radius: 50%;
    margin: 0 auto 1rem;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .empty-state h3 {
    font-size: 1.25rem;
    color: #1e293b;
    margin: 1rem 0;
  }

  .empty-state.error h3 {
    color: #dc2626;
  }

  .empty-state p {
    color: #64748b;
    margin-bottom: 2rem;
  }

  /* What's Next Section */
  .whats-next-section {
    background-color: #f8f9fa;
    padding: 0 0 4rem;
  }

  .whats-next-section h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
    text-align: center;
    margin-bottom: 3rem;
  }

  .next-steps-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
  }

  .next-step-card {
    padding: 2rem;
    text-align: center;
    background: white;
    border-radius: 12px;
    transition: all 0.2s;
  }

  .next-step-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  }

  .step-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 1.5rem;
    background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .next-step-card h3 {
    font-size: 1.25rem;
    color: #1e293b;
    margin-bottom: 1rem;
  }

  .next-step-card p {
    color: #64748b;
    line-height: 1.6;
    margin-bottom: 1.5rem;
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
    
    .summary-card {
      grid-template-columns: 1fr;
      gap: 1rem;
    }
    
    .model-grid {
      grid-template-columns: 1fr;
    }
    
    .next-steps-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
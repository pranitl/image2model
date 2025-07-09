<script>
  import { createEventDispatcher } from 'svelte';
  import Icon from './Icon.svelte';
  import Button from './Button.svelte';
  import api from '$lib/services/api';
  
  /**
   * @type {Object} file - File object with model information
   * @type {string} file.filename - Name of the file
   * @type {number} file.size - Size in bytes
   * @type {string} file.downloadUrl - URL for downloading
   * @type {string} file.mimeType - MIME type of the file
   * @type {Object} file.rendered_image - Preview image object
   */
  export let file;
  
  /**
   * @type {string} jobId - Job ID for the model
   */
  export let jobId;
  
  /**
   * @type {Function} onDownload - Callback when download is clicked
   */
  export let onDownload = null;
  
  /**
   * @type {Function} onPreview - Callback when preview is clicked
   */
  export let onPreview = null;
  
  const dispatch = createEventDispatcher();
  
  // Determine if URL is external (FAL.AI)
  $: isExternalUrl = api.isExternalUrl(file.downloadUrl);
  
  // Extract file format from filename
  $: fileFormat = (() => {
    if (!file.filename) return '3D';
    const ext = file.filename.split('.').pop().toUpperCase();
    return ['GLB', 'OBJ', 'STL'].includes(ext) ? ext : '3D';
  })();
  
  // Format file size
  $: formattedSize = api.formatFileSize(file.size || 0);
  
  // Handle image loading error
  let imageError = false;
  
  function handleImageError() {
    imageError = true;
  }
  
  function handleDownloadClick(e) {
    if (onDownload) {
      e.preventDefault();
      onDownload(file);
    }
    dispatch('download', file);
  }
  
  function handlePreviewClick() {
    if (onPreview) {
      onPreview(file);
    }
    dispatch('preview', file);
  }
</script>

<div class="model-card card hover-lift">
  <!-- Preview Section -->
  <div class="model-preview">
    {#if file.rendered_image?.url && !imageError}
      <img 
        src={file.rendered_image.url} 
        alt="Preview of {file.filename}"
        loading="lazy"
        on:error={handleImageError}
        class="model-thumbnail"
      />
    {:else}
      <div class="model-preview-placeholder">
        <Icon name="cube" size={48} color="#94a3b8" />
        <span>3D Model</span>
      </div>
    {/if}
    <span class="model-format">{fileFormat}</span>
  </div>
  
  <!-- Info Section -->
  <div class="model-info">
    <h3 class="model-name" title={file.filename}>{file.filename || 'Unnamed Model'}</h3>
    <div class="model-details">
      <span class="model-size">{formattedSize}</span>
    </div>
    
    <!-- Actions -->
    <div class="model-actions">
      {#if isExternalUrl}
        <a 
          href={file.downloadUrl}
          target="_blank"
          rel="noopener noreferrer"
          class="btn btn-primary btn-sm"
          aria-label="Download {file.filename}"
          on:click={handleDownloadClick}
        >
          <Icon name="download" size={16} />
          Download
        </a>
      {:else}
        <a 
          href={file.downloadUrl || api.getDownloadUrl(jobId, file.filename)}
          download={file.filename}
          class="btn btn-primary btn-sm"
          aria-label="Download {file.filename}"
          on:click={handleDownloadClick}
        >
          <Icon name="download" size={16} />
          Download
        </a>
      {/if}
      
      <Button 
        variant="ghost"
        size="sm"
        on:click={handlePreviewClick}
        aria-label="Preview {file.filename}"
      >
        <Icon name="eye" size={16} />
        Preview
      </Button>
    </div>
  </div>
</div>

<style>
  .model-card {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.2s ease;
  }
  
  .model-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
    border-color: #3498db;
  }
  
  /* Preview Section */
  .model-preview {
    width: 100%;
    height: 200px;
    background: #f8f9fa;
    position: relative;
    overflow: hidden;
  }
  
  .model-thumbnail {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .model-preview-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    gap: 0.5rem;
  }
  
  .model-preview-placeholder span {
    font-size: 0.875rem;
    font-weight: 500;
  }
  
  .model-format {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: #3498db;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  /* Info Section */
  .model-info {
    padding: 1.25rem;
  }
  
  .model-name {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0 0 0.5rem 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .model-details {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }
  
  .model-size {
    font-size: 0.875rem;
    color: #64748b;
  }
  
  /* Actions */
  .model-actions {
    display: flex;
    gap: 0.5rem;
  }
  
  .model-actions :global(.btn) {
    flex: 1;
    justify-content: center;
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
  }
  
  .model-actions :global(a.btn) {
    text-decoration: none;
  }
  
  /* Hover lift effect */
  :global(.hover-lift) {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  :global(.hover-lift:hover) {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  }
  
  /* Responsive */
  @media (max-width: 480px) {
    .model-preview {
      height: 150px;
    }
    
    .model-actions {
      flex-direction: column;
    }
    
    .model-actions :global(.btn) {
      width: 100%;
    }
  }
</style>
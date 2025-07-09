// Centralized API service for the Svelte app
// Consolidates all API calls from upload, processing, and results functionality

class APIService {
  constructor(apiKey = null) {
    // API base URL - dynamically set based on current origin
    this.API_BASE = typeof window !== 'undefined' 
      ? `${window.location.origin}/api/v1`
      : '/api/v1';
    
    // Default timeout for requests
    this.DEFAULT_TIMEOUT = 60000; // 60 seconds
    
    // API key from environment variables
    this.API_KEY = apiKey;
    
    // Debug logging in development
    if (import.meta.env.MODE === 'development') {
      console.log('API Service initialized with key:', this.API_KEY ? `${this.API_KEY.substring(0, 10)}...` : 'NOT SET');
    }
  }

  // Set API key after initialization
  setApiKey(apiKey) {
    this.API_KEY = apiKey;
    if (import.meta.env.MODE === 'development') {
      console.log('API key updated:', this.API_KEY ? `${this.API_KEY.substring(0, 10)}...` : 'NOT SET');
    }
  }

  // Helper method to get common headers
  getHeaders(additionalHeaders = {}) {
    return {
      'Authorization': `Bearer ${this.API_KEY}`,
      ...additionalHeaders
    };
  }

  // Helper method for handling API errors
  async handleApiError(response) {
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
        console.error('API Error Response:', errorData);
      } catch (e) {
        errorData = { message: `HTTP ${response.status}: ${response.statusText}` };
      }
      throw new Error(errorData.detail || errorData.message || errorData.error || `Request failed: ${response.statusText}`);
    }
    return response;
  }

  // Upload batch of files with face limit
  async uploadBatch(files, faceLimit = null) {
    const formData = new FormData();
    
    // Add files to form data
    files.forEach((fileObj) => {
      // Handle both File objects and our wrapped file objects
      const file = fileObj.file || fileObj;
      console.log('Adding file:', file.name, 'Type:', file.type, 'Size:', file.size);
      formData.append('files', file);
    });
    
    // Add face limit parameter (backend expects a number, not a string)
    if (faceLimit !== null && faceLimit !== undefined && faceLimit !== 'auto') {
      console.log('Adding face_limit:', faceLimit, 'Type:', typeof faceLimit);
      formData.append('face_limit', faceLimit);
    } else {
      console.log('Not sending face_limit, value is:', faceLimit);
    }
    // If faceLimit is 'auto' or not provided, don't send it (backend will use default)
    
    try {
      const headers = this.getHeaders();
      console.log('Upload headers:', headers);
      console.log('Upload URL:', `${this.API_BASE}/upload/`);
      
      const response = await fetch(`${this.API_BASE}/upload/`, {
        method: 'POST',
        body: formData,
        headers: headers,
        signal: AbortSignal.timeout(this.DEFAULT_TIMEOUT)
      });
      
      await this.handleApiError(response);
      const data = await response.json();
      
      console.log('API Response:', data);
      
      return {
        success: true,
        batchId: data.batch_id || data.job_id,
        taskId: data.task_id || data.job_id, // Use task_id if available, otherwise job_id
        jobId: data.job_id,
        fileCount: data.total_files || files.length
      };
    } catch (error) {
      console.error('Upload failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Alternative upload endpoint (from original API)
  async uploadFiles(files, faceLimit = 5000) {
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    formData.append('face_limit', faceLimit.toString());
    
    try {
      const response = await fetch(`${this.API_BASE}/upload/`, {
        method: 'POST',
        body: formData,
        headers: this.getHeaders()
      });
      
      await this.handleApiError(response);
      const data = await response.json();
      
      return {
        success: true,
        jobId: data.job_id,
        taskId: data.task_id,
        fileCount: data.total_files || files.length
      };
    } catch (error) {
      console.error('Upload failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Create Server-Sent Events connection for progress updates
  createProgressStream(taskId, callbacks = {}) {
    const {
      onProgress = () => {},
      onFileUpdate = () => {},
      onComplete = () => {},
      onError = () => {},
      onTaskUpdate = () => {}
    } = callbacks;
    
    // Note: EventSource doesn't support custom headers, so auth may need to be handled differently
    const eventSource = new EventSource(`${this.API_BASE}/status/tasks/${taskId}/stream`);
    
    // Handle specific event types
    eventSource.addEventListener('task_progress', (event) => {
      const data = JSON.parse(event.data);
      onProgress(data);
      onTaskUpdate('progress', data);
    });
    
    eventSource.addEventListener('task_completed', (event) => {
      const data = JSON.parse(event.data);
      onComplete(data);
      onTaskUpdate('completed', data);
      eventSource.close();
    });
    
    eventSource.addEventListener('task_failed', (event) => {
      const data = JSON.parse(event.data);
      onError(data.error || 'Processing failed');
      onTaskUpdate('failed', data);
      eventSource.close();
    });
    
    eventSource.addEventListener('file_update', (event) => {
      const data = JSON.parse(event.data);
      onFileUpdate(data);
    });
    
    // Handle connection errors
    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      if (eventSource.readyState === EventSource.CLOSED) {
        onError('Connection lost');
      }
    };
    
    // Return control object
    return {
      close: () => eventSource.close(),
      readyState: () => eventSource.readyState,
      eventSource
    };
  }

  // Get list of processed files for a job
  async getJobFiles(jobId) {
    try {
      const response = await fetch(`${this.API_BASE}/download/${jobId}/all`, {
        headers: this.getHeaders()
      });
      await this.handleApiError(response);
      const data = await response.json();
      
      // Transform the response to a consistent format
      return {
        success: true,
        files: (data.files || []).map((file, index) => ({
          filename: file.filename,
          name: file.filename, // Alias for compatibility
          size: file.size || 0,
          downloadUrl: data.download_urls?.[index],
          mimeType: file.mime_type,
          mime_type: file.mime_type, // Alias for compatibility
          createdTime: file.created_time,
          rendered_image: file.rendered_image || null // FAL.AI preview image
        })),
        totalFiles: data.total_files || data.files?.length || 0,
        jobId: data.job_id || jobId
      };
    } catch (error) {
      console.error('Failed to fetch job files:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Get job status (non-streaming)
  async getJobStatus(taskId) {
    try {
      const response = await fetch(`${this.API_BASE}/status/tasks/${taskId}`, {
        headers: this.getHeaders()
      });
      await this.handleApiError(response);
      const data = await response.json();
      return { success: true, ...data };
    } catch (error) {
      console.error('Failed to get job status:', error);
      return { success: false, error: error.message };
    }
  }

  // Download a single file
  getDownloadUrl(jobId, filename) {
    // Note: Downloads via direct URL may need auth token in query params
    return `${this.API_BASE}/download/${jobId}/${encodeURIComponent(filename)}`;
  }

  // Get download all URL
  getDownloadAllUrl(jobId) {
    // Note: Downloads via direct URL may need auth token in query params
    return `${this.API_BASE}/download/${jobId}/all`;
  }

  // Check if a URL is from FAL.AI (external)
  isExternalUrl(url) {
    if (!url) return false;
    return url.includes('fal.ai') || url.includes('fal.media') || url.includes('fal.run');
  }

  // Format file size for display
  formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Retry helper for resilient API calls
  async retryOperation(operation, maxRetries = 3, backoffMs = 1000) {
    let lastError;
    
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        console.error(`Attempt ${attempt + 1} failed:`, error);
        
        if (attempt < maxRetries - 1) {
          // Exponential backoff
          await new Promise(resolve => 
            setTimeout(resolve, backoffMs * Math.pow(2, attempt))
          );
        }
      }
    }
    
    throw lastError;
  }
}

// Create singleton instance
const api = new APIService();

// Export for use in Svelte components
export default api;

// Also export class for testing or alternative instances
export { APIService };
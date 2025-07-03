// Comprehensive API client for AI 3D Model Generator
(function() {
    'use strict';
    
    // API Configuration - dynamically set based on current origin
    const API_BASE = window.location.origin + '/api/v1';
    
    // Helper function for handling API errors
    async function handleApiError(response) {
        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { message: 'Unknown error occurred' };
            }
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        return response;
    }
    
    // Upload batch of files with face limit
    async function uploadBatch(files, faceLimit = 5000) {
        const formData = new FormData();
        
        // Add files to form data
        files.forEach((file) => {
            formData.append('files', file);
        });
        
        // Add face limit parameter
        formData.append('face_limit', faceLimit.toString());
        
        try {
            const response = await fetch(`${API_BASE}/upload/batch`, {
                method: 'POST',
                body: formData
                // Don't set Content-Type header - browser will set it with boundary
            });
            
            await handleApiError(response);
            const data = await response.json();
            
            return {
                success: true,
                jobId: data.job_id,
                taskId: data.task_id,
                fileCount: data.file_count || files.length
            };
        } catch (error) {
            console.error('Upload failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    // Stream progress updates using Server-Sent Events
    function streamProgress(taskId, callbacks = {}) {
        const {
            onProgress = () => {},
            onFileUpdate = () => {},
            onComplete = () => {},
            onError = () => {}
        } = callbacks;
        
        const eventSource = new EventSource(`${API_BASE}/status/tasks/${taskId}/stream`);
        
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                // Handle different event types based on data structure
                if (data.status === 'completed' && data.job_id) {
                    onComplete({
                        jobId: data.job_id,
                        successCount: data.success_count || 0,
                        failureCount: data.failure_count || 0
                    });
                    eventSource.close();
                } else if (data.status === 'failed') {
                    onError(new Error(data.error || 'Processing failed'));
                    eventSource.close();
                } else if (data.progress !== undefined) {
                    // Overall progress update
                    onProgress({
                        overall: data.progress,
                        currentFile: data.current_file,
                        status: data.status,
                        totalFiles: data.total_files,
                        files: data.files
                    });
                } else if (data.file_name) {
                    // Individual file update
                    onFileUpdate({
                        fileName: data.file_name,
                        status: data.status,
                        progress: data.progress,
                        error: data.error
                    });
                }
            } catch (error) {
                console.error('Error parsing SSE data:', error);
            }
        };
        
        eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
            onError(error);
            
            // Auto-reconnect is handled by EventSource, but we can close if needed
            if (eventSource.readyState === EventSource.CLOSED) {
                console.log('SSE connection closed');
            }
        };
        
        // Return control object
        return {
            close: () => eventSource.close(),
            readyState: () => eventSource.readyState
        };
    }
    
    // Get list of processed files for a job
    async function getJobFiles(jobId) {
        try {
            // First try the documented endpoint
            let response = await fetch(`${API_BASE}/jobs/${jobId}/files`);
            
            // If that fails, try the alternative endpoint
            if (!response.ok && response.status === 404) {
                response = await fetch(`${API_BASE}/download/${jobId}/all`);
            }
            
            await handleApiError(response);
            const data = await response.json();
            
            // Handle different response formats
            let files = data.files || data.models || [];
            
            return {
                success: true,
                files: files.map(file => ({
                    name: file.name || file.filename,
                    size: file.size || 0,
                    downloadUrl: file.download_url || `${API_BASE}/download/${jobId}/${file.name || file.filename}`,
                    thumbnailUrl: file.thumbnail_url || file.preview_url || null
                })),
                downloadAllUrl: `${API_BASE}/download/${jobId}/all`
            };
        } catch (error) {
            console.error('Failed to fetch job files:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    // Cancel a processing job
    async function cancelJob(taskId) {
        try {
            const response = await fetch(`${API_BASE}/tasks/${taskId}/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            await handleApiError(response);
            return { success: true };
        } catch (error) {
            console.error('Failed to cancel job:', error);
            return { success: false, error: error.message };
        }
    }
    
    // Check job status (non-streaming)
    async function getJobStatus(taskId) {
        try {
            const response = await fetch(`${API_BASE}/status/tasks/${taskId}`);
            await handleApiError(response);
            const data = await response.json();
            return { success: true, ...data };
        } catch (error) {
            console.error('Failed to get job status:', error);
            return { success: false, error: error.message };
        }
    }
    
    // Export API module as global object and maintain compatibility
    const API = {
        uploadBatch,
        streamProgress,
        getJobFiles,
        cancelJob,
        getJobStatus,
        API_BASE
    };
    
    // Export as window.API for vanilla JS usage
    window.API = API;
    
    // Also maintain backward compatibility with lowercase api
    window.api = {
        uploadBatch: API.uploadBatch,
        streamProgress: (taskId, onUpdate) => {
            // Adapter for old interface
            return API.streamProgress(taskId, {
                onProgress: onUpdate
            });
        },
        getJobFiles: API.getJobFiles
    };
    
})();
// Comprehensive API client for AI 3D Model Generator
(function() {
    'use strict';
    
    // API Configuration - dynamically set based on current origin
    const API_BASE = window.location.origin + '/api/v1';
    
    // API Key configuration - can be set via localStorage or environment
    // In development, use default key if none is set
    const DEFAULT_DEV_KEY = 'dev-api-key-123456';
    const API_KEY = localStorage.getItem('api_key') || window.API_KEY || 
                   (window.location.hostname === 'localhost' ? DEFAULT_DEV_KEY : '');
    
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
    
    // Helper function to get request headers
    function getHeaders(additionalHeaders = {}) {
        const headers = {};
        if (API_KEY) {
            headers['Authorization'] = `Bearer ${API_KEY}`;
        }
        return { ...headers, ...additionalHeaders };
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
            const response = await fetch(`${API_BASE}/upload/`, {
                method: 'POST',
                headers: getHeaders(),
                body: formData
                // Don't set Content-Type header - browser will set it with boundary
            });
            
            await handleApiError(response);
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
    
    // Stream progress updates using Server-Sent Events
    function streamProgress(taskId, callbacks = {}) {
        const {
            onProgress = () => {},
            onFileUpdate = () => {},
            onComplete = () => {},
            onError = () => {}
        } = callbacks;
        
        // Create EventSource with auth headers if API key is present
        const url = `${API_BASE}/status/tasks/${taskId}/stream`;
        const eventSourceInit = API_KEY ? {
            headers: {
                'Authorization': `Bearer ${API_KEY}`
            }
        } : undefined;
        
        const eventSource = new EventSource(url, eventSourceInit);
        
        // Helper function to parse and handle event data
        const handleEventData = (event, eventType) => {
            try {
                const data = JSON.parse(event.data);
                
                // Handle different event types
                switch (eventType) {
                    case 'task_completed':
                        // Task completed successfully
                        if (data.result && data.result.job_id) {
                            onComplete({
                                jobId: data.result.job_id,
                                successCount: data.result.successful_files || 0,
                                failureCount: data.result.failed_files || 0
                            });
                        } else {
                            onComplete({
                                jobId: data.job_id || taskId,
                                successCount: data.summary?.successful_files || 0,
                                failureCount: data.summary?.failed_files || 0
                            });
                        }
                        eventSource.close();
                        break;
                        
                    case 'task_failed':
                        onError(new Error(data.error || 'Processing failed'));
                        eventSource.close();
                        break;
                        
                    case 'task_progress':
                    case 'task_queued':
                    case 'task_status':
                        // Overall progress update
                        onProgress({
                            overall: data.progress || data.overall || 0,
                            currentFile: data.current_file,
                            status: data.status,
                            totalFiles: data.total || data.total_files,
                            files: data.files,
                            current: data.current,
                            total: data.total
                        });
                        break;
                        
                    case 'file_update':
                        // Individual file update
                        onFileUpdate({
                            fileName: data.file_name || data.filename,
                            status: data.status,
                            progress: data.progress,
                            error: data.error
                        });
                        break;
                        
                    default:
                        // Handle generic message events
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
                            onProgress({
                                overall: data.progress,
                                currentFile: data.current_file,
                                status: data.status,
                                totalFiles: data.total_files,
                                files: data.files
                            });
                        } else if (data.file_name) {
                            onFileUpdate({
                                fileName: data.file_name,
                                status: data.status,
                                progress: data.progress,
                                error: data.error
                            });
                        }
                }
            } catch (error) {
                console.error('Error parsing SSE data:', error);
            }
        };
        
        // Add specific event listeners for named events
        eventSource.addEventListener('task_completed', (event) => handleEventData(event, 'task_completed'));
        eventSource.addEventListener('task_failed', (event) => handleEventData(event, 'task_failed'));
        eventSource.addEventListener('task_progress', (event) => handleEventData(event, 'task_progress'));
        eventSource.addEventListener('task_queued', (event) => handleEventData(event, 'task_queued'));
        eventSource.addEventListener('task_retry', (event) => handleEventData(event, 'task_retry'));
        eventSource.addEventListener('task_cancelled', (event) => handleEventData(event, 'task_cancelled'));
        eventSource.addEventListener('task_status', (event) => handleEventData(event, 'task_status'));
        eventSource.addEventListener('task_error', (event) => handleEventData(event, 'task_error'));
        eventSource.addEventListener('stream_error', (event) => handleEventData(event, 'stream_error'));
        eventSource.addEventListener('connection_timeout', (event) => handleEventData(event, 'connection_timeout'));
        eventSource.addEventListener('heartbeat', (event) => handleEventData(event, 'heartbeat'));
        
        // Also keep the generic message handler for backward compatibility
        eventSource.onmessage = (event) => handleEventData(event, 'generic');
        
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
            // Use the correct endpoint from OpenAPI schema
            const response = await fetch(`${API_BASE}/download/${jobId}/all`, {
                headers: getHeaders()
            });
            
            await handleApiError(response);
            const data = await response.json();
            
            // According to schema, response is JobFilesResponse with:
            // job_id, files[], download_urls[], total_files
            // Each file has: filename, size, mime_type, created_time
            
            return {
                success: true,
                files: (data.files || []).map((file, index) => ({
                    filename: file.filename,  // Changed from 'name' to 'filename' to match results.js
                    size: file.size || 0,
                    downloadUrl: data.download_urls?.[index] || `${API_BASE}/download/${jobId}/${file.filename}`,
                    thumbnailUrl: null, // Not provided in schema
                    mimeType: file.mime_type,
                    mime_type: file.mime_type, // Add both for compatibility
                    createdTime: file.created_time,
                    rendered_image: file.rendered_image || null  // Add rendered_image from FAL.AI
                })),
                downloadAllUrl: `${API_BASE}/download/${jobId}/all`,
                totalFiles: data.total_files
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
    // NOTE: Cancel endpoint not available in current API
    async function cancelJob(taskId) {
        console.warn('Cancel endpoint not available in current API');
        // For now, just close the SSE connection on client side
        return { 
            success: false, 
            error: 'Cancel functionality not available in current API version' 
        };
    }
    
    // Check job status (non-streaming)
    async function getJobStatus(taskId) {
        try {
            const response = await fetch(`${API_BASE}/status/tasks/${taskId}`, {
                headers: getHeaders()
            });
            await handleApiError(response);
            const data = await response.json();
            return { success: true, ...data };
        } catch (error) {
            console.error('Failed to get job status:', error);
            return { success: false, error: error.message };
        }
    }
    
    // Function to set API key programmatically
    function setApiKey(key) {
        if (key) {
            localStorage.setItem('api_key', key);
            // Reload page to apply new key
            window.location.reload();
        }
    }
    
    // Function to get current API key
    function getApiKey() {
        return API_KEY;
    }
    
    // Export API module as global object and maintain compatibility
    const API = {
        uploadBatch,
        streamProgress,
        getJobFiles,
        cancelJob,
        getJobStatus,
        API_BASE,
        setApiKey,
        getApiKey
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
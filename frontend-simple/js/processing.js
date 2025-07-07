// Enhanced Processing Module with SSE and real-time updates
const ProcessingModule = (function() {
    'use strict';
    
    // State management
    const state = {
        taskId: null,
        jobId: null,  // Add jobId to state
        eventSource: null,
        streamController: null,
        files: new Map(), // Map of filename -> file status
        overallProgress: 0,
        isComplete: false,
        isCancelled: false,
        reconnectAttempts: 0,
        maxReconnectAttempts: 5,
        reconnectDelay: 1000, // Start with 1 second
        startTime: new Date(),
        elapsedInterval: null
    };
    
    // DOM element references
    let elements = {};
    
    // Initialize on DOM ready
    function init() {
        // Extract task_id and job_id from URL
        const urlParams = new URLSearchParams(window.location.search);
        state.taskId = urlParams.get('taskId') || urlParams.get('task_id');
        state.jobId = urlParams.get('jobId') || urlParams.get('job_id');
        
        if (!state.taskId) {
            showError('No task ID provided');
            setTimeout(() => window.location.href = 'upload.html', 3000);
            return;
        }
        
        // Cache DOM elements
        cacheElements();
        
        // Set initial UI
        initializeUI();
        
        // Setup event listeners
        setupEventListeners();
        
        // Start elapsed timer
        startElapsedTimer();
        
        // Setup mobile navigation
        setupMobileNavigation();
        
        // Setup tips carousel
        setupTipsCarousel();
        
        // Setup view toggle
        setupViewToggle();
        
        // Establish SSE connection
        connectSSE();
    }
    
    // Cache all DOM elements
    function cacheElements() {
        elements = {
            taskId: document.getElementById('taskId'),
            fileCount: document.getElementById('fileCount'),
            startTime: document.getElementById('startTime'),
            elapsedTime: document.getElementById('elapsedTime'),
            progressFill: document.getElementById('progressFill'),
            progressText: document.querySelector('#progressFill .progress-text'),
            filesCompleted: document.getElementById('filesCompleted'),
            totalFiles: document.getElementById('totalFiles'),
            fileGrid: document.getElementById('fileGrid'),
            cancelBtn: document.getElementById('cancelBtn'),
            statusMessage: document.getElementById('statusMessage')
        };
    }
    
    // Initialize UI with default values
    function initializeUI() {
        if (elements.taskId) {
            elements.taskId.textContent = state.taskId;
        }
        if (elements.startTime) {
            elements.startTime.textContent = state.startTime.toLocaleTimeString();
        }
        if (elements.fileCount) {
            elements.fileCount.textContent = '0';
        }
        if (elements.totalFiles) {
            elements.totalFiles.textContent = '0';
        }
        if (elements.filesCompleted) {
            elements.filesCompleted.textContent = '0';
        }
    }
    
    // Setup event listeners
    function setupEventListeners() {
        if (elements.cancelBtn) {
            elements.cancelBtn.addEventListener('click', handleCancel);
        }
        
        // Handle page unload
        window.addEventListener('beforeunload', cleanup);
    }
    
    // Start elapsed time counter
    function startElapsedTimer() {
        state.elapsedInterval = setInterval(() => {
            const elapsed = Math.floor((new Date() - state.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            if (elements.elapsedTime) {
                elements.elapsedTime.textContent = 
                    minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
            }
        }, 1000);
    }
    
    // Establish SSE connection
    function connectSSE() {
        try {
            
            // Use API client's streamProgress function with callbacks
            state.streamController = window.API.streamProgress(state.taskId, {
                onProgress: handleProgressUpdate,
                onFileUpdate: handleFileUpdate,
                onComplete: handleComplete,
                onError: handleError
            });
            
            // Set reconnect attempts to 0 on successful connection
            state.reconnectAttempts = 0;
            state.reconnectDelay = 1000;
            
        } catch (error) {
            console.error('Failed to establish SSE connection:', error);
            handleConnectionError();
        }
    }
    
    // Handle connection errors with exponential backoff
    function handleConnectionError() {
        // Close existing connection
        if (state.streamController && state.streamController.close) {
            state.streamController.close();
            state.streamController = null;
        }
        
        // Check if we should reconnect
        if (state.reconnectAttempts < state.maxReconnectAttempts && 
            !state.isComplete && !state.isCancelled) {
            
            state.reconnectAttempts++;
            
            // Show reconnection status
            showStatus(`Connection lost. Reconnecting... (${state.reconnectAttempts}/${state.maxReconnectAttempts})`);
            
            // Exponential backoff
            setTimeout(() => {
                connectSSE();
            }, state.reconnectDelay);
            
            // Increase delay for next attempt
            state.reconnectDelay = Math.min(state.reconnectDelay * 2, 30000); // Max 30 seconds
        } else {
            showError('Connection lost. Please refresh the page.');
        }
    }
    
    // Handle overall progress updates
    function handleProgressUpdate(data) {
        
        // Update file counts
        if (data.totalFiles !== undefined) {
            if (elements.fileCount) elements.fileCount.textContent = data.totalFiles;
            if (elements.totalFiles) elements.totalFiles.textContent = data.totalFiles;
        }
        
        // Update current/total from backend progress
        if (data.current !== undefined && data.total !== undefined) {
            if (elements.filesCompleted) elements.filesCompleted.textContent = data.current;
            if (elements.totalFiles) elements.totalFiles.textContent = data.total;
        }
        
        // Initialize file grid if we have files
        if (data.files && Array.isArray(data.files)) {
            updateFileGrid(data.files);
            updateCompletedCount();
        }
        
        // Calculate and update overall progress based on individual file progress
        updateOverallProgressFromFiles();
    }
    
    // Handle individual file updates
    function handleFileUpdate(data) {
        
        if (data.fileName) {
            updateFileCard(
                data.fileName, 
                data.status, 
                data.error || formatStatus(data.status),
                data.progress
            );
        }
    }
    
    // Handle completion
    function handleComplete(data) {
        state.isComplete = true;
        
        // Close SSE connection
        cleanup();
        
        // Check if there were any successful files
        const hasSuccess = data.successCount && data.successCount > 0;
        const hasFailures = data.failureCount && data.failureCount > 0;
        
        // Update UI based on results
        updateOverallProgress(100);
        
        if (!hasSuccess && hasFailures) {
            // All files failed
            showError('All files failed to process. Please check the error messages.');
            if (elements.cancelBtn) {
                elements.cancelBtn.disabled = false;
                elements.cancelBtn.textContent = 'Back to Upload';
                elements.cancelBtn.onclick = () => window.location.href = 'upload.html';
            }
        } else if (hasSuccess && hasFailures) {
            // Partial success
            showStatus(`Processing complete: ${data.successCount} succeeded, ${data.failureCount} failed`);
            redirectToResults(data.jobId || state.jobId || state.taskId);
        } else if (hasSuccess) {
            // All succeeded
            showStatus('All files processed successfully!');
            redirectToResults(data.jobId || state.jobId || state.taskId);
        } else {
            // No count information - still redirect
            showStatus('Processing complete');
            redirectToResults(data.jobId || state.jobId || state.taskId);
        }
        
        // Disable cancel button if proceeding to results
        if (elements.cancelBtn && (hasSuccess || (!hasSuccess && !hasFailures))) {
            elements.cancelBtn.disabled = true;
            elements.cancelBtn.textContent = 'Completed';
        }
    }
    
    // Helper function to redirect to results
    function redirectToResults(jobId) {
        
        showStatus('Processing complete! Redirecting to results...', 'success');
        
        // Redirect immediately
        window.location.href = `results.html?jobId=${jobId}`;
    }
    
    // Handle errors
    function handleError(error) {
        console.error('Processing error:', error);
        
        // Check if it's a connection error
        if (!state.isComplete && !state.isCancelled) {
            handleConnectionError();
        }
    }
    
    // Update overall progress bar
    function updateOverallProgress(progress) {
        state.overallProgress = Math.min(Math.max(progress, 0), 100);
        
        if (elements.progressFill) {
            elements.progressFill.style.width = `${state.overallProgress}%`;
            elements.progressFill.style.transition = 'width 0.3s ease-out';
        }
        
        if (elements.progressText) {
            elements.progressText.textContent = `${Math.round(state.overallProgress)}%`;
        }
    }
    
    // Calculate overall progress from individual file progress
    function updateOverallProgressFromFiles() {
        if (state.files.size === 0) return;
        
        let totalProgress = 0;
        let fileCount = 0;
        
        state.files.forEach((file) => {
            fileCount++;
            if (file.status === 'completed') {
                totalProgress += 100;
            } else if (file.status === 'processing' && file.progress) {
                totalProgress += file.progress;
            } else if (file.status === 'failed') {
                totalProgress += 100; // Count failed as "processed"
            }
        });
        
        const overallProgress = fileCount > 0 ? Math.round(totalProgress / fileCount) : 0;
        updateOverallProgress(overallProgress);
    }
    
    // Update file grid
    function updateFileGrid(files) {
        if (!elements.fileGrid) return;
        
        // Update state
        files.forEach(file => {
            const key = file.name || file.filename;
            if (key) {
                state.files.set(key, file);
            }
        });
        
        // Clear and rebuild grid
        elements.fileGrid.innerHTML = '';
        
        state.files.forEach((file, filename) => {
            createFileCard(filename, file);
        });
    }
    
    // Create file card
    function createFileCard(filename, fileData) {
        if (!elements.fileGrid) return;
        
        const card = document.createElement('div');
        card.className = `file-card file-status-${fileData.status || 'pending'} card-lift animate-fade-in-scale`;
        card.dataset.filename = filename;
        
        const statusIcon = getStatusIcon(fileData.status);
        const showProgress = fileData.status === 'processing' || fileData.status === 'pending';
        const progressValue = fileData.progress || 0;
        
        card.innerHTML = `
            <div class="file-card-content">
                ${fileData.thumbnail ? 
                    `<img src="${fileData.thumbnail}" alt="${filename}" class="file-thumbnail">` :
                    `<div class="file-thumbnail-placeholder">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                            <circle cx="8.5" cy="8.5" r="1.5"></circle>
                            <polyline points="21 15 16 10 5 21"></polyline>
                        </svg>
                    </div>`
                }
                <div class="file-info">
                    <h4 class="file-name" title="${filename}">${truncateFileName(filename)}</h4>
                    <div class="file-status">
                        ${statusIcon}
                        <span class="status-text">${formatStatus(fileData.status)}</span>
                    </div>
                    <div class="file-progress-bar" style="display: ${showProgress ? 'block' : 'none'}">
                        <div class="file-progress-fill" style="width: ${progressValue}%">
                            <span class="file-progress-text">${progressValue}%</span>
                        </div>
                    </div>
                    ${fileData.error ? 
                        `<div class="file-error">${fileData.error}</div>` : ''
                    }
                </div>
            </div>
        `;
        
        elements.fileGrid.appendChild(card);
    }
    
    // Update file card status
    function updateFileCard(filename, status, message, progress = null) {
        const card = document.querySelector(`[data-filename="${filename}"]`);
        if (!card) {
            // Create card if it doesn't exist
            const fileData = { 
                status: status, 
                error: status === 'failed' ? message : null,
                progress: progress || 0
            };
            state.files.set(filename, fileData);
            createFileCard(filename, fileData);
            return;
        }
        
        // Update state
        const fileData = state.files.get(filename) || {};
        fileData.status = status;
        if (status === 'failed') fileData.error = message;
        if (progress !== null) fileData.progress = progress;
        state.files.set(filename, fileData);
        
        // Update card appearance with animation
        card.className = `file-card file-status-${status} card-lift`;
        
        // Add status-specific animations
        if (status === 'completed') {
            card.classList.add('animate-scale-pulse');
        } else if (status === 'failed') {
            card.classList.add('animate-shake');
        }
        
        // Update status text
        const statusText = card.querySelector('.status-text');
        if (statusText) {
            statusText.textContent = message || formatStatus(status);
        }
        
        // Update icon
        const iconContainer = card.querySelector('.file-status');
        if (iconContainer) {
            const statusIcon = getStatusIcon(status);
            const existingIcon = iconContainer.querySelector('svg, .spinner');
            if (existingIcon) {
                existingIcon.outerHTML = statusIcon;
            }
        }
        
        // Handle progress bar visibility and value
        const progressBar = card.querySelector('.file-progress-bar');
        const showProgress = status === 'processing' || status === 'pending';
        if (progressBar) {
            progressBar.style.display = showProgress ? 'block' : 'none';
            if (showProgress && progress !== null) {
                const progressFill = progressBar.querySelector('.file-progress-fill');
                const progressText = progressBar.querySelector('.file-progress-text');
                if (progressFill) {
                    progressFill.style.width = `${progress}%`;
                }
                if (progressText) {
                    progressText.textContent = `${progress}%`;
                }
            }
        }
        
        // Update completed count and overall progress
        updateCompletedCount();
        updateOverallProgressFromFiles();
    }
    
    // Update file progress
    function updateFileProgress(filename, progress) {
        const card = document.querySelector(`[data-filename="${filename}"]`);
        if (!card) return;
        
        const progressFill = card.querySelector('.file-progress-fill');
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
    }
    
    // Get status icon
    function getStatusIcon(status) {
        const icons = {
            pending: '<svg class="status-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
            processing: '<svg class="status-icon spinning" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"></path></svg>',
            completed: '<svg class="status-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
            failed: '<svg class="status-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>'
        };
        return icons[status] || icons.pending;
    }
    
    // Format status text
    function formatStatus(status) {
        const statusMap = {
            pending: 'Waiting',
            processing: 'Processing',
            completed: 'Complete',
            failed: 'Failed'
        };
        return statusMap[status] || status || 'Unknown';
    }
    
    // Truncate filename
    function truncateFileName(name, maxLength = 25) {
        if (name.length <= maxLength) return name;
        const ext = name.split('.').pop();
        const baseName = name.substring(0, name.lastIndexOf('.'));
        const truncated = baseName.substring(0, maxLength - ext.length - 4) + '...';
        return `${truncated}.${ext}`;
    }
    
    // Update completed count
    function updateCompletedCount() {
        let completed = 0;
        state.files.forEach(file => {
            if (file.status === 'completed') completed++;
        });
        
        if (elements.filesCompleted) {
            elements.filesCompleted.textContent = completed;
        }
    }
    
    // Handle cancel
    async function handleCancel() {
        if (!confirm('Are you sure you want to cancel this batch processing?')) {
            return;
        }
        
        state.isCancelled = true;
        
        // Close SSE connection
        cleanup();
        
        try {
            // Use the API module's cancelJob function
            const result = await window.API.cancelJob(state.taskId);
            
            if (result.success) {
                showStatus('Batch processing cancelled');
                setTimeout(() => {
                    window.location.href = 'upload.html';
                }, 2000);
            } else {
                throw new Error(result.error || 'Failed to cancel batch');
            }
        } catch (error) {
            console.error('Cancel error:', error);
            showError('Failed to cancel batch processing');
            
            // Still allow going back
            if (confirm('Failed to cancel task. Return to upload page anyway?')) {
                window.location.href = 'upload.html';
            }
        }
    }
    
    // Show status message
    function showStatus(message) {
        if (elements.statusMessage) {
            elements.statusMessage.textContent = message;
            elements.statusMessage.className = 'status-message info';
            elements.statusMessage.style.display = 'block';
        }
    }
    
    // Show error message
    function showError(message) {
        if (elements.statusMessage) {
            elements.statusMessage.textContent = message;
            elements.statusMessage.className = 'status-message error';
            elements.statusMessage.style.display = 'block';
        } else {
            // Fallback to error overlay
            const errorOverlay = document.createElement('div');
            errorOverlay.className = 'error-overlay';
            errorOverlay.innerHTML = `
                <div class="error-content">
                    <svg class="error-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <h3>Processing Error</h3>
                    <p>${message}</p>
                    <button class="btn-primary" onclick="window.location.href='upload.html'">
                        Try Again
                    </button>
                </div>
            `;
            document.body.appendChild(errorOverlay);
        }
    }
    
    // Cleanup function
    function cleanup() {
        // Close SSE connection
        if (state.streamController && state.streamController.close) {
            state.streamController.close();
        }
        
        // Clear elapsed timer
        if (state.elapsedInterval) {
            clearInterval(state.elapsedInterval);
        }
    }
    
    // Setup mobile navigation
    function setupMobileNavigation() {
        const navbarToggle = document.getElementById('navbar-toggle');
        const navbarMenu = document.getElementById('navbar-menu');
        
        if (navbarToggle && navbarMenu) {
            navbarToggle.addEventListener('click', () => {
                navbarMenu.classList.toggle('active');
                navbarToggle.classList.toggle('active');
            });
            
            // Close menu when clicking a link
            const navLinks = navbarMenu.querySelectorAll('.navbar-link');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    navbarMenu.classList.remove('active');
                    navbarToggle.classList.remove('active');
                });
            });
        }
    }
    
    // Setup tips carousel
    function setupTipsCarousel() {
        const tips = document.querySelectorAll('.tip-card');
        if (tips.length === 0) return;
        
        let currentTip = 0;
        
        setInterval(() => {
            tips[currentTip].classList.remove('active');
            currentTip = (currentTip + 1) % tips.length;
            tips[currentTip].classList.add('active');
        }, 5000); // Change tip every 5 seconds
    }
    
    // Setup view toggle for file grid
    function setupViewToggle() {
        const viewBtns = document.querySelectorAll('.view-btn');
        const fileGrid = document.getElementById('fileGrid');
        
        viewBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.dataset.view;
                
                // Update button states
                viewBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Update grid class
                if (fileGrid) {
                    if (view === 'list') {
                        fileGrid.classList.add('list-view');
                    } else {
                        fileGrid.classList.remove('list-view');
                    }
                }
            });
        });
    }
    
    // Public API
    return {
        init: init
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', ProcessingModule.init);
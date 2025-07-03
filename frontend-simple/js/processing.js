// Processing page logic with enhanced SSE and UI updates
class ProcessingPage {
    constructor() {
        this.urlParams = new URLSearchParams(window.location.search);
        this.taskId = this.urlParams.get('taskId');
        this.eventSource = null;
        this.startTime = new Date();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.fileStatuses = new Map();
        
        // DOM elements
        this.elements = {
            taskId: document.getElementById('taskId'),
            fileCount: document.getElementById('fileCount'),
            startTime: document.getElementById('startTime'),
            elapsedTime: document.getElementById('elapsedTime'),
            progressFill: document.getElementById('progressFill'),
            progressText: document.querySelector('.progress-text'),
            filesCompleted: document.getElementById('filesCompleted'),
            totalFiles: document.getElementById('totalFiles'),
            fileGrid: document.getElementById('fileGrid'),
            cancelBtn: document.getElementById('cancelBtn')
        };
        
        this.init();
    }
    
    init() {
        if (!this.taskId) {
            console.error('No task ID provided');
            window.location.href = 'upload.html';
            return;
        }
        
        // Set initial UI values
        this.elements.taskId.textContent = this.taskId;
        this.elements.startTime.textContent = this.startTime.toLocaleTimeString();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Start elapsed time counter
        this.startElapsedTimer();
        
        // Connect to SSE
        this.connectToSSE();
    }
    
    setupEventListeners() {
        // Cancel button
        this.elements.cancelBtn.addEventListener('click', () => this.handleCancel());
        
        // Handle page unload
        window.addEventListener('beforeunload', () => {
            if (this.eventSource) {
                this.eventSource.close();
            }
        });
    }
    
    startElapsedTimer() {
        this.elapsedInterval = setInterval(() => {
            const elapsed = Math.floor((new Date() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            this.elements.elapsedTime.textContent = 
                minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
        }, 1000);
    }
    
    connectToSSE() {
        console.log('Connecting to SSE for task:', this.taskId);
        
        try {
            this.eventSource = api.streamProgress(this.taskId, (data) => {
                this.handleProgressUpdate(data);
            });
            
            // Add custom error handler for reconnection logic
            const originalOnerror = this.eventSource.onerror;
            this.eventSource.onerror = (error) => {
                console.error('SSE error:', error);
                this.handleSSEError();
                if (originalOnerror) originalOnerror(error);
            };
            
            // Add open handler
            this.eventSource.onopen = () => {
                console.log('SSE connection established');
                this.reconnectAttempts = 0;
            };
            
        } catch (error) {
            console.error('Failed to create EventSource:', error);
            this.showError('Failed to connect to processing stream');
        }
    }
    
    handleProgressUpdate(data) {
        console.log('Progress update:', data);
        
        // Update overall progress
        if (data.progress !== undefined) {
            this.updateProgressBar(data.progress);
        }
        
        // Update file count
        if (data.total_files !== undefined) {
            this.elements.fileCount.textContent = data.total_files;
            this.elements.totalFiles.textContent = data.total_files;
        }
        
        // Update files grid
        if (data.files && Array.isArray(data.files)) {
            this.updateFileGrid(data.files);
            this.updateCompletedCount(data.files);
        }
        
        // Handle completion
        if (data.status === 'completed' && data.job_id) {
            this.handleProcessingComplete(data.job_id);
        }
        
        // Handle failure
        if (data.status === 'failed') {
            this.handleProcessingFailed(data.error || 'Processing failed');
        }
    }
    
    updateProgressBar(percentage) {
        const progress = Math.min(100, Math.max(0, percentage));
        this.elements.progressFill.style.width = `${progress}%`;
        this.elements.progressText.textContent = `${Math.round(progress)}%`;
    }
    
    updateFileGrid(files) {
        // Update internal state
        files.forEach(file => {
            this.fileStatuses.set(file.id || file.name, file);
        });
        
        // Clear and rebuild grid
        this.elements.fileGrid.innerHTML = '';
        
        files.forEach(file => {
            const card = this.createFileCard(file);
            this.elements.fileGrid.appendChild(card);
        });
    }
    
    createFileCard(file) {
        const card = document.createElement('div');
        card.className = `file-card file-status-${file.status || 'pending'}`;
        card.id = `file-${file.id || file.name.replace(/\./g, '-')}`;
        
        // Status icon based on state
        const statusIcon = this.getStatusIcon(file.status);
        
        card.innerHTML = `
            <div class="file-card-content">
                ${file.thumbnail ? 
                    `<img src="${file.thumbnail}" alt="${file.name}" class="file-thumbnail">` :
                    `<div class="file-thumbnail-placeholder">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                            <circle cx="8.5" cy="8.5" r="1.5"></circle>
                            <polyline points="21 15 16 10 5 21"></polyline>
                        </svg>
                    </div>`
                }
                <div class="file-info">
                    <h4 class="file-name">${this.truncateFileName(file.name)}</h4>
                    <div class="file-status">
                        ${statusIcon}
                        <span class="status-text">${this.formatStatus(file.status)}</span>
                    </div>
                    ${file.progress && file.status === 'processing' ? 
                        `<div class="file-progress-bar">
                            <div class="file-progress-fill" style="width: ${file.progress}%"></div>
                        </div>` : ''
                    }
                    ${file.error ? 
                        `<div class="file-error">${file.error}</div>` : ''
                    }
                </div>
            </div>
        `;
        
        return card;
    }
    
    getStatusIcon(status) {
        const icons = {
            pending: '<svg class="status-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
            processing: '<svg class="status-icon spinning" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"></path></svg>',
            completed: '<svg class="status-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
            failed: '<svg class="status-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>'
        };
        return icons[status] || icons.pending;
    }
    
    formatStatus(status) {
        const statusMap = {
            pending: 'Waiting',
            processing: 'Processing',
            completed: 'Complete',
            failed: 'Failed'
        };
        return statusMap[status] || status || 'Unknown';
    }
    
    truncateFileName(name, maxLength = 25) {
        if (name.length <= maxLength) return name;
        const ext = name.split('.').pop();
        const baseName = name.substring(0, name.lastIndexOf('.'));
        const truncated = baseName.substring(0, maxLength - ext.length - 4) + '...';
        return `${truncated}.${ext}`;
    }
    
    updateCompletedCount(files) {
        const completed = files.filter(f => f.status === 'completed').length;
        this.elements.filesCompleted.textContent = completed;
    }
    
    handleProcessingComplete(jobId) {
        console.log('Processing complete, job ID:', jobId);
        clearInterval(this.elapsedInterval);
        
        // Show success state
        this.elements.progressFill.classList.add('progress-complete');
        
        // Close SSE connection
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        // Redirect to results after a short delay
        setTimeout(() => {
            window.location.href = `results.html?jobId=${jobId}`;
        }, 1500);
    }
    
    handleProcessingFailed(error) {
        console.error('Processing failed:', error);
        clearInterval(this.elapsedInterval);
        
        // Show error state
        this.elements.progressFill.classList.add('progress-error');
        
        // Close SSE connection
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        // Show error message
        this.showError(error);
    }
    
    handleSSEError() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        // Attempt reconnection with exponential backoff
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000);
            
            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
            
            setTimeout(() => {
                this.connectToSSE();
            }, delay);
        } else {
            this.showError('Lost connection to server. Please refresh the page.');
        }
    }
    
    async handleCancel() {
        if (!confirm('Are you sure you want to cancel processing?')) {
            return;
        }
        
        try {
            // Close SSE connection first
            if (this.eventSource) {
                this.eventSource.close();
            }
            
            // Call cancel API
            const response = await fetch(`/api/v1/tasks/${this.taskId}/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to cancel task');
            }
            
            // Redirect back to upload
            window.location.href = 'upload.html';
            
        } catch (error) {
            console.error('Cancel error:', error);
            // Even if cancel fails, allow user to go back
            if (confirm('Failed to cancel task. Return to upload page anyway?')) {
                window.location.href = 'upload.html';
            }
        }
    }
    
    showError(message) {
        // Create error overlay
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

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProcessingPage();
});
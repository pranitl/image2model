// Enhanced Results Module
const ResultsModule = (function() {
    'use strict';
    
    // State
    const state = {
        jobId: null,
        files: [],
        totalSize: 0,
        downloadProgress: 0,
        startTime: null,
        processingTime: null
    };
    
    // DOM elements
    let elements = {};
    
    // Initialize
    function init() {
        // Get job ID from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        state.jobId = urlParams.get('jobId');
        
        if (!state.jobId) {
            showError('No job ID provided. Please return to the upload page.');
            return;
        }
        
        // Cache DOM elements
        cacheElements();
        
        // Setup event listeners
        setupEventListeners();
        
        // Setup mobile navigation
        setupMobileNavigation();
        
        // Load results
        loadResults();
    }
    
    function cacheElements() {
        elements = {
            modelList: document.getElementById('modelList'),
            downloadAllBtn: document.getElementById('downloadAllBtn'),
            modelCount: document.getElementById('modelCount'),
            processingTime: document.getElementById('processingTime'),
            totalSize: document.getElementById('totalSize'),
            downloadAllSize: document.getElementById('downloadAllSize')
        };
    }
    
    function setupEventListeners() {
        // Download all button
        if (elements.downloadAllBtn) {
            elements.downloadAllBtn.addEventListener('click', handleDownloadAll);
        }
    }
    
    function setupMobileNavigation() {
        const navbarToggle = document.getElementById('navbar-toggle');
        const navbarMenu = document.getElementById('navbar-menu');
        
        if (navbarToggle && navbarMenu) {
            navbarToggle.addEventListener('click', () => {
                navbarMenu.classList.toggle('active');
                navbarToggle.classList.toggle('active');
            });
        }
    }
    
    async function loadResults() {
        try {
            // Show loading state
            showLoadingState();
            
            // Fetch job files using the api module
            const response = await window.API.getJobFiles(state.jobId);
            
            // Check if the API call was successful
            if (!response.success) {
                throw new Error(response.error || 'Failed to load job files');
            }
            
            if (!response.files || response.files.length === 0) {
                showEmptyState();
                return;
            }
            
            // Update state
            state.files = response.files;
            
            // Calculate total size
            state.totalSize = response.files.reduce((total, file) => total + (file.size || 0), 0);
            
            // Update summary
            updateSummary();
            
            // Clear loading state and display models
            displayModels(response.files);
            
            // Setup download all button
            setupDownloadAllButton();
            
        } catch (error) {
            console.error('Error loading results:', error);
            showError('Error loading results. Please try again later.');
        }
    }
    
    function showLoadingState() {
        if (elements.modelList) {
            elements.modelList.innerHTML = `
                <div class="loading-state">
                    <div class="spinner-large"></div>
                    <p>Loading your 3D models...</p>
                </div>
            `;
        }
    }
    
    function showEmptyState() {
        if (elements.modelList) {
            elements.modelList.innerHTML = `
                <div class="empty-state">
                    <svg width="64" height="64" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                    </svg>
                    <h3>No models generated</h3>
                    <p>The processing completed but no 3D models were generated.</p>
                    <p class="text-muted">This may happen if there were processing errors.</p>
                    <a href="upload.html" class="btn btn-primary">Try Again</a>
                </div>
            `;
        }
        
        if (elements.downloadAllBtn) {
            elements.downloadAllBtn.style.display = 'none';
        }
    }
    
    function updateSummary() {
        // Update model count
        if (elements.modelCount) {
            elements.modelCount.textContent = state.files.length;
            animateValue(elements.modelCount, 0, state.files.length, 1000);
        }
        
        // Update total size
        if (elements.totalSize) {
            elements.totalSize.textContent = formatFileSize(state.totalSize);
        }
        
        if (elements.downloadAllSize) {
            elements.downloadAllSize.textContent = formatFileSize(state.totalSize);
        }
        
        // Calculate processing time (mock for now)
        if (elements.processingTime) {
            const processingMinutes = Math.floor(Math.random() * 3) + 1;
            const processingSeconds = Math.floor(Math.random() * 60);
            elements.processingTime.textContent = `${processingMinutes}m ${processingSeconds}s`;
        }
    }
    
    function displayModels(files) {
        if (!elements.modelList) return;
        
        elements.modelList.innerHTML = '';
        
        files.forEach((file, index) => {
            const card = createModelCard(file, index);
            elements.modelList.appendChild(card);
        });
    }
    
    function createModelCard(file, index) {
        const card = document.createElement('div');
        card.className = 'model-card card hover-lift animate-fade-in-scale';
        card.style.animationDelay = `${index * 100}ms`;
        
        // Determine file format from filename
        const fileExt = file.filename.split('.').pop().toUpperCase();
        const format = ['GLB', 'OBJ', 'STL'].includes(fileExt) ? fileExt : 'GLB';
        
        card.innerHTML = `
            <div class="model-preview">
                ${file.rendered_image && file.rendered_image.url ? 
                    `<img src="${file.rendered_image.url}" alt="${file.filename}" class="model-thumbnail" loading="lazy">` :
                    `<div class="model-preview-placeholder">
                        <svg width="48" height="48" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 2a8 8 0 100 16 8 8 0 000-16zM7 9a1 1 0 000 2h6a1 1 0 100-2H7z"/>
                        </svg>
                        <span>3D Model</span>
                    </div>`
                }
                <span class="model-format">${format}</span>
            </div>
            <div class="model-info">
                <h3 class="model-name" title="${escapeHtml(file.filename)}">${escapeHtml(file.filename)}</h3>
                <div class="model-details">
                    <span class="model-size">${formatFileSize(file.size)}</span>
                    <span class="model-status success">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                        </svg>
                        Ready
                    </span>
                </div>
                <div class="model-actions">
                    ${createDownloadButton(file)}
                    <button class="btn btn-ghost btn-sm" onclick="ResultsModule.preview('${file.filename}')">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                            <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/>
                        </svg>
                        Preview
                    </button>
                </div>
            </div>
        `;
        
        return card;
    }
    
    function createDownloadButton(file) {
        const downloadUrl = file.downloadUrl;
        const isFalUrl = downloadUrl && (downloadUrl.includes('fal.ai') || downloadUrl.includes('fal.media') || downloadUrl.includes('fal.run'));
        
        if (isFalUrl) {
            // Direct FAL.AI URL - open in new tab
            return `
                <a href="${downloadUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 012 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                    Download
                </a>
            `;
        } else {
            // Local file URL
            return `
                <a href="/api/v1/download/${state.jobId}/${encodeURIComponent(file.filename)}" 
                   download="${file.filename}" 
                   class="btn btn-primary btn-sm">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 012 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                    Download
                </a>
            `;
        }
    }
    
    function setupDownloadAllButton() {
        if (!elements.downloadAllBtn || state.files.length === 0) return;
        
        // Check if all files are external URLs
        const allExternal = state.files.every(file => {
            const url = file.downloadUrl;
            return url && (url.includes('fal.ai') || url.includes('fal.media') || url.includes('fal.run'));
        });
        
        if (allExternal) {
            // Disable download all for external files
            elements.downloadAllBtn.disabled = true;
            elements.downloadAllBtn.title = 'Download individual files from their source';
            elements.downloadAllBtn.innerHTML = `
                <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                <span>Download Files Individually</span>
            `;
        }
    }
    
    async function handleDownloadAll() {
        if (state.files.length === 0) return;
        
        // Show download progress modal
        showDownloadProgress();
        
        try {
            // Simulate download progress
            for (let i = 0; i <= 100; i += 10) {
                updateDownloadProgress(i);
                await sleep(200);
            }
            
            // Trigger actual download
            window.location.href = `/api/v1/download/${state.jobId}/all`;
            
            // Hide modal after a delay
            setTimeout(hideDownloadProgress, 2000);
            
        } catch (error) {
            console.error('Download error:', error);
            showError('Failed to download files. Please try again.');
            hideDownloadProgress();
        }
    }
    
    function showDownloadProgress() {
        let modal = document.getElementById('downloadModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'downloadModal';
            modal.className = 'download-modal';
            modal.innerHTML = `
                <div class="download-modal-content">
                    <h3>Preparing Download</h3>
                    <div class="download-progress">
                        <div class="download-progress-bar" id="downloadProgressBar">0%</div>
                    </div>
                    <p class="download-status" id="downloadStatus">Gathering your files...</p>
                    <button class="btn btn-ghost" onclick="ResultsModule.cancelDownload()">Cancel</button>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        modal.classList.add('active');
    }
    
    function updateDownloadProgress(percent) {
        const progressBar = document.getElementById('downloadProgressBar');
        const status = document.getElementById('downloadStatus');
        
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
            progressBar.textContent = `${percent}%`;
        }
        
        if (status && percent === 100) {
            status.textContent = 'Download starting...';
        }
    }
    
    function hideDownloadProgress() {
        const modal = document.getElementById('downloadModal');
        if (modal) {
            modal.classList.remove('active');
        }
    }
    
    // Utility functions
    function formatFileSize(bytes) {
        if (!bytes || bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
    
    function animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= end) {
                element.textContent = end;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    }
    
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-toast show';
        errorDiv.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>${message}</span>
        `;
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    // Public API
    return {
        init: init,
        preview: function(filename) {
            alert(`3D preview for ${filename} coming soon!`);
        },
        cancelDownload: hideDownloadProgress
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', ResultsModule.init);
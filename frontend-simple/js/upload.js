// Enhanced Upload Module with comprehensive file handling
const UploadModule = (function() {
    'use strict';
    
    // State management
    const state = {
        files: [],
        maxFiles: 25,
        maxFileSize: 10 * 1024 * 1024, // 10MB
        allowedTypes: ['image/jpeg', 'image/jpg', 'image/png'],
        faceLimit: 10000, // default value
        objectUrls: [] // Track for cleanup
    };
    
    // DOM element references
    let dropZone, fileInput, browseBtn, fileList, generateBtn, faceLimitInput, uploadForm;
    
    // Initialize module
    function init() {
        // Cache DOM elements
        dropZone = document.getElementById('dropZone');
        fileInput = document.getElementById('fileInput');
        browseBtn = document.querySelector('#dropZone button');
        fileList = document.getElementById('fileList');
        generateBtn = document.getElementById('generateBtn');
        faceLimitInput = document.getElementById('faceLimit');
        uploadForm = document.getElementById('uploadForm');
        
        // Set up event listeners
        setupEventListeners();
        updateUI();
    }
    
    // Set up all event listeners
    function setupEventListeners() {
        // Drag and drop events
        dropZone.addEventListener('dragover', handleDragOver);
        dropZone.addEventListener('dragleave', handleDragLeave);
        dropZone.addEventListener('drop', handleDrop);
        dropZone.addEventListener('dragenter', (e) => e.preventDefault());
        
        // File input and browse button
        if (browseBtn) {
            browseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                fileInput.click();
            });
        }
        fileInput.addEventListener('change', handleFileSelect);
        
        // Form submission
        uploadForm.addEventListener('submit', handleSubmit);
        
        // Face limit input
        if (faceLimitInput) {
            faceLimitInput.addEventListener('change', (e) => {
                const value = parseInt(e.target.value);
                state.faceLimit = value > 0 ? value : 10000;
            });
        }
    }
    
    // Drag and drop handlers
    function handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        e.dataTransfer.dropEffect = 'copy';
        dropZone.classList.add('drag-over');
    }
    
    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        // Only remove class if leaving the dropzone entirely
        if (e.target === dropZone) {
            dropZone.classList.remove('drag-over');
        }
    }
    
    function handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files);
        processFiles(files);
    }
    
    function handleFileSelect(e) {
        const files = Array.from(e.target.files);
        processFiles(files);
        // Reset input to allow re-selecting same files
        e.target.value = '';
    }
    
    // Process and validate files
    function processFiles(newFiles) {
        const validFiles = [];
        const errors = [];
        
        for (const file of newFiles) {
            const validation = validateFile(file);
            if (validation.valid) {
                validFiles.push(file);
            } else {
                errors.push(`${file.name}: ${validation.error}`);
            }
        }
        
        // Check total file count
        if (state.files.length + validFiles.length > state.maxFiles) {
            const remaining = state.maxFiles - state.files.length;
            if (remaining > 0) {
                showError(`Maximum ${state.maxFiles} files allowed. You can add ${remaining} more file(s).`);
                // Add only the files that fit
                validFiles.splice(remaining);
            } else {
                showError(`Maximum ${state.maxFiles} files already reached.`);
                return;
            }
        }
        
        // Show validation errors if any
        if (errors.length > 0) {
            showError(errors.join('\\n'));
        }
        
        // Add valid files
        if (validFiles.length > 0) {
            addFiles(validFiles);
        }
    }
    
    // Validate individual file
    function validateFile(file) {
        // Check file type
        const fileType = file.type.toLowerCase();
        if (!state.allowedTypes.includes(fileType)) {
            // Also check extension as fallback
            const ext = file.name.toLowerCase().split('.').pop();
            if (!['jpg', 'jpeg', 'png'].includes(ext)) {
                return { valid: false, error: 'Invalid file type. Only JPG, JPEG, and PNG allowed.' };
            }
        }
        
        // Check file size
        if (file.size > state.maxFileSize) {
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            return { valid: false, error: `File too large (${sizeMB}MB). Maximum size is 10MB.` };
        }
        
        // Check for duplicates (by name and size)
        if (state.files.some(f => f.file.name === file.name && f.file.size === file.size)) {
            return { valid: false, error: 'File already added.' };
        }
        
        return { valid: true };
    }
    
    // Add files to state and generate previews
    function addFiles(files) {
        files.forEach(file => {
            // Create unique ID for each file
            const fileId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            const fileObj = {
                id: fileId,
                file: file,
                preview: null
            };
            
            // Add to state first
            state.files.push(fileObj);
            
            // Generate preview
            generatePreview(fileObj);
        });
        
        updateUI();
    }
    
    // Generate image preview
    function generatePreview(fileObj) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            fileObj.preview = e.target.result;
            renderFileCard(fileObj);
        };
        
        reader.onerror = function() {
            console.error('Error reading file:', fileObj.file.name);
            // Use placeholder on error
            fileObj.preview = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iIzMzMyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+RXJyb3I8L3RleHQ+PC9zdmc+';
            renderFileCard(fileObj);
        };
        
        reader.readAsDataURL(fileObj.file);
    }
    
    // Render file preview card
    function renderFileCard(fileObj) {
        // Check if card already exists
        let card = document.querySelector(`[data-file-id="${fileObj.id}"]`);
        
        if (!card) {
            card = document.createElement('div');
            card.className = 'file-card card-lift animate-fade-in-scale';
            card.dataset.fileId = fileObj.id;
            fileList.appendChild(card);
        }
        
        // Update card content
        card.innerHTML = `
            <img src="${fileObj.preview}" alt="${fileObj.file.name}" class="card-image-zoom">
            <p title="${fileObj.file.name}">${truncateFileName(fileObj.file.name)}</p>
            <small>${formatFileSize(fileObj.file.size)}</small>
            <button class="remove-btn hover-scale" onclick="UploadModule.removeFile('${fileObj.id}')">Remove</button>
        `;
    }
    
    // Remove file from list
    function removeFile(fileId) {
        // Find and remove from state
        const index = state.files.findIndex(f => f.id === fileId);
        if (index !== -1) {
            state.files.splice(index, 1);
        }
        
        // Remove from DOM
        const card = document.querySelector(`[data-file-id="${fileId}"]`);
        if (card) {
            card.remove();
        }
        
        updateUI();
    }
    
    // Handle form submission
    async function handleSubmit(e) {
        e.preventDefault();
        
        if (state.files.length === 0) {
            showError('Please select at least one image to upload.');
            return;
        }
        
        // Disable UI during upload
        setUIState('uploading');
        
        try {
            // Extract files from state
            const files = state.files.map(f => f.file);
            
            // Get face limit value
            const faceLimit = faceLimitInput.value || state.faceLimit;
            
            // Upload using API client
            const response = await api.uploadBatch(files, faceLimit);
            
            // Check if upload was successful
            if (!response || !response.success) {
                throw new Error(response?.error || 'Upload failed');
            }
            
            // Check for task ID in the response
            if (!response.taskId) {
                throw new Error('No task ID received from server');
            }
            
            // Clean up object URLs before redirect
            cleanupObjectUrls();
            
            // Show success message
            generateBtn.textContent = 'Upload successful! Redirecting...';
            
            // Redirect immediately to processing page with both IDs
            window.location.href = `processing.html?taskId=${response.taskId}&jobId=${response.jobId}`;
            
        } catch (error) {
            console.error('Upload error:', error);
            showError(`Upload failed: ${error.message}`);
            setUIState('ready');
            
            // Keep error visible for debugging
            alert(`Upload error: ${error.message}\n\nCheck console for details.`);
        }
    }
    
    // Set UI state during operations
    function setUIState(state) {
        switch(state) {
            case 'uploading':
                generateBtn.disabled = true;
                generateBtn.textContent = 'Uploading...';
                dropZone.style.pointerEvents = 'none';
                dropZone.style.opacity = '0.6';
                // Disable all remove buttons
                document.querySelectorAll('.remove-btn').forEach(btn => {
                    btn.disabled = true;
                });
                break;
            case 'ready':
                generateBtn.disabled = state.files.length === 0;
                generateBtn.textContent = 'Generate 3D Models';
                dropZone.style.pointerEvents = 'auto';
                dropZone.style.opacity = '1';
                // Re-enable remove buttons
                document.querySelectorAll('.remove-btn').forEach(btn => {
                    btn.disabled = false;
                });
                break;
        }
    }
    
    // Update UI elements
    function updateUI() {
        // Update generate button state
        generateBtn.disabled = state.files.length === 0;
        
        // Update file count display
        const fileCountText = `${state.files.length} / ${state.maxFiles} files`;
        
        // Update drop zone text
        const dropZoneText = dropZone.querySelector('p');
        if (dropZoneText) {
            if (state.files.length === 0) {
                dropZoneText.textContent = 'Drag & drop files here,';
            } else {
                dropZoneText.textContent = fileCountText;
            }
        }
        
        // Show/hide file list
        fileList.style.display = state.files.length > 0 ? 'grid' : 'none';
    }
    
    // Utility: Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Utility: Truncate long file names
    function truncateFileName(name, maxLength = 20) {
        if (name.length <= maxLength) return name;
        const ext = name.split('.').pop();
        const baseName = name.substring(0, name.lastIndexOf('.'));
        const truncated = baseName.substring(0, maxLength - ext.length - 4) + '...';
        return `${truncated}.${ext}`;
    }
    
    // Show error message
    function showError(message) {
        // Remove any existing error
        const existingError = document.querySelector('.error-toast');
        if (existingError) {
            existingError.remove();
        }
        
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-toast';
        errorDiv.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>${message}</span>
        `;
        document.body.appendChild(errorDiv);
        
        // Animate in
        setTimeout(() => errorDiv.classList.add('show'), 10);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv.classList.remove('show');
            setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
    }
    
    // Clean up object URLs to prevent memory leaks
    function cleanupObjectUrls() {
        state.objectUrls.forEach(url => {
            URL.revokeObjectURL(url);
        });
        state.objectUrls = [];
    }
    
    // Public API
    return {
        init: init,
        removeFile: removeFile,
        // Expose for debugging
        getState: () => state
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', UploadModule.init);

// Make removeFile globally accessible for onclick handlers
window.UploadModule = UploadModule;
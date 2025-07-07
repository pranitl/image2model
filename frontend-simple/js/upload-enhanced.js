// Enhanced Upload Page Functionality
(function() {
    'use strict';
    
    // DOM Elements
    const navbarToggle = document.getElementById('navbar-toggle');
    const navbarMenu = document.getElementById('navbar-menu');
    const optionsToggle = document.getElementById('optionsToggle');
    const optionsContent = document.getElementById('optionsContent');
    const faceLimitRange = document.getElementById('faceLimitRange');
    const faceLimitValue = document.getElementById('faceLimitValue');
    const faceLimitInput = document.getElementById('faceLimit');
    const presetBtns = document.querySelectorAll('.preset-btn');
    const filePreviewSection = document.getElementById('filePreviewSection');
    const fileGallery = document.getElementById('fileGallery');
    const fileCount = document.getElementById('fileCount');
    const clearAllBtn = document.getElementById('clearAllBtn');
    const addMoreBtn = document.getElementById('addMoreBtn');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    
    // State
    let draggedElement = null;
    let placeholderElement = null;
    
    // Initialize
    function init() {
        setupNavigation();
        setupAdvancedOptions();
        setupFileActions();
        setupDragAndDrop();
        enhanceUploadZone();
        setupClipboardPaste();
        setupKeyboardShortcuts();
        setupUploadModuleIntegration();
    }
    
    // Navigation setup
    function setupNavigation() {
        if (navbarToggle && navbarMenu) {
            navbarToggle.addEventListener('click', () => {
                navbarMenu.classList.toggle('active');
                navbarToggle.classList.toggle('active');
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!navbarToggle.contains(e.target) && !navbarMenu.contains(e.target)) {
                    navbarMenu.classList.remove('active');
                    navbarToggle.classList.remove('active');
                }
            });
        }
    }
    
    // Advanced options panel
    function setupAdvancedOptions() {
        if (optionsToggle && optionsContent) {
            optionsToggle.addEventListener('click', () => {
                const isActive = optionsContent.classList.contains('active');
                optionsContent.classList.toggle('active');
                optionsToggle.classList.toggle('active');
                
                // Smooth scroll into view when opening
                if (!isActive) {
                    setTimeout(() => {
                        optionsContent.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 100);
                }
            });
        }
        
        // Face limit slider
        if (faceLimitRange && faceLimitValue && faceLimitInput) {
            faceLimitRange.addEventListener('input', (e) => {
                const value = e.target.value;
                updateFaceLimitDisplay(value);
                updatePresetButtons(value);
            });
            
            // Preset buttons
            presetBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const value = btn.dataset.value;
                    setFaceLimit(value);
                    
                    // Update active state
                    presetBtns.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                });
            });
        }
    }
    
    function updateFaceLimitDisplay(value) {
        if (value === 'auto' || !value) {
            faceLimitValue.textContent = 'Auto';
            faceLimitInput.value = '';
        } else {
            const numValue = parseInt(value);
            faceLimitValue.textContent = numValue.toLocaleString();
            faceLimitInput.value = numValue;
            faceLimitRange.value = numValue;
        }
    }
    
    function updatePresetButtons(value) {
        presetBtns.forEach(btn => {
            const btnValue = btn.dataset.value;
            btn.classList.remove('active');
            
            if (btnValue === 'auto' && (!value || value === 'auto')) {
                btn.classList.add('active');
            } else if (btnValue === String(value)) {
                btn.classList.add('active');
            }
        });
    }
    
    function setFaceLimit(value) {
        updateFaceLimitDisplay(value);
        if (value !== 'auto') {
            faceLimitRange.value = value;
        }
    }
    
    // File actions
    function setupFileActions() {
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', () => {
                if (confirm('Remove all uploaded images?')) {
                    clearAllFiles();
                }
            });
        }
        
        if (addMoreBtn) {
            addMoreBtn.addEventListener('click', () => {
                fileInput.click();
            });
        }
    }
    
    function clearAllFiles() {
        // Clear the state in upload module
        if (window.UploadModule) {
            const state = window.UploadModule.getState();
            state.files = [];
        }
        
        // Clear the gallery
        fileGallery.innerHTML = '';
        filePreviewSection.style.display = 'none';
        
        // Reset UI
        updateFileCount(0);
        document.getElementById('generateBtn').disabled = true;
        
        // Show success animation
        dropZone.classList.add('upload-success');
        setTimeout(() => {
            dropZone.classList.remove('upload-success');
        }, 500);
    }
    
    // Enhanced upload zone
    function enhanceUploadZone() {
        // Make entire drop zone clickable
        dropZone.addEventListener('click', (e) => {
            if (e.target === dropZone || e.target.closest('.upload-zone-content')) {
                if (!e.target.matches('button')) {
                    fileInput.click();
                }
            }
        });
    }
    
    // Setup integration with existing upload module
    function setupUploadModuleIntegration() {
        // Wait for upload module to be ready
        const checkInterval = setInterval(() => {
            if (window.UploadModule) {
                clearInterval(checkInterval);
                integrateWithUploadModule();
            }
        }, 100);
    }
    
    function integrateWithUploadModule() {
        // Hide the original file list
        const originalFileList = document.getElementById('fileList');
        if (originalFileList) {
            originalFileList.style.display = 'none';
        }
        
        // Monitor for changes in the upload module's state
        setInterval(() => {
            if (window.UploadModule) {
                updateFileGallery();
            }
        }, 500);
    }
    
    // Update file gallery display
    function updateFileGallery() {
        if (!window.UploadModule) return;
        
        const state = window.UploadModule.getState();
        const files = state.files;
        
        if (files.length === 0) {
            filePreviewSection.style.display = 'none';
            return;
        }
        
        filePreviewSection.style.display = 'block';
        updateFileCount(files.length);
        
        // Check if gallery needs updating
        const currentCards = fileGallery.querySelectorAll('.file-preview-card');
        if (currentCards.length === files.length) {
            // Check if all file IDs match
            let needsUpdate = false;
            files.forEach((file, index) => {
                if (!fileGallery.querySelector(`[data-file-id="${file.id}"]`)) {
                    needsUpdate = true;
                }
            });
            if (!needsUpdate) return;
        }
        
        // Clear and rebuild gallery
        fileGallery.innerHTML = '';
        
        files.forEach((fileObj, index) => {
            const card = createFilePreviewCard(fileObj, index);
            fileGallery.appendChild(card);
        });
    }
    
    function createFilePreviewCard(fileObj, index) {
        const card = document.createElement('div');
        card.className = 'file-preview-card animate-fade-in-scale';
        card.dataset.fileId = fileObj.id;
        card.dataset.index = index;
        card.draggable = true;
        
        card.innerHTML = `
            <img src="${fileObj.preview || ''}" alt="${fileObj.file.name}" class="file-preview-image">
            <div class="file-preview-info">
                <div class="file-preview-name" title="${fileObj.file.name}">
                    ${truncateFileName(fileObj.file.name)}
                </div>
                <div class="file-preview-size">${formatFileSize(fileObj.file.size)}</div>
            </div>
            <button class="file-remove-btn" onclick="removeFileEnhanced('${fileObj.id}')">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L8.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L5.414 10 1.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                </svg>
            </button>
            <div class="file-preview-progress">
                <div class="file-preview-progress-bar" style="width: 0%"></div>
            </div>
        `;
        
        // Setup drag events
        setupCardDragEvents(card);
        
        return card;
    }
    
    // Drag and drop for reordering
    function setupDragAndDrop() {
        // Create placeholder element
        placeholderElement = document.createElement('div');
        placeholderElement.className = 'file-preview-card placeholder';
        placeholderElement.style.opacity = '0.5';
        placeholderElement.style.border = '2px dashed var(--accent-primary)';
    }
    
    function setupCardDragEvents(card) {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
        card.addEventListener('dragover', handleDragOver);
        card.addEventListener('drop', handleDrop);
        card.addEventListener('dragenter', handleDragEnter);
        card.addEventListener('dragleave', handleDragLeave);
    }
    
    function handleDragStart(e) {
        draggedElement = this;
        this.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', this.innerHTML);
    }
    
    function handleDragEnd(e) {
        this.classList.remove('dragging');
        
        // Remove any remaining placeholders
        const placeholders = fileGallery.querySelectorAll('.placeholder');
        placeholders.forEach(p => p.remove());
        
        // Clear drag states
        const cards = fileGallery.querySelectorAll('.file-preview-card');
        cards.forEach(card => card.classList.remove('drag-over'));
        
        draggedElement = null;
    }
    
    function handleDragOver(e) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        e.dataTransfer.dropEffect = 'move';
        
        const afterElement = getDragAfterElement(fileGallery, e.clientX, e.clientY);
        if (afterElement == null) {
            fileGallery.appendChild(placeholderElement);
        } else {
            fileGallery.insertBefore(placeholderElement, afterElement);
        }
        
        return false;
    }
    
    function handleDragEnter(e) {
        this.classList.add('drag-over');
    }
    
    function handleDragLeave(e) {
        this.classList.remove('drag-over');
    }
    
    function handleDrop(e) {
        if (e.stopPropagation) {
            e.stopPropagation();
        }
        e.preventDefault();
        
        if (draggedElement !== this) {
            // Reorder the files
            reorderFiles(draggedElement.dataset.index, this.dataset.index);
        }
        
        return false;
    }
    
    function getDragAfterElement(container, x, y) {
        const draggableElements = [...container.querySelectorAll('.file-preview-card:not(.dragging)')];
        
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offsetX = x - box.left - box.width / 2;
            const offsetY = y - box.top - box.height / 2;
            
            if (offsetX < 0 && offsetX > closest.offsetX) {
                return { offsetX: offsetX, offsetY: offsetY, element: child };
            } else {
                return closest;
            }
        }, { offsetX: Number.NEGATIVE_INFINITY, offsetY: Number.NEGATIVE_INFINITY }).element;
    }
    
    function reorderFiles(fromIndex, toIndex) {
        if (!window.UploadModule) return;
        
        const state = window.UploadModule.getState();
        const files = state.files;
        const from = parseInt(fromIndex);
        const to = parseInt(toIndex);
        
        if (from !== to) {
            const movedFile = files.splice(from, 1)[0];
            files.splice(to, 0, movedFile);
            updateFileGallery();
        }
    }
    
    // Clipboard paste support
    function setupClipboardPaste() {
        document.addEventListener('paste', (e) => {
            const items = e.clipboardData.items;
            const imageFiles = [];
            
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    const file = items[i].getAsFile();
                    if (file) {
                        imageFiles.push(file);
                    }
                }
            }
            
            if (imageFiles.length > 0 && window.UploadModule) {
                window.UploadModule.processFiles(imageFiles);
                
                // Show success animation
                dropZone.classList.add('upload-success');
                setTimeout(() => {
                    dropZone.classList.remove('upload-success');
                }, 500);
            }
        });
    }
    
    // Keyboard shortcuts
    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Delete key removes selected files
            if (e.key === 'Delete' && e.target.tagName !== 'INPUT') {
                const selectedCards = fileGallery.querySelectorAll('.file-preview-card.selected');
                if (selectedCards.length > 0) {
                    if (confirm(`Remove ${selectedCards.length} selected files?`)) {
                        selectedCards.forEach(card => {
                            removeFileEnhanced(card.dataset.fileId);
                        });
                    }
                }
            }
            
            // Ctrl/Cmd + A selects all
            if ((e.ctrlKey || e.metaKey) && e.key === 'a' && e.target.tagName !== 'INPUT') {
                e.preventDefault();
                const cards = fileGallery.querySelectorAll('.file-preview-card');
                cards.forEach(card => card.classList.add('selected'));
            }
            
            // Escape deselects all
            if (e.key === 'Escape') {
                const cards = fileGallery.querySelectorAll('.file-preview-card');
                cards.forEach(card => card.classList.remove('selected'));
            }
        });
        
        // Click to select
        fileGallery.addEventListener('click', (e) => {
            const card = e.target.closest('.file-preview-card');
            if (card && !e.target.closest('.file-remove-btn')) {
                if (e.ctrlKey || e.metaKey) {
                    card.classList.toggle('selected');
                } else {
                    // Clear other selections
                    fileGallery.querySelectorAll('.file-preview-card').forEach(c => {
                        c.classList.remove('selected');
                    });
                    card.classList.add('selected');
                }
            }
        });
    }
    
    // Helper functions
    function updateFileCount(count) {
        if (fileCount) {
            fileCount.textContent = count;
        }
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function truncateFileName(name, maxLength = 20) {
        if (name.length <= maxLength) return name;
        const ext = name.split('.').pop();
        const baseName = name.substring(0, name.lastIndexOf('.'));
        const truncated = baseName.substring(0, maxLength - ext.length - 4) + '...';
        return `${truncated}.${ext}`;
    }
    
    // Enhanced remove file function
    window.removeFileEnhanced = function(fileId) {
        if (window.UploadModule) {
            window.UploadModule.removeFile(fileId);
            
            // Show animation
            const card = document.querySelector(`[data-file-id="${fileId}"]`);
            if (card) {
                card.classList.add('animate-fade-out-scale');
                setTimeout(() => {
                    updateFileGallery();
                }, 300);
            }
        }
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
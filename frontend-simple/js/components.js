/* =================================================================
   Component JavaScript Library
   ================================================================= 
   
   Interactive functionality for the component design system.
   Vanilla JavaScript with no framework dependencies.
   
   Components:
   1. Modal System
   2. Toast Notifications  
   3. Tabs
   4. File Upload
   5. Tooltips
   6. Mobile Navigation
   
   ================================================================= */

// Component Initialization
document.addEventListener('DOMContentLoaded', () => {
    initModals();
    initToasts();
    initTabs();
    initFileUploads();
    initTooltips();
    initMobileNav();
});

/* =================================================================
   1. Modal System
   ================================================================= */

function initModals() {
    // Open modal
    document.querySelectorAll('[data-modal-open]').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = trigger.dataset.modalOpen;
            const modal = document.getElementById(modalId);
            if (modal) openModal(modal);
        });
    });

    // Close modal
    document.querySelectorAll('[data-modal-close]').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modal = trigger.closest('.modal-overlay');
            if (modal) closeModal(modal);
        });
    });

    // Close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal(overlay);
        });
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal-overlay.active');
            if (activeModal) closeModal(activeModal);
        }
    });
}

function openModal(modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Focus management
    const focusable = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable.length) focusable[0].focus();
    
    // Announce to screen readers
    modal.setAttribute('aria-hidden', 'false');
}

function closeModal(modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
    modal.setAttribute('aria-hidden', 'true');
    
    // Return focus to trigger
    const trigger = document.querySelector(`[data-modal-open="${modal.id}"]`);
    if (trigger) trigger.focus();
}

/* =================================================================
   2. Toast Notifications
   ================================================================= */

const toastQueue = [];
let isShowingToast = false;

function initToasts() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.bottom = 'var(--spacing-xl)';
        container.style.right = 'var(--spacing-xl)';
        container.style.zIndex = '1000';
        container.style.pointerEvents = 'none';
        document.body.appendChild(container);
    }
}

function showToast(message, type = 'info', duration = 3000) {
    const toast = {
        message,
        type,
        duration
    };
    
    toastQueue.push(toast);
    
    if (!isShowingToast) {
        displayNextToast();
    }
}

function displayNextToast() {
    if (toastQueue.length === 0) {
        isShowingToast = false;
        return;
    }
    
    isShowingToast = true;
    const toast = toastQueue.shift();
    
    const toastEl = document.createElement('div');
    toastEl.className = `toast toast-${toast.type}`;
    toastEl.innerHTML = `
        <div class="toast-header">
            <span class="toast-title">${getToastTitle(toast.type)}</span>
            <button class="toast-close" aria-label="Close notification">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M14.95 5.05a.75.75 0 00-1.06 0L10 8.94 6.11 5.05a.75.75 0 10-1.06 1.06L8.94 10l-3.89 3.89a.75.75 0 101.06 1.06L10 11.06l3.89 3.89a.75.75 0 101.06-1.06L11.06 10l3.89-3.89a.75.75 0 000-1.06z"/>
                </svg>
            </button>
        </div>
        <div class="toast-body">${toast.message}</div>
    `;
    toastEl.style.pointerEvents = 'auto';
    
    const container = document.getElementById('toast-container');
    container.appendChild(toastEl);
    
    // Close button
    toastEl.querySelector('.toast-close').addEventListener('click', () => {
        removeToast(toastEl);
    });
    
    // Animate in
    requestAnimationFrame(() => {
        toastEl.classList.add('show');
    });
    
    // Auto remove
    setTimeout(() => {
        removeToast(toastEl);
    }, toast.duration);
}

function removeToast(toastEl) {
    toastEl.classList.remove('show');
    
    setTimeout(() => {
        toastEl.remove();
        displayNextToast();
    }, 300);
}

function getToastTitle(type) {
    const titles = {
        success: 'Success',
        error: 'Error',
        warning: 'Warning',
        info: 'Info'
    };
    return titles[type] || 'Notification';
}

/* =================================================================
   3. Tabs
   ================================================================= */

function initTabs() {
    document.querySelectorAll('.tabs').forEach(tabContainer => {
        const buttons = tabContainer.querySelectorAll('.tab-button');
        const panels = tabContainer.querySelectorAll('.tab-panel');
        
        buttons.forEach((button, index) => {
            button.addEventListener('click', () => {
                // Update buttons
                buttons.forEach(btn => {
                    btn.classList.remove('active');
                    btn.setAttribute('aria-selected', 'false');
                });
                button.classList.add('active');
                button.setAttribute('aria-selected', 'true');
                
                // Update panels
                panels.forEach(panel => {
                    panel.classList.remove('active');
                    panel.setAttribute('aria-hidden', 'true');
                });
                if (panels[index]) {
                    panels[index].classList.add('active');
                    panels[index].setAttribute('aria-hidden', 'false');
                }
            });
            
            // Keyboard navigation
            button.addEventListener('keydown', (e) => {
                let newIndex = index;
                
                if (e.key === 'ArrowRight') {
                    newIndex = (index + 1) % buttons.length;
                } else if (e.key === 'ArrowLeft') {
                    newIndex = (index - 1 + buttons.length) % buttons.length;
                } else if (e.key === 'Home') {
                    newIndex = 0;
                } else if (e.key === 'End') {
                    newIndex = buttons.length - 1;
                }
                
                if (newIndex !== index) {
                    e.preventDefault();
                    buttons[newIndex].click();
                    buttons[newIndex].focus();
                }
            });
        });
    });
}

/* =================================================================
   4. File Upload
   ================================================================= */

function initFileUploads() {
    document.querySelectorAll('.form-file-upload').forEach(uploadArea => {
        const input = uploadArea.querySelector('input[type="file"]');
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length && input) {
                input.files = files;
                handleFileSelect(uploadArea, files);
            }
        });
        
        // File input change
        if (input) {
            input.addEventListener('change', (e) => {
                handleFileSelect(uploadArea, e.target.files);
            });
        }
    });
}

function handleFileSelect(uploadArea, files) {
    const fileList = uploadArea.querySelector('.file-list');
    if (!fileList) return;
    
    fileList.innerHTML = '';
    
    Array.from(files).forEach(file => {
        const fileCard = createFileCard(file);
        fileList.appendChild(fileCard);
    });
    
    // Dispatch custom event
    uploadArea.dispatchEvent(new CustomEvent('filesSelected', { 
        detail: { files: Array.from(files) } 
    }));
}

function createFileCard(file) {
    const card = document.createElement('div');
    card.className = 'card card-file';
    
    const isImage = file.type.startsWith('image/');
    const iconClass = isImage ? 'image-icon' : 'file-icon';
    
    card.innerHTML = `
        <div class="card-file-icon ${iconClass}">
            ${getFileIcon(file.type)}
        </div>
        <div class="card-file-info">
            <div class="card-file-name">${file.name}</div>
            <div class="card-file-meta">${formatFileSize(file.size)} • ${file.type || 'Unknown'}</div>
        </div>
        <div class="card-file-actions">
            <button class="btn btn-sm btn-ghost" aria-label="Remove ${file.name}">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M5.5 2a.5.5 0 00-.5.5V3H2.5a.5.5 0 000 1h.57l.43 8.06A1.5 1.5 0 004.5 13.5h7a1.5 1.5 0 001-1.44L12.93 4h.57a.5.5 0 000-1H11v-.5a.5.5 0 00-.5-.5h-5zM6 3v-.5h4V3H6zm1 2.5v5a.5.5 0 001 0v-5a.5.5 0 00-1 0zm3 0v5a.5.5 0 001 0v-5a.5.5 0 00-1 0z"/>
                </svg>
            </button>
        </div>
    `;
    
    // Preview for images
    if (isImage) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.createElement('img');
            preview.src = e.target.result;
            preview.alt = file.name;
            preview.style.width = '48px';
            preview.style.height = '48px';
            preview.style.objectFit = 'cover';
            preview.style.borderRadius = 'var(--radius-sm)';
            card.querySelector('.card-file-icon').appendChild(preview);
        };
        reader.readAsDataURL(file);
    }
    
    // Remove button
    card.querySelector('button').addEventListener('click', () => {
        card.remove();
    });
    
    return card;
}

function getFileIcon(type) {
    if (type.startsWith('image/')) {
        return `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
        </svg>`;
    }
    return `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z"/>
        <polyline points="13 2 13 9 20 9"/>
    </svg>`;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/* =================================================================
   5. Tooltips
   ================================================================= */

function initTooltips() {
    // Add tooltip wrapper to elements with title attribute
    document.querySelectorAll('[title]').forEach(element => {
        const tooltipText = element.getAttribute('title');
        element.removeAttribute('title');
        
        const wrapper = document.createElement('span');
        wrapper.className = 'tooltip';
        element.parentNode.insertBefore(wrapper, element);
        wrapper.appendChild(element);
        
        const tooltip = document.createElement('span');
        tooltip.className = 'tooltip-content';
        tooltip.textContent = tooltipText;
        tooltip.setAttribute('role', 'tooltip');
        wrapper.appendChild(tooltip);
    });
}

/* =================================================================
   6. Mobile Navigation
   ================================================================= */

function initMobileNav() {
    const navToggle = document.querySelector('[data-nav-toggle]');
    const navMenu = document.querySelector('.navbar-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            const isOpen = navMenu.classList.contains('active');
            navMenu.classList.toggle('active');
            navToggle.setAttribute('aria-expanded', !isOpen);
        });
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
                navToggle.focus();
            }
        });
    }
}

/* =================================================================
   Public API
   ================================================================= */

window.Components = {
    showToast,
    openModal: (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) openModal(modal);
    },
    closeModal: (modalId) => {
        const modal = document.getElementById(modalId);
        if (modal) closeModal(modal);
    }
};
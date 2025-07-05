// Results page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get job ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('jobId');
    
    if (!jobId) {
        showError('No job ID provided. Please return to the upload page.');
        return;
    }
    
    // Initialize the page
    loadResults();
    
    async function loadResults() {
        const modelList = document.getElementById('modelList');
        const downloadAllBtn = document.getElementById('downloadAllBtn');
        const container = document.querySelector('.container');
        
        try {
            // Show loading state
            modelList.innerHTML = '<p style="text-align: center;">Loading results...</p>';
            
            // Fetch job files using the api module
            const response = await api.getJobFiles(jobId);
            
            // Check if the API call was successful
            if (!response.success) {
                throw new Error(response.error || 'Failed to load job files');
            }
            
            if (!response.files || response.files.length === 0) {
                modelList.innerHTML = `
                    <div style="text-align: center; padding: 2rem;">
                        <svg style="width: 64px; height: 64px; color: var(--text-muted); margin-bottom: 1rem;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="8" x2="12" y2="12"></line>
                            <line x1="12" y1="16" x2="12.01" y2="16"></line>
                        </svg>
                        <h3>No files generated</h3>
                        <p style="color: var(--text-muted); margin: 1rem 0;">The processing completed but no 3D models were generated.</p>
                        <p style="color: var(--text-muted); font-size: 0.875rem;">This may happen if the API quota is exceeded or if there were processing errors.</p>
                        <a href="upload.html" class="btn-primary" style="margin-top: 1.5rem;">Try Again</a>
                    </div>
                `;
                downloadAllBtn.style.display = 'none';
                return;
            }
            
            // Clear loading state
            modelList.innerHTML = '';
            
            // Create download links for each file
            response.files.forEach((file, index) => {
                const modelItem = createModelItem(file, jobId);
                modelList.appendChild(modelItem);
            });
            
            // Configure download all button
            setupDownloadAllButton(downloadAllBtn, response.files, jobId);
            
        } catch (error) {
            console.error('Error loading results:', error);
            showError('Error loading results. Please try again later.');
        }
    }
    
    function createModelItem(file, jobId) {
        const modelItem = document.createElement('div');
        modelItem.className = 'model-item';
        
        // Create preview section if rendered_image exists
        if (file.rendered_image && file.rendered_image.url) {
            const previewContainer = document.createElement('div');
            previewContainer.className = 'model-item-preview';
            
            const previewImg = document.createElement('img');
            previewImg.src = file.rendered_image.url;
            previewImg.alt = `Preview of ${file.filename}`;
            previewImg.loading = 'lazy';
            
            previewContainer.appendChild(previewImg);
            modelItem.appendChild(previewContainer);
        }
        
        // Create file info section
        const fileInfo = document.createElement('div');
        fileInfo.className = 'model-item-info';
        fileInfo.innerHTML = `
            <h3>${escapeHtml(file.filename)}</h3>
            <small>${formatFileSize(file.size)} - ${getFileTypeLabel(file.mime_type)}</small>
        `;
        
        // Create actions section
        const actionsContainer = document.createElement('div');
        actionsContainer.className = 'model-item-actions';
        
        const downloadBtn = document.createElement('a');
        
        // Check if this is a FAL.AI URL
        const downloadUrl = file.downloadUrl;
        const isFalUrl = downloadUrl && (downloadUrl.includes('fal.ai') || downloadUrl.includes('fal.media') || downloadUrl.includes('fal.run'));
        
        if (isFalUrl) {
            // Direct FAL.AI URL - open in new tab
            downloadBtn.href = downloadUrl;
            downloadBtn.target = '_blank';
            downloadBtn.rel = 'noopener noreferrer';
        } else {
            // Local file URL
            downloadBtn.href = `/api/v1/download/${jobId}/${encodeURIComponent(file.filename)}`;
        }
        
        downloadBtn.className = 'btn-secondary';
        downloadBtn.textContent = 'Download';
        downloadBtn.download = file.filename;
        
        // No click tracking needed
        
        actionsContainer.appendChild(downloadBtn);
        
        modelItem.appendChild(fileInfo);
        modelItem.appendChild(actionsContainer);
        
        return modelItem;
    }
    
    function setupDownloadAllButton(button, files, jobId) {
        button.onclick = async function() {
            button.disabled = true;
            const originalText = button.textContent;
            button.textContent = 'Preparing downloads...';
            
            let downloadCount = 0;
            
            // Download each file sequentially
            for (const file of files) {
                try {
                    const link = document.createElement('a');
                    
                    // Check if this is a FAL.AI URL
                    const downloadUrl = file.downloadUrl;
                    const isFalUrl = downloadUrl && (downloadUrl.includes('fal.ai') || downloadUrl.includes('fal.media') || downloadUrl.includes('fal.run'));
                    
                    if (isFalUrl) {
                        // Direct FAL.AI URL
                        link.href = downloadUrl;
                        link.target = '_blank';
                        link.rel = 'noopener noreferrer';
                    } else {
                        // Local file URL
                        link.href = `/api/v1/download/${jobId}/${encodeURIComponent(file.filename)}`;
                    }
                    
                    link.download = file.filename;
                    link.style.display = 'none';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    downloadCount++;
                    button.textContent = `Downloading ${downloadCount}/${files.length}...`;
                    
                    // Small delay between downloads to prevent browser blocking
                    await new Promise(resolve => setTimeout(resolve, 500));
                } catch (error) {
                    console.error(`Failed to download ${file.filename}:`, error);
                }
            }
            
            button.disabled = false;
            button.textContent = originalText;
            
            // Show completion message
            if (downloadCount === files.length) {
                showToast('All files downloaded successfully!');
            } else {
                showToast(`Downloaded ${downloadCount} of ${files.length} files.`, 'warning');
            }
        };
    }
    
    function showError(message) {
        document.querySelector('.container').innerHTML = `
            <h1>Error</h1>
            <p style="color: #dc3545;">${escapeHtml(message)}</p>
            <a href="upload.html" class="btn-primary">Back to Upload</a>
        `;
    }
    
    function showToast(message, type = 'success') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${type === 'success' ? '#28a745' : '#ffc107'};
            color: ${type === 'success' ? 'white' : '#333'};
            padding: 16px 24px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function getFileTypeLabel(mimeType) {
        const typeMap = {
            'model/gltf-binary': 'GLB 3D Model',
            'model/obj': 'OBJ 3D Model',
            'application/octet-stream': '3D Model'
        };
        return typeMap[mimeType] || '3D Model';
    }
    
    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
// Processing page logic with SSE
const urlParams = new URLSearchParams(window.location.search);
const taskId = urlParams.get('taskId');
const progressFill = document.getElementById('progressFill');
const batchInfo = document.getElementById('batchInfo');
const fileGrid = document.getElementById('fileGrid');
const cancelBtn = document.getElementById('cancelBtn');

let eventSource = null;
let currentJobId = null;

if (taskId) {
    startProcessing();
} else {
    window.location.href = 'upload.html';
}

function startProcessing() {
    eventSource = api.streamProgress(taskId, handleProgressUpdate);
}

function handleProgressUpdate(data) {
    // Update progress bar
    if (data.progress !== undefined) {
        progressFill.style.width = `${data.progress}%`;
    }
    
    // Update batch info
    if (data.batch_info) {
        batchInfo.textContent = `Batch ${data.batch_info.current}/${data.batch_info.total} (${data.batch_info.files} images)`;
    }
    
    // Update file grid
    if (data.files) {
        updateFileGrid(data.files);
    }
    
    // Check if processing is complete
    if (data.status === 'completed' && data.job_id) {
        currentJobId = data.job_id;
        setTimeout(() => {
            window.location.href = `results.html?jobId=${data.job_id}`;
        }, 1000);
    }
    
    // Handle errors
    if (data.status === 'failed') {
        alert('Processing failed: ' + (data.error || 'Unknown error'));
        eventSource.close();
    }
}

function updateFileGrid(files) {
    fileGrid.innerHTML = files.map(file => `
        <div class="file-card ${file.status}">
            <h3>${file.name}</h3>
            <p>Status: ${file.status}</p>
            ${file.progress ? `<div class="file-progress">${file.progress}%</div>` : ''}
        </div>
    `).join('');
}

cancelBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to cancel processing?')) {
        if (eventSource) {
            eventSource.close();
        }
        window.location.href = 'upload.html';
    }
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (eventSource) {
        eventSource.close();
    }
});
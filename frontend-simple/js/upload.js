// File upload handling
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const generateBtn = document.getElementById('generateBtn');
const uploadForm = document.getElementById('uploadForm');

let selectedFiles = [];

// Drag and drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(files) {
    const validFiles = Array.from(files).filter(file => {
        const isValid = file.type.match(/image\/(jpeg|jpg|png)/);
        const isUnder10MB = file.size <= 10 * 1024 * 1024;
        return isValid && isUnder10MB;
    });
    
    selectedFiles = [...selectedFiles, ...validFiles].slice(0, 25);
    updateFileList();
    generateBtn.disabled = selectedFiles.length === 0;
}

function updateFileList() {
    fileList.innerHTML = selectedFiles.map((file, index) => `
        <div class="file-card">
            <img src="${URL.createObjectURL(file)}" alt="${file.name}" style="width: 100%; height: 100px; object-fit: cover;">
            <p>${file.name}</p>
            <button onclick="removeFile(${index})">Remove</button>
        </div>
    `).join('');
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
    generateBtn.disabled = selectedFiles.length === 0;
}

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    try {
        generateBtn.disabled = true;
        generateBtn.textContent = 'Uploading...';
        
        const faceLimit = document.getElementById('faceLimit').value;
        const result = await api.uploadBatch(selectedFiles, faceLimit);
        
        // Redirect to processing page
        window.location.href = `processing.html?taskId=${result.task_id}`;
    } catch (error) {
        alert('Upload failed: ' + error.message);
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate 3D Model';
    }
});
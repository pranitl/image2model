// Simple API client
const API_BASE = 'http://localhost:8000/api/v1';

const api = {
    async uploadBatch(files, faceLimit) {
        const formData = new FormData();
        files.forEach(file => formData.append('files', file));
        if (faceLimit) formData.append('face_limit', faceLimit);
        
        const response = await fetch(`${API_BASE}/upload/batch`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Upload failed');
        return response.json();
    },
    
    streamProgress(taskId, onUpdate) {
        const eventSource = new EventSource(`${API_BASE}/status/tasks/${taskId}/stream`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            onUpdate(data);
        };
        
        eventSource.onerror = () => {
            eventSource.close();
        };
        
        return eventSource;
    },
    
    async getJobFiles(jobId) {
        const response = await fetch(`${API_BASE}/download/${jobId}/all`);
        if (!response.ok) throw new Error('Failed to get files');
        return response.json();
    }
};
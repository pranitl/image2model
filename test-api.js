// Test script to debug API issue
const fetch = require('node-fetch');

async function testAPI() {
    const jobId = 'd4913ceb-db36-4b3f-af8b-80999336d50d';
    
    try {
        // Direct API call
        console.log('Testing direct API call...');
        const response = await fetch(`http://localhost:3001/api/v1/download/${jobId}/all`);
        const data = await response.json();
        console.log('Direct API response:', JSON.stringify(data, null, 2));
        
        // Simulate api.js processing
        console.log('\nSimulating api.js processing...');
        const processedResponse = {
            success: true,
            files: (data.files || []).map((file, index) => ({
                filename: file.filename,
                size: file.size || 0,
                downloadUrl: data.download_urls?.[index] || `/api/v1/download/${jobId}/${file.filename}`,
                thumbnailUrl: null,
                mimeType: file.mime_type,
                mime_type: file.mime_type,
                createdTime: file.created_time,
                rendered_image: file.rendered_image || null
            })),
            downloadAllUrl: `/api/v1/download/${jobId}/all`,
            totalFiles: data.total_files
        };
        
        console.log('Processed response:', JSON.stringify(processedResponse, null, 2));
        
        // Check what results.js would see
        console.log('\nChecking results.js logic:');
        console.log('response.success:', processedResponse.success);
        console.log('response.files exists:', !!processedResponse.files);
        console.log('response.files.length:', processedResponse.files?.length);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

testAPI();
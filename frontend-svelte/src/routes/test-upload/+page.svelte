<script>
  import { onMount } from 'svelte';
  import api from '$lib/services/api';
  import { apiKey } from '$lib/stores/auth';
  
  let result = '';
  let testing = false;
  
  async function testDirectUpload() {
    testing = true;
    result = 'Testing direct backend upload...\n';
    
    try {
      // Create a test file
      const blob = new Blob(['test content'], { type: 'image/png' });
      const file = new File([blob], 'test.png', { type: 'image/png' });
      
      // Log current state
      result += `API Key from store: ${$apiKey ? 'Set' : 'Not set'}\n`;
      result += `API Key in service: ${api.API_KEY ? 'Set' : 'Not set'}\n`;
      result += `API Base URL: ${api.API_BASE}\n\n`;
      
      // Make sure API key is set
      if ($apiKey && !api.API_KEY) {
        api.setApiKey($apiKey);
        result += 'Updated API key in service\n';
      }
      
      // Try direct fetch first
      result += 'Testing direct fetch to backend...\n';
      const formData = new FormData();
      formData.append('files', file);
      
      const directResponse = await fetch('http://localhost:8000/api/v1/upload/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${api.API_KEY || $apiKey}`
        },
        body: formData
      });
      
      result += `Direct fetch status: ${directResponse.status}\n`;
      
      if (!directResponse.ok) {
        const error = await directResponse.text();
        result += `Direct fetch error: ${error}\n\n`;
      } else {
        const data = await directResponse.json();
        result += `Direct fetch success: ${JSON.stringify(data, null, 2)}\n\n`;
      }
      
      // Now try through API service
      result += 'Testing through API service...\n';
      const apiResult = await api.uploadBatch([file], null);
      result += `API service result: ${JSON.stringify(apiResult, null, 2)}\n`;
      
    } catch (error) {
      result += `Error: ${error.message}\n`;
      result += `Stack: ${error.stack}\n`;
    }
    
    testing = false;
  }
  
  onMount(() => {
    // Make sure we have the API key
    const unsubscribe = apiKey.subscribe(value => {
      if (value && !api.API_KEY) {
        api.setApiKey(value);
      }
    });
    
    return unsubscribe;
  });
</script>

<div style="padding: 2rem; font-family: monospace;">
  <h1>Direct Upload Test</h1>
  
  <button 
    on:click={testDirectUpload} 
    disabled={testing}
    style="padding: 0.5rem 1rem; background: #007bff; color: white; border: none; cursor: pointer; margin-bottom: 1rem;"
  >
    {testing ? 'Testing...' : 'Test Upload'}
  </button>
  
  <pre style="background: #f0f0f0; padding: 1rem; white-space: pre-wrap; max-height: 600px; overflow-y: auto;">
{result || 'Click "Test Upload" to begin'}
  </pre>
</div>
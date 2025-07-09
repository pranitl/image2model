<script>
  import { onMount } from 'svelte';
  import api from '$lib/services/api';
  import { apiKey } from '$lib/stores/auth';
  import { page } from '$app/stores';
  
  let apiKeyFromStore = null;
  let apiKeyFromService = null;
  let testResult = null;
  
  $: apiKeyFromStore = $apiKey;
  
  onMount(() => {
    apiKeyFromService = api.API_KEY;
  });
  
  async function testAPI() {
    try {
      testResult = 'Testing...';
      
      // Create a mock file
      const mockFile = new File(['test content'], 'test.jpg', { type: 'image/jpeg' });
      
      // Try to upload
      const result = await api.uploadBatch([mockFile], null);
      testResult = JSON.stringify(result, null, 2);
    } catch (error) {
      testResult = `Error: ${error.message}\nStack: ${error.stack}`;
    }
  }
</script>

<div style="padding: 2rem; font-family: monospace;">
  <h1>API Test Page</h1>
  
  <div style="margin: 1rem 0;">
    <h2>API Key Status:</h2>
    <p>From Store: {apiKeyFromStore ? apiKeyFromStore.substring(0, 10) + '...' : 'NOT SET'}</p>
    <p>From Service: {apiKeyFromService ? apiKeyFromService.substring(0, 10) + '...' : 'NOT SET'}</p>
  </div>
  
  <button on:click={testAPI} style="padding: 0.5rem 1rem; background: #007bff; color: white; border: none; cursor: pointer;">
    Test Upload API
  </button>
  
  {#if testResult}
    <div style="margin-top: 1rem; padding: 1rem; background: #f0f0f0; white-space: pre-wrap;">
      {testResult}
    </div>
  {/if}
</div>
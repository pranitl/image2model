<script>
  import '../app-core.css';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import Toast from '$lib/components/Toast.svelte';
  import api from '$lib/services/api.js';
  import { apiKey } from '$lib/stores/auth.js';
  
  export let data;
  
  let mounted = false;
  
  // Set API key immediately when data is available
  $: if (data?.apiKey) {
    console.log('Setting API key from layout data');
    api.setApiKey(data.apiKey);
    apiKey.set(data.apiKey);
  }
  
  onMount(() => {
    mounted = true;
    // Double-check API key is set
    if (!data?.apiKey) {
      console.error('No API key provided from server');
    }
  });
</script>

<!-- Preload critical fonts -->
<svelte:head>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
</svelte:head>

<slot />
<Toast />

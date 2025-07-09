<script>
  import '../app-core.css';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import Toast from '$lib/components/Toast.svelte';
  import api from '$lib/services/api.js';
  
  export let data;
  
  let mounted = false;
  
  onMount(() => {
    mounted = true;
    // Set API key from server-side data
    if (data.apiKey) {
      api.setApiKey(data.apiKey);
    } else {
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

<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  onMount(() => {
    // Redirect to main upload page with dev mode
    goto('/upload?dev=true');
  });
</script>

<p>Redirecting to upload page...</p>
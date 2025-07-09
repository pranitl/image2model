<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  onMount(() => {
    // Redirect to main processing page with dev mode and results view
    goto('/processing?dev=true&results=true');
  });
</script>

<p>Redirecting to results page...</p>
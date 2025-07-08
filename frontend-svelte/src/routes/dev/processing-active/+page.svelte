<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  onMount(() => {
    // Redirect to main processing page with dev mode
    goto('/processing?dev=true');
  });
</script>

<p>Redirecting to processing page...</p>
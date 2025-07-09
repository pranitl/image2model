<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  onMount(() => {
    // Redirect to processing page with error state
    goto('/processing?dev=true&error=true');
  });
</script>

<p>Redirecting to error states...</p>
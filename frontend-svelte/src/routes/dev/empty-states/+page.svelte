<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  onMount(() => {
    // Redirect to upload page with no files (empty state)
    goto('/upload');
  });
</script>

<p>Redirecting to empty states...</p>
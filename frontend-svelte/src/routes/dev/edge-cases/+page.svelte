<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  
  onMount(() => {
    // Check for specific edge case from URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const caseType = urlParams.get('case') || 'manyFiles';
    
    // Redirect to appropriate page based on edge case type
    switch(caseType) {
      case 'slowProcessing':
        goto('/processing?dev=true&edgeCase=slowProcessing');
        break;
      case 'largeFiles':
        goto('/processing?dev=true&results=true&edgeCase=largeFiles');
        break;
      case 'mixedResults':
        goto('/processing?dev=true&results=true&edgeCase=mixedResults');
        break;
      case 'singleFile':
        goto('/processing?dev=true&results=true&edgeCase=singleFile');
        break;
      case 'manyFiles':
      default:
        goto('/processing?dev=true&edgeCase=manyFiles');
        break;
    }
  });
</script>

<p>Redirecting to edge cases...</p>
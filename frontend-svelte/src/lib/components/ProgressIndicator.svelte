<script>
  /**
   * @type {number} currentStep - Current active step in the progress flow
   * @default 1
   * Valid values: 1 (Upload), 2 (Process), 3 (Download)
   */
  export let currentStep = 1;
  
  /**
   * Step definitions for the progress indicator
   * @readonly
   */
  const steps = [
    { number: 1, text: 'Upload' },
    { number: 2, text: 'Process' },
    { number: 3, text: 'Download' }
  ];
</script>

<div class="progress-indicator">
  {#each steps as step}
    <div class="progress-step {step.number < currentStep ? 'complete' : ''} {step.number === currentStep ? 'active' : ''}">
      <span class="progress-step-number">
        {#if step.number < currentStep}
          ✓
        {:else}
          {step.number}
        {/if}
      </span>
      <span class="progress-step-text">{step.text}</span>
    </div>
  {/each}
</div>

<style>
  .progress-indicator {
    display: inline-flex;
    align-items: center;
    gap: 1rem;
    background: rgba(255, 255, 255, 0.1);
    padding: 0.5rem 1.5rem;
    border-radius: 9999px;
    backdrop-filter: blur(10px);
  }

  .progress-step {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
  }

  .progress-step:not(:last-child)::after {
    content: '';
    position: absolute;
    left: calc(100% + 0.5rem);
    top: 50%;
    transform: translateY(-50%);
    width: 1rem;
    height: 2px;
    background: rgba(255, 255, 255, 0.3);
  }

  .progress-step-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
    font-weight: 600;
    transition: all 0.3s ease;
  }

  .progress-step.complete .progress-step-number {
    background: white;
    color: #2c3e50;
    border-color: white;
  }

  .progress-step.active .progress-step-number {
    background: white;
    color: #2c3e50;
    border-color: white;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
  }

  .progress-step-text {
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 400;
  }

  .progress-step.active .progress-step-text {
    color: white;
    font-weight: 500;
  }

  /* Responsive */
  @media (max-width: 640px) {
    .progress-indicator {
      gap: 0.5rem;
      padding: 0.375rem 1rem;
    }

    .progress-step-text {
      display: none;
    }

    .progress-step-number {
      width: 28px;
      height: 28px;
      font-size: 0.75rem;
    }
  }
</style>
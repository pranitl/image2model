<script>
  import { createEventDispatcher } from 'svelte';
  
  export let value = 0;
  export let min = 0;
  export let max = 100;
  export let step = 1;
  export let label = '';
  export let description = '';
  export let displayValue = null; // Custom display value (e.g., "Auto", "5,000")
  export let presets = []; // Array of { value, label, isDefault? }
  export let disabled = false;
  export let showValue = true;
  export let valueFormatter = (val) => val.toLocaleString();
  
  const dispatch = createEventDispatcher();
  
  // Handle preset clicks
  function selectPreset(presetValue) {
    value = presetValue;
    dispatch('change', { value: presetValue });
  }
  
  // Handle slider input
  function handleInput(e) {
    value = parseFloat(e.target.value);
    dispatch('change', { value });
  }
  
  // Calculate percentage for slider fill
  $: percentage = ((value - min) / (max - min)) * 100;
  
  // Determine display value
  $: actualDisplayValue = displayValue !== null ? displayValue : valueFormatter(value);
</script>

<div class="slider-container" class:disabled>
  {#if label}
    <div class="slider-header">
      <label class="slider-label">{label}</label>
      {#if showValue}
        <div class="slider-value">{actualDisplayValue}</div>
      {/if}
    </div>
  {/if}
  
  <div class="slider-wrapper">
    <input 
      type="range" 
      class="slider-input"
      {min}
      {max}
      {step}
      {value}
      {disabled}
      on:input={handleInput}
      style="--percentage: {percentage}%"
    >
  </div>
  
  {#if presets.length > 0}
    <div class="slider-presets">
      {#each presets as preset}
        <button 
          type="button" 
          class="preset-btn"
          class:active={value === preset.value}
          on:click={() => selectPreset(preset.value)}
          {disabled}
        >
          {preset.label}
        </button>
      {/each}
    </div>
  {/if}
  
  {#if description}
    <p class="slider-description">{description}</p>
  {/if}
</div>

<style>
  .slider-container {
    width: 100%;
    margin-bottom: 1.5rem;
  }
  
  .slider-container.disabled {
    opacity: 0.6;
    pointer-events: none;
  }
  
  .slider-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }
  
  .slider-label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--brand-dark-charcoal, #3A424A);
  }
  
  .slider-value {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--brand-bright-cyan, #5DADE2);
    background: var(--blue-100, #D6EAF8);
    padding: 0.25rem 0.75rem;
    border-radius: 0.25rem;
  }
  
  .slider-wrapper {
    position: relative;
    width: 100%;
    height: 40px;
    display: flex;
    align-items: center;
  }
  
  .slider-input {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 6px;
    background: linear-gradient(
      to right,
      var(--brand-bright-cyan, #5DADE2) 0%,
      var(--brand-bright-cyan, #5DADE2) var(--percentage),
      var(--brand-light-gray, #ECF0F1) var(--percentage),
      var(--brand-light-gray, #ECF0F1) 100%
    );
    border-radius: 0.25rem;
    outline: none;
    transition: all 0.3s ease;
  }
  
  .slider-input:hover {
    opacity: 0.9;
  }
  
  .slider-input:focus {
    box-shadow: 0 0 0 3px rgba(93, 173, 226, 0.1);
  }
  
  .slider-input::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    background: var(--brand-bright-cyan, #5DADE2);
    border: 3px solid white;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }
  
  .slider-input::-webkit-slider-thumb:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    background: var(--brand-sky-blue, #3498DB);
  }
  
  .slider-input::-webkit-slider-thumb:active {
    transform: scale(0.95);
  }
  
  .slider-input::-moz-range-thumb {
    width: 20px;
    height: 20px;
    background: var(--brand-bright-cyan, #5DADE2);
    border: 3px solid white;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }
  
  .slider-input::-moz-range-thumb:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    background: var(--brand-sky-blue, #3498DB);
  }
  
  .slider-input::-moz-range-thumb:active {
    transform: scale(0.95);
  }
  
  .slider-presets {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.75rem;
  }
  
  .preset-btn {
    flex: 1;
    padding: 0.5rem 1rem;
    background: white;
    border: 1px solid var(--brand-light-gray, #ECF0F1);
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--brand-dark-charcoal, #3A424A);
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .preset-btn:hover:not(:disabled) {
    background: var(--blue-100, #D6EAF8);
    border-color: var(--brand-bright-cyan, #5DADE2);
    color: var(--brand-bright-cyan, #5DADE2);
    transform: translateY(-1px);
  }
  
  .preset-btn.active {
    background: var(--brand-bright-cyan, #5DADE2);
    border-color: var(--brand-bright-cyan, #5DADE2);
    color: white;
    box-shadow: 0 2px 8px rgba(93, 173, 226, 0.3);
  }
  
  .preset-btn:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
  
  .slider-description {
    margin-top: 0.5rem;
    font-size: 0.8125rem;
    color: var(--brand-dark-gray, #7F8C8D);
    line-height: 1.5;
  }
  
  /* Dark mode support - Future enhancement */
  @media (prefers-color-scheme: dark) {
    .slider-label {
      color: #e2e8f0;
    }
    
    .slider-value {
      background: rgba(93, 173, 226, 0.2);
      color: var(--brand-bright-cyan, #5DADE2);
    }
    
    .slider-input {
      background: linear-gradient(
        to right,
        var(--brand-bright-cyan, #5DADE2) 0%,
        var(--brand-bright-cyan, #5DADE2) var(--percentage),
        #374151 var(--percentage),
        #374151 100%
      );
    }
    
    .preset-btn {
      background: #1f2937;
      border-color: #374151;
      color: #e5e7eb;
    }
    
    .preset-btn:hover:not(:disabled) {
      background: #374151;
      border-color: var(--brand-bright-cyan, #5DADE2);
      color: var(--brand-bright-cyan, #5DADE2);
    }
    
    .preset-btn.active {
      background: var(--brand-bright-cyan, #5DADE2);
      border-color: var(--brand-bright-cyan, #5DADE2);
    }
    
    .slider-description {
      color: #9ca3af;
    }
  }
</style>
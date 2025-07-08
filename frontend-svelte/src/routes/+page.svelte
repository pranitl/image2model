<script>
  import { onMount } from 'svelte';
  
  let heroLogoElement;
  
  onMount(() => {
    // Initialize animations when component mounts
    if (typeof window !== 'undefined' && window.initializeAnimations) {
      window.initializeAnimations();
    }
  });
</script>

<!-- Navigation Bar -->
<nav class="navbar animate-fade-in">
  <div class="navbar-container">
    <a href="/" class="navbar-brand">
      <img src="/assets/logo-cropped.png" alt="image2model" class="nav-logo" width="48" height="48" loading="eager">
      <span class="brand-text">image2model</span>
    </a>
    <button class="navbar-toggle" id="navbar-toggle" aria-label="Toggle navigation">
      <span class="navbar-toggle-bar"></span>
      <span class="navbar-toggle-bar"></span>
      <span class="navbar-toggle-bar"></span>
    </button>
    <ul class="navbar-menu" id="navbar-menu">
      <li><a href="#features" class="navbar-link">Features</a></li>
      <li><a href="#how-it-works" class="navbar-link">How It Works</a></li>
      <li><a href="#examples" class="navbar-link">Examples</a></li>
      <li><a href="#pricing" class="navbar-link">Pricing</a></li>
      <li><a href="/upload" class="btn btn-primary btn-sm">Start Creating</a></li>
    </ul>
  </div>
</nav>

<!-- Hero Section -->
<section class="hero gradient-cool-ocean">
  <div class="geometric-pattern"></div>
  <div class="container">
    <div class="hero-content animate-fade-in">
      <div class="hero-logo-animated animate-float" bind:this={heroLogoElement}>
        <img src="/assets/logo-cropped.png" alt="image2model" width="150" height="150" class="hero-logo" loading="eager">
      </div>
      <h1 class="display gradient-text-blue animate-gradient">Transform Images Into 3D Models</h1>
      <p class="hero-description lead animate-fade-in-up delay-200">
        Turn your photos into professional 3D models instantly. No expertise required - just upload and let our AI work its magic.
      </p>
      <div class="hero-cta animate-fade-in-scale delay-400">
        <a href="/upload" class="btn btn-primary btn-lg hover-lift">
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L11 6.414V13a1 1 0 11-2 0V6.414L7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3z"/>
            <path d="M3 11a1 1 0 011 1v3a1 1 0 001 1h10a1 1 0 001-1v-3a1 1 0 112 0v3a3 3 0 01-3 3H5a3 3 0 01-3-3v-3a1 1 0 011-1z"/>
          </svg>
          Start Creating Now
        </a>
        <a href="#demo" class="btn btn-ghost btn-lg">
          Watch Demo
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/>
          </svg>
        </a>
      </div>
      <div class="hero-stats animate-fade-in delay-600">
        <div class="stat-item">
          <span class="stat-number gradient-text-blue">&lt;1min</span>
          <span class="stat-label">Processing Time</span>
        </div>
        <div class="stat-item">
          <span class="stat-number gradient-text-blue">Batch</span>
          <span class="stat-label">Processing Ready</span>
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  /* Blue Theme Style Overrides for Better Contrast */
  
  /* Override gradient backgrounds for blue theme */
  :global(.gradient-cool-ocean) {
    background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%) !important;
  }
  
  :global(.gradient-primary) {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
  }

  /* Blue gradient variations for feature icons */
  :global(.gradient-blue-light) {
    background: linear-gradient(135deg, #85C1E9 0%, #5DADE2 100%);
  }

  :global(.gradient-blue-medium) {
    background: linear-gradient(135deg, #5DADE2 0%, #3498DB 100%);
  }

  :global(.gradient-blue-dark) {
    background: linear-gradient(135deg, #2874A6 0%, #1B4F72 100%);
  }
  
  /* Text that should be white on dark blue backgrounds */
  :global(.hero h1),
  :global(.hero .hero-description),
  :global(.cta-title),
  :global(.cta-subtitle) {
    color: #ffffff !important;
    -webkit-text-fill-color: initial !important;
    background: none !important;
  }
  
  /* Accent text with blue gradient - only for elements on light backgrounds */
  :global(.gradient-text-blue) {
    background: linear-gradient(135deg, #3498db 0%, #5dade2 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    background-size: 200% 200%;
    animation: gradient-shift 3s ease-in-out infinite;
  }
  
  /* Stats should be white on dark backgrounds */
  :global(.hero-stats .stat-number) {
    color: #ffffff !important;
    -webkit-text-fill-color: initial !important;
    background: none !important;
    font-weight: 700;
  }
  
  :global(.hero-stats .stat-label) {
    color: #bdc3c7 !important;
  }

  /* Navigation Styles */
  :global(.navbar) {
    background-color: rgba(26, 35, 50, 0.98);
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  }

  :global(.navbar-link) {
    color: #ecf0f1;
  }

  :global(.navbar-link:hover) {
    color: #5dade2;
  }
  
  :global(.navbar-brand) {
    color: #ffffff !important;
  }
  
  :global(.navbar-brand .brand-text) {
    color: #ffffff !important;
  }

  /* Button overrides for blue theme */
  :global(.btn-primary) {
    background: linear-gradient(135deg, #5dade2 0%, #3498db 100%) !important;
    color: #ffffff !important;
    font-weight: 600;
    border: none;
  }
  
  :global(.btn-primary:hover) {
    background: linear-gradient(135deg, #3498db 0%, #2874a6 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 14px 0 rgba(93, 173, 226, 0.4);
  }
  
  :global(.btn-secondary) {
    background-color: #ecf0f1 !important;
    color: #2c3e50 !important;
    border: 1px solid #ecf0f1 !important;
  }
  
  :global(.btn-secondary:hover) {
    background-color: #bdc3c7 !important;
    border-color: #bdc3c7 !important;
  }
  
  :global(.btn-ghost) {
    background-color: transparent;
    color: #ffffff !important;
    border: 2px solid rgba(255, 255, 255, 0.3);
  }
  
  :global(.btn-ghost:hover) {
    background-color: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.5);
    color: #ffffff !important;
  }
</style>

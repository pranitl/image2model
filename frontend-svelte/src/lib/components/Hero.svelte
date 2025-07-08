<script>
  /**
   * @type {string} title - Main heading text displayed in the hero section
   */
  export let title = '';
  
  /**
   * @type {string} subtitle - Optional subtitle text displayed below the title
   */
  export let subtitle = '';
  
  /**
   * @type {'default'|'landing'} variant - Visual variant of the hero section
   * - 'default': Standard hero with normal padding
   * - 'landing': Larger hero with increased height for landing pages
   */
  export let variant = 'default';
</script>

<section class="hero {variant}" {...$$restProps}>
  <div class="geometric-pattern"></div>
  <div class="container">
    <div class="hero-content">
      <h1 class="hero-title">{title}</h1>
      {#if subtitle}
        <p class="hero-subtitle">{subtitle}</p>
      {/if}
      <slot name="content"></slot>
    </div>
  </div>
</section>

<style>
  .hero {
    background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);
    color: white;
    padding: 4rem 0 5rem;
    position: relative;
    overflow: hidden;
    text-align: center;
  }

  .hero.landing {
    padding: 6rem 0 7rem;
    min-height: 600px;
    display: flex;
    align-items: center;
  }

  .geometric-pattern {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    opacity: 0.5;
  }

  .container {
    position: relative;
    z-index: 1;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  .hero-content {
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .hero-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: white !important;
    line-height: 1.2;
    /* Override any gradient text effects */
    background: none !important;
    -webkit-background-clip: initial !important;
    -webkit-text-fill-color: white !important;
    text-fill-color: white !important;
  }

  .hero-subtitle {
    font-size: 1.25rem;
    opacity: 0.9;
    margin-bottom: 2rem;
    color: white !important;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    /* Override any gradient text effects */
    background: none !important;
    -webkit-background-clip: initial !important;
    -webkit-text-fill-color: white !important;
    text-fill-color: white !important;
  }

  /* Animation classes */
  :global(.hero .animate-fade-in-up) {
    animation: fadeInUp 0.6s ease-out;
  }

  :global(.hero .animate-fade-in-up.delay-200) {
    animation-delay: 0.2s;
    animation-fill-mode: both;
  }

  :global(.hero .animate-fade-in-scale) {
    animation: fadeInScale 0.6s ease-out;
  }

  :global(.hero .animate-fade-in-scale.delay-400) {
    animation-delay: 0.4s;
    animation-fill-mode: both;
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeInScale {
    from {
      opacity: 0;
      transform: scale(0.9);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  /* Responsive */
  @media (max-width: 768px) {
    .hero {
      padding: 3rem 0 4rem;
    }

    .hero.landing {
      padding: 4rem 0 5rem;
      min-height: 500px;
    }

    .hero-title {
      font-size: 2rem;
    }

    .hero-subtitle {
      font-size: 1.125rem;
    }
  }
</style>
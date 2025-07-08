<script>
  import { onMount } from 'svelte';
  
  let heroLogoElement;
  let navbarToggle;
  let navbarMenu;
  let mobileMenuActive = false;
  
  onMount(() => {
    // Initialize animations when component mounts
    if (typeof window !== 'undefined' && window.initializeAnimations) {
      window.initializeAnimations();
    }
    
    // Smooth scroll for anchor links
    const anchors = document.querySelectorAll('a[href^="#"]');
    anchors.forEach(anchor => {
      anchor.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = anchor.getAttribute('href').slice(1);
        const target = document.getElementById(targetId);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  });
  
  function toggleMobileMenu() {
    mobileMenuActive = !mobileMenuActive;
  }
  
  function closeMobileMenu() {
    mobileMenuActive = false;
  }
</script>

<!-- Navigation Bar -->
<nav class="navbar animate-fade-in">
  <div class="navbar-container">
    <a href="/" class="navbar-brand">
      <img src="/assets/logo-cropped.png" alt="image2model" class="nav-logo" width="48" height="48" loading="eager">
      <span class="brand-text">image2model</span>
    </a>
    <button class="navbar-toggle" class:active={mobileMenuActive} on:click={toggleMobileMenu} aria-label="Toggle navigation">
      <span class="navbar-toggle-bar"></span>
      <span class="navbar-toggle-bar"></span>
      <span class="navbar-toggle-bar"></span>
    </button>
    <ul class="navbar-menu" class:active={mobileMenuActive}>
      <li><a href="#features" class="navbar-link" on:click={closeMobileMenu}>Features</a></li>
      <li><a href="#how-it-works" class="navbar-link" on:click={closeMobileMenu}>How It Works</a></li>
      <li><a href="#examples" class="navbar-link" on:click={closeMobileMenu}>Examples</a></li>
      <li><a href="#pricing" class="navbar-link" on:click={closeMobileMenu}>Pricing</a></li>
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

<!-- Features Section -->
<section id="features" class="features-section">
  <div class="container">
    <div class="section-header">
      <h2 class="section-title animate-fade-in">Why Choose image2model?</h2>
      <p class="section-subtitle text-secondary animate-fade-in-up delay-200">
        Professional tools that make 3D content creation accessible to everyone.
      </p>
    </div>
    
    <div class="features-grid">
      <div class="feature-card card card-hover reveal-on-scroll">
        <div class="feature-icon gradient-blue-medium">
          <svg width="32" height="32" fill="currentColor" viewBox="0 0 20 20">
            <path d="M13 7H7v6h6V7z"/>
            <path fill-rule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2z" clip-rule="evenodd"/>
          </svg>
        </div>
        <h3 class="feature-title">AI-Powered Precision</h3>
        <p class="feature-description">Advanced neural networks analyze every detail to create accurate 3D representations.</p>
      </div>

      <div class="feature-card card card-hover reveal-on-scroll delay-stagger">
        <div class="feature-icon gradient-blue-medium">
          <svg width="32" height="32" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
          </svg>
        </div>
        <h3 class="feature-title">Lightning Fast</h3>
        <p class="feature-description">Get your 3D models in under a minute. Our optimized AI pipeline delivers rapid results.</p>
      </div>

      <div class="feature-card card card-hover reveal-on-scroll delay-stagger">
        <div class="feature-icon gradient-blue-medium">
          <svg width="32" height="32" fill="currentColor" viewBox="0 0 20 20">
            <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z"/>
            <path fill-rule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clip-rule="evenodd"/>
          </svg>
        </div>
        <h3 class="feature-title">Batch Processing</h3>
        <p class="feature-description">Upload multiple images at once and process them all together. Perfect for large projects!</p>
      </div>

      <div class="feature-card card card-hover reveal-on-scroll delay-stagger">
        <div class="feature-icon gradient-blue-medium">
          <svg width="32" height="32" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
        </div>
        <h3 class="feature-title">Secure & Private</h3>
        <p class="feature-description">Your images and models are encrypted and never shared. Enterprise-grade security.</p>
      </div>
    </div>
  </div>
</section>

<!-- How It Works Section -->
<section id="how-it-works" class="how-it-works">
  <div class="container">
    <div class="section-header">
      <h2 class="section-title animate-fade-in">Simple Three-Step Process</h2>
      <p class="section-subtitle text-secondary animate-fade-in-up delay-200">
        No 3D expertise required - just upload and let AI do the work!
      </p>
    </div>

    <div class="steps">
      <div class="step card card-lift reveal-on-scroll">
        <div class="step-icon gradient-blue-medium">
          <svg width="48" height="48" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z"/>
          </svg>
        </div>
        <span class="step-number gradient-animated">1</span>
        <h3 class="step-title">Upload Your Images</h3>
        <p class="step-description">Drag and drop or browse to upload JPG, PNG, or HEIC images. Multiple angles improve accuracy.</p>
      </div>
      <div class="step card card-lift reveal-on-scroll delay-stagger">
        <div class="step-icon gradient-blue-medium animate-spin-slow">
          <svg width="48" height="48" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd"/>
          </svg>
        </div>
        <span class="step-number gradient-animated">2</span>
        <h3 class="step-title">AI Processing Magic</h3>
        <p class="step-description">Our neural networks analyze depth, texture, and geometry to reconstruct your 3D model.</p>
      </div>
      <div class="step card card-lift reveal-on-scroll delay-stagger">
        <div class="step-icon gradient-blue-medium">
          <svg width="48" height="48" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"/>
          </svg>
        </div>
        <span class="step-number gradient-animated">3</span>
        <h3 class="step-title">Download & Create</h3>
        <p class="step-description">Preview, refine, and download your model in your preferred format. Ready for any project.</p>
      </div>
    </div>

  </div>
</section>

<!-- Transformation Examples Section -->
<section id="examples" class="examples-section">
  <div class="container">
    <div class="section-header">
      <h2 class="section-title animate-fade-in">See the Magic in Action</h2>
      <p class="section-subtitle text-secondary animate-fade-in-up delay-200">
        Real transformations from real photos.
      </p>
    </div>

    <div class="examples-grid">
      <div class="example-card reveal-on-scroll">
        <div class="example-content">
          <div class="example-gallery">
            <div class="example-image-wrapper">
              <img src="/assets/examples/jacket-before.png" alt="Vintage military jacket on display" class="example-image" loading="lazy">
              <span class="example-label">Original Photo</span>
            </div>
            <div class="example-image-wrapper">
              <img src="/assets/examples/jacket-after.webp" alt="3D rendered model of vintage military jacket" class="example-image" loading="lazy">
              <span class="example-label">3D Model</span>
            </div>
          </div>
          <div class="example-info">
            <h3 class="example-title">Artifacts / Museum Objects</h3>
            <p class="example-description">Transform  photos into explorable 3D objects.</p>
            <a href="/upload" class="btn btn-secondary btn-sm">Try with this image</a>
          </div>
        </div>
      </div>

      <div class="example-card reveal-on-scroll delay-stagger">
        <div class="example-content">
          <div class="example-gallery">
            <div class="example-image-wrapper">
              <img src="/assets/examples/jordan1s-before.jpg" alt="Red and black Jordan 1 sneakers on white background" class="example-image" loading="lazy">
              <span class="example-label">Original Photo</span>
            </div>
            <div class="example-image-wrapper">
              <img src="/assets/examples/jordan1s-after.webp" alt="3D rendered model of red and black Jordan 1 sneakers" class="example-image" loading="lazy">
              <span class="example-label">3D Model</span>
            </div>
          </div>
          <div class="example-info">
            <h3 class="example-title">Product Photography</h3>
            <p class="example-description">E-commerce ready 3D models from simple product photos.</p>
            <a href="/upload" class="btn btn-secondary btn-sm">Try with this image</a>
          </div>
        </div>
      </div>

      <div class="example-card reveal-on-scroll delay-stagger">
        <div class="example-content">
          <div class="example-gallery">
            <div class="example-image-wrapper">
              <img src="/assets/examples/chair-before.png" alt="Modern office chair on white background" class="example-image" loading="lazy">
              <span class="example-label">Original Photo</span>
            </div>
            <div class="example-image-wrapper">
              <img src="/assets/examples/chair-rendered.webp" alt="3D rendered model of modern office chair" class="example-image" loading="lazy">
              <span class="example-label">3D Model</span>
            </div>
          </div>
          <div class="example-info">
            <h3 class="example-title">Furniture</h3>
            <p class="example-description">Create immersive 3D objects from furniture photos.</p>
            <a href="/upload" class="btn btn-secondary btn-sm">Try with this image</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>


<!-- CTA Section -->
<section class="cta-section gradient-primary">
  <div class="container">
    <div class="cta-content animate-fade-in">
      <h2 class="cta-title">Ready to Transform Your First Image?</h2>
      <p class="cta-subtitle">Start creating professional 3D models from your images today!</p>
      <div class="cta-buttons animate-fade-in-scale delay-200">
        <a href="/upload" class="btn btn-primary btn-lg hover-lift">
          Start Creating
        </a>
      </div>
    </div>
  </div>
</section>

<!-- Footer -->
<footer class="site-footer">
  <div class="footer-container">
    <div class="footer-content">
      <div class="footer-brand">
        <img src="/assets/logo-cropped.png" alt="image2model" width="64" height="64" class="footer-logo">
        <p class="footer-tagline">Making 3D content creation accessible to everyone!</p>
      </div>
      <div class="footer-links">
        <ul class="footer-list">
          <li><a href="#features">Features</a></li>
          <li><a href="#pricing">Pricing</a></li>
          <li><a href="#contact">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="footer-text">&copy; 2025 image2model. All rights reserved.</p>
    </div>
  </div>
</footer>

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
  
  /* Ensure proper contrast for sections */
  :global(.features-section),
  :global(.examples-section) {
    background-color: #f8f9fa;
  }
  
  :global(.how-it-works) {
    background-color: #ecf0f1;
  }
  
  /* Card backgrounds */
  :global(.card),
  :global(.feature-card),
  :global(.step),
  :global(.example-card) {
    background-color: #ffffff !important;
  }
  
  /* Text colors for better contrast */
  :global(.section-title),
  :global(.feature-title),
  :global(.step-title),
  :global(.example-title) {
    color: #2c3e50 !important;
  }
  
  :global(.section-subtitle),
  :global(.feature-description),
  :global(.step-description),
  :global(.example-description) {
    color: #34495e !important;
  }
  
  /* Footer styling with blue theme */
  :global(.site-footer) {
    background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);
    color: #ecf0f1;
    padding: 3rem 0 2rem;
    margin-top: 4rem;
  }
  
  :global(.footer-container) {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }
  
  :global(.footer-content) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 2rem;
    margin-bottom: 2rem;
  }
  
  :global(.footer-brand) {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  :global(.footer-logo) {
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
  }
  
  :global(.footer-tagline) {
    color: #bdc3c7;
    margin: 0;
  }
  
  :global(.footer-links) {
    display: flex;
    align-items: center;
  }
  
  :global(.footer-list) {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    gap: 2rem;
  }
  
  :global(.footer-list a) {
    color: #ecf0f1;
    text-decoration: none;
    transition: color 0.3s ease;
  }
  
  :global(.footer-list a:hover) {
    color: #5dade2;
  }
  
  :global(.footer-bottom) {
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  :global(.footer-text) {
    color: #95a5a6;
    margin: 0;
    font-size: 0.875rem;
    text-align: left;
  }
  
  /* Navbar alignment fixes */
  :global(.navbar-brand) {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
  }
  
  :global(.nav-logo) {
    vertical-align: middle;
  }
  
  :global(.brand-text) {
    font-size: 1.25rem;
    font-weight: 600;
    line-height: 1;
  }
  
  :global(.navbar-menu) {
    display: flex;
    align-items: center;
    gap: 2rem;
    list-style: none;
    margin: 0;
    padding: 0;
  }
  
  :global(.navbar-menu li) {
    display: flex;
    align-items: center;
  }
  
  :global(.navbar-menu .btn-sm) {
    padding: 0.25rem 0.875rem !important;
    font-size: 0.875rem !important;
    line-height: 1.25 !important;
    height: auto !important;
    min-height: unset !important;
  }
  
  /* Hero stats spacing fix */
  :global(.hero-stats) {
    display: flex;
    justify-content: center;
    gap: 4rem !important;
    margin-top: 3rem;
  }
  
  :global(.stat-item) {
    text-align: center;
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    :global(.footer-content) {
      flex-direction: column;
      text-align: center;
    }
    
    :global(.footer-brand) {
      flex-direction: column;
    }
    
    :global(.footer-list) {
      flex-direction: column;
      gap: 1rem;
    }
    
    :global(.hero-stats) {
      gap: 2rem !important;
    }
  }
</style>

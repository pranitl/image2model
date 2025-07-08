<script>
  import { page } from '$app/stores';
  import { browser } from '$app/environment';
  
  export let variant = 'default'; // 'default' or 'landing'
  
  let mobileMenuActive = false;
  
  function toggleMobileMenu() {
    mobileMenuActive = !mobileMenuActive;
  }
  
  function closeMobileMenu() {
    mobileMenuActive = false;
  }
  
  // Smooth scroll handler for anchor links
  function handleAnchorClick(e) {
    const href = e.target.getAttribute('href');
    if (href?.startsWith('#') && browser) {
      e.preventDefault();
      const target = document.querySelector(href);
      target?.scrollIntoView({ behavior: 'smooth' });
      closeMobileMenu();
    }
  }
  
  // Navigation items
  const navItems = variant === 'landing' 
    ? [
        { href: '#features', label: 'Features' },
        { href: '#how-it-works', label: 'How It Works' },
        { href: '#examples', label: 'Examples' },
        { href: '#pricing', label: 'Pricing' }
      ]
    : [
        { href: '/#features', label: 'Features' },
        { href: '/#how-it-works', label: 'How It Works' },
        { href: '/#examples', label: 'Examples' },
        { href: '/#pricing', label: 'Pricing' }
      ];
</script>

<nav class="navbar animate-fade-in">
  <div class="navbar-container">
    <a href="/" class="navbar-brand">
      <img src="/assets/logo-cropped.png" alt="image2model" class="nav-logo" width="48" height="48" loading="eager">
      <span class="brand-text">image2model</span>
    </a>
    
    <button 
      class="navbar-toggle" 
      class:active={mobileMenuActive} 
      on:click={toggleMobileMenu} 
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggle-bar"></span>
      <span class="navbar-toggle-bar"></span>
      <span class="navbar-toggle-bar"></span>
    </button>
    
    <ul class="navbar-menu" class:active={mobileMenuActive}>
      {#each navItems as item}
        <li>
          <a 
            href={item.href} 
            class="navbar-link" 
            on:click={variant === 'landing' ? handleAnchorClick : closeMobileMenu}
          >
            {item.label}
          </a>
        </li>
      {/each}
      {#if variant === 'landing'}
        <li><a href="/upload" class="btn btn-primary btn-sm">Start Creating</a></li>
      {/if}
    </ul>
  </div>
</nav>

<style>
  .navbar {
    position: fixed;
    top: 0;
    width: 100%;
    background: rgba(26, 32, 44, 0.95);
    backdrop-filter: blur(10px);
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  .navbar-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 70px;
  }

  .navbar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
    color: white;
    font-weight: 600;
    font-size: 1.25rem;
  }

  .nav-logo {
    height: 48px;
    width: 48px;
  }

  .brand-text {
    color: white;
  }

  .navbar-toggle {
    display: none;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
    flex-direction: column;
    gap: 4px;
  }

  .navbar-toggle-bar {
    width: 25px;
    height: 3px;
    background: white;
    transition: all 0.3s ease;
    display: block;
  }

  .navbar-toggle.active .navbar-toggle-bar:nth-child(1) {
    transform: rotate(45deg) translate(5px, 5px);
  }

  .navbar-toggle.active .navbar-toggle-bar:nth-child(2) {
    opacity: 0;
  }

  .navbar-toggle.active .navbar-toggle-bar:nth-child(3) {
    transform: rotate(-45deg) translate(7px, -6px);
  }

  .navbar-menu {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: 2rem;
    align-items: center;
  }

  .navbar-link {
    color: rgba(255, 255, 255, 0.9);
    text-decoration: none;
    transition: color 0.3s ease;
    font-weight: 500;
  }

  .navbar-link:hover {
    color: #3b82f6;
  }

  /* Mobile styles */
  @media (max-width: 768px) {
    .navbar-toggle {
      display: flex;
    }

    .navbar-menu {
      position: absolute;
      top: 70px;
      left: 0;
      right: 0;
      background: rgba(26, 32, 44, 0.98);
      flex-direction: column;
      padding: 1rem;
      gap: 1rem;
      transform: translateY(-100%);
      opacity: 0;
      transition: all 0.3s ease;
      pointer-events: none;
    }

    .navbar-menu.active {
      transform: translateY(0);
      opacity: 1;
      pointer-events: all;
    }

    .navbar-menu li {
      width: 100%;
      text-align: center;
    }
  }

  /* Button styles - imported from global */
  :global(.btn) {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1rem;
  }

  :global(.btn-primary) {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
  }

  :global(.btn-primary:hover) {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
  }

  :global(.btn-sm) {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }
</style>
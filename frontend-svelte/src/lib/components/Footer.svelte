<footer class="site-footer">
  <div class="footer-container">
    <div class="footer-content">
      <div class="footer-brand">
        <img src="/assets/logo-cropped.png" alt="image2model" width="64" height="64" class="footer-logo">
        <p class="footer-tagline">Making 3D content creation accessible to everyone!</p>
      </div>
      <div class="footer-links">
        <ul class="footer-list">
          <li><a href="/#features">Features</a></li>
          <li><a href="/#pricing">Pricing</a></li>
          <li><a href="/#contact">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="footer-text">&copy; 2025 image2model. All rights reserved.</p>
    </div>
  </div>
</footer>

<style>
  /* Footer styles moved from global CSS */
  .site-footer {
    background-color: #1a202c;
    color: white;
    padding: 3rem 0 1.5rem;
    margin-top: 5rem;
  }

  .footer-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  .footer-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .footer-brand {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .footer-logo {
    height: 64px;
    width: 64px;
  }

  .footer-tagline {
    color: #cbd5e0;
    font-size: 0.875rem;
    margin: 0;
  }

  .footer-links {
    display: flex;
    gap: 3rem;
  }

  .footer-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    gap: 2rem;
  }

  .footer-list a {
    color: #cbd5e0;
    text-decoration: none;
    transition: color 0.3s ease;
  }

  .footer-list a:hover {
    color: #2196f3;
  }

  .footer-bottom {
    text-align: center;
  }

  .footer-text {
    color: #718096;
    font-size: 0.875rem;
    margin: 0;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .footer-content {
      flex-direction: column;
      gap: 2rem;
    }

    .footer-links {
      width: 100%;
    }

    .footer-list {
      flex-direction: column;
      gap: 1rem;
    }

    .footer-bottom {
      margin-top: 2rem;
    }
  }
</style>
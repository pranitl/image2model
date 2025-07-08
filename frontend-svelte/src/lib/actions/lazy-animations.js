// Lazy-loaded animation utilities
let animationsLoaded = false;
let animationModule = null;

// Lazy load animation actions
export async function lazyScrollReveal(node, options = {}) {
  if (!animationsLoaded) {
    animationModule = await import('./animations.js');
    animationsLoaded = true;
  }
  
  return animationModule.scrollReveal(node, options);
}

export async function lazyStaggerReveal(node, options = {}) {
  if (!animationsLoaded) {
    animationModule = await import('./animations.js');
    animationsLoaded = true;
  }
  
  return animationModule.staggerReveal(node, options);
}

export async function lazyParallax(node, options = {}) {
  if (!animationsLoaded) {
    animationModule = await import('./animations.js');
    animationsLoaded = true;
  }
  
  return animationModule.parallax(node, options);
}

// Check if user prefers reduced motion
export function prefersReducedMotion() {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// Conditional animation loader
export function conditionalAnimation(node, animationType, options = {}) {
  if (prefersReducedMotion()) {
    // Skip animations for users who prefer reduced motion
    node.style.opacity = '1';
    node.style.transform = 'none';
    return {
      destroy() {}
    };
  }
  
  // Load animations based on viewport visibility
  const observer = new IntersectionObserver(
    async (entries) => {
      if (entries[0].isIntersecting) {
        observer.disconnect();
        
        switch (animationType) {
          case 'scroll':
            await lazyScrollReveal(node, options);
            break;
          case 'stagger':
            await lazyStaggerReveal(node, options);
            break;
          case 'parallax':
            await lazyParallax(node, options);
            break;
        }
      }
    },
    { rootMargin: '100px' }
  );
  
  observer.observe(node);
  
  return {
    destroy() {
      observer.disconnect();
    }
  };
}
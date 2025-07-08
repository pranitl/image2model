// Simple error handler fallback
function handleAnimationError(error, element) {
  console.warn('Animation error:', error);
  if (element) {
    element.style.opacity = '1';
    element.style.transform = 'none';
  }
}

// Svelte action for scroll-based animations (SSR-safe with error handling)
export function scrollReveal(node, options = {}) {
  const {
    threshold = 0.1,
    rootMargin = '50px',
    animationClass = 'animate-in',
    hiddenClass = 'scroll-hidden'
  } = options;

  let observer;

  function handleIntersect(entries) {
    entries.forEach(entry => {
      try {
        if (entry.isIntersecting) {
          entry.target.classList.remove(hiddenClass);
          entry.target.classList.add(animationClass);
          if (options.once !== false) {
            observer.unobserve(entry.target);
          }
        } else if (options.once === false) {
          entry.target.classList.add(hiddenClass);
          entry.target.classList.remove(animationClass);
        }
      } catch (error) {
        handleAnimationError(error, entry.target);
      }
    });
  }

  // SSR-safe: Check for browser environment
  if (typeof window !== 'undefined' && typeof IntersectionObserver !== 'undefined') {
    try {
      // Add hidden class initially
      node.classList.add(hiddenClass);
      
      observer = new IntersectionObserver(handleIntersect, {
        threshold,
        rootMargin
      });

      observer.observe(node);
    } catch (error) {
      handleAnimationError(error, node);
    }
  } else {
    // Fallback for SSR: Don't hide elements, show them immediately
    node.classList.add(animationClass);
  }

  return {
    destroy() {
      try {
        if (observer) {
          observer.disconnect();
        }
      } catch (error) {
        if (handleAnimationError) {
          handleAnimationError(error, node);
        }
      }
    }
  };
}

// Svelte action for stagger animations
export function staggerReveal(node, options = {}) {
  const {
    staggerDelay = 100,
    animationClass = 'animate-in',
    hiddenClass = 'scroll-hidden'
  } = options;

  const children = node.querySelectorAll('[data-stagger]');
  
  // Apply scroll reveal to each child with staggered delay
  const childActions = [];
  children.forEach((child, index) => {
    child.style.animationDelay = `${index * staggerDelay}ms`;
    const action = scrollReveal(child, { ...options, animationClass, hiddenClass });
    childActions.push(action);
  });

  return {
    destroy() {
      childActions.forEach(action => {
        if (action && action.destroy) {
          action.destroy();
        }
      });
    }
  };
}

// Svelte action for parallax effects (SSR-safe)
export function parallax(node, options = {}) {
  const { speed = 0.5, offset = 0 } = options;
  let ticking = false;

  // SSR-safe: Check for browser environment
  if (typeof window === 'undefined') {
    return {
      destroy() {}
    };
  }

  function updatePosition() {
    const scrolled = window.pageYOffset;
    const rate = scrolled * speed * -1;
    node.style.transform = `translateY(${rate + offset}px)`;
    ticking = false;
  }

  function handleScroll() {
    if (!ticking) {
      window.requestAnimationFrame(updatePosition);
      ticking = true;
    }
  }

  window.addEventListener('scroll', handleScroll);
  updatePosition();

  return {
    destroy() {
      window.removeEventListener('scroll', handleScroll);
    }
  };
}

// Initialize animations on elements with data attributes
export function initializeAnimations() {
  // This function is now deprecated - use Svelte actions instead
  console.warn('initializeAnimations() is deprecated. Use Svelte actions instead.');
}
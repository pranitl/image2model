/* =================================================================
   image2model Animation Controller
   JavaScript for advanced animations and interactions
   ================================================================= */

class AnimationController {
    constructor() {
        this.observers = new Map();
        this.animationQueue = [];
        this.isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.animationSettings = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        this.init();
    }
    
    init() {
        // Initialize all animation features
        this.setupIntersectionObservers();
        this.setupScrollAnimations();
        this.setupRippleEffects();
        this.setupParallax();
        this.setupNumberCounters();
        this.setupTextReveals();
        this.bindEventListeners();
        
        // Monitor reduced motion preference changes
        window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
            this.isReducedMotion = e.matches;
            this.updateAnimationState();
        });
    }
    
    /* =================================================================
       Intersection Observer for Scroll Animations
       ================================================================= */
    
    setupIntersectionObservers() {
        // Create observer for reveal animations
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !this.isReducedMotion) {
                    entry.target.classList.add('revealed');
                    
                    // Stagger children animations if applicable
                    const children = entry.target.querySelectorAll('[data-animate-child]');
                    children.forEach((child, index) => {
                        setTimeout(() => {
                            child.classList.add('revealed');
                        }, index * 100);
                    });
                }
            });
        }, this.animationSettings);
        
        // Observe all elements with reveal animations
        document.querySelectorAll('.reveal-on-scroll, [data-animate="on-scroll"]').forEach(el => {
            revealObserver.observe(el);
        });
        
        this.observers.set('reveal', revealObserver);
    }
    
    /* =================================================================
       Scroll-triggered Animations
       ================================================================= */
    
    setupScrollAnimations() {
        let ticking = false;
        
        const updateAnimations = () => {
            const scrollY = window.scrollY;
            const windowHeight = window.innerHeight;
            
            // Parallax elements
            document.querySelectorAll('[data-parallax]').forEach(el => {
                if (!this.isReducedMotion) {
                    const speed = parseFloat(el.dataset.parallax) || 0.5;
                    const yPos = -(scrollY * speed);
                    el.style.transform = `translateY(${yPos}px)`;
                }
            });
            
            // Progress indicators
            document.querySelectorAll('[data-scroll-progress]').forEach(el => {
                const maxScroll = document.documentElement.scrollHeight - windowHeight;
                const progress = (scrollY / maxScroll) * 100;
                el.style.width = `${progress}%`;
            });
            
            ticking = false;
        };
        
        const requestTick = () => {
            if (!ticking) {
                requestAnimationFrame(updateAnimations);
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', requestTick, { passive: true });
    }
    
    /* =================================================================
       Ripple Effect for Buttons
       ================================================================= */
    
    setupRippleEffects() {
        document.addEventListener('click', (e) => {
            const button = e.target.closest('.ripple, [data-ripple]');
            if (!button || this.isReducedMotion) return;
            
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            button.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    }
    
    /* =================================================================
       Parallax Effects
       ================================================================= */
    
    setupParallax() {
        // Enhanced parallax with mouse movement
        document.addEventListener('mousemove', (e) => {
            if (this.isReducedMotion) return;
            
            const mouseX = e.clientX / window.innerWidth - 0.5;
            const mouseY = e.clientY / window.innerHeight - 0.5;
            
            document.querySelectorAll('[data-parallax-mouse]').forEach(el => {
                const speed = parseFloat(el.dataset.parallaxMouse) || 1;
                const x = mouseX * speed * 50;
                const y = mouseY * speed * 50;
                
                el.style.transform = `translate(${x}px, ${y}px)`;
            });
        });
    }
    
    /* =================================================================
       Number Counter Animations
       ================================================================= */
    
    setupNumberCounters() {
        const animateNumber = (el) => {
            const final = parseInt(el.dataset.countTo) || 0;
            const duration = parseInt(el.dataset.countDuration) || 2000;
            const start = 0;
            const increment = final / (duration / 16);
            let current = start;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= final) {
                    current = final;
                    clearInterval(timer);
                }
                el.textContent = Math.floor(current).toLocaleString();
            }, 16);
        };
        
        // Create observer for number counters
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.dataset.counted && !this.isReducedMotion) {
                    entry.target.dataset.counted = 'true';
                    animateNumber(entry.target);
                }
            });
        }, this.animationSettings);
        
        document.querySelectorAll('[data-count-to]').forEach(el => {
            counterObserver.observe(el);
        });
        
        this.observers.set('counter', counterObserver);
    }
    
    /* =================================================================
       Text Reveal Animations
       ================================================================= */
    
    setupTextReveals() {
        document.querySelectorAll('[data-text-reveal]').forEach(el => {
            const text = el.textContent;
            el.textContent = '';
            
            // Split text into spans
            text.split('').forEach((char, i) => {
                const span = document.createElement('span');
                span.textContent = char === ' ' ? '\u00A0' : char;
                span.style.setProperty('--i', i);
                span.style.animationDelay = `${i * 50}ms`;
                el.appendChild(span);
            });
        });
    }
    
    /* =================================================================
       Animation Utilities
       ================================================================= */
    
    // Animate element with specific animation
    animate(element, animationName, options = {}) {
        const {
            duration = 'var(--duration-medium)',
            delay = '0ms',
            easing = 'var(--ease-out-cubic)',
            fillMode = 'both',
            onComplete = null
        } = options;
        
        if (this.isReducedMotion && !options.essential) {
            if (onComplete) onComplete();
            return;
        }
        
        element.style.animation = `${animationName} ${duration} ${easing} ${delay} ${fillMode}`;
        
        if (onComplete) {
            element.addEventListener('animationend', onComplete, { once: true });
        }
    }
    
    // Queue animations
    queue(animations) {
        animations.forEach((anim, index) => {
            setTimeout(() => {
                this.animate(anim.element, anim.name, anim.options);
            }, index * (anim.stagger || 100));
        });
    }
    
    // Add animation classes with automatic cleanup
    addAnimationClass(element, className, duration = 1000) {
        element.classList.add(className);
        element.classList.add('will-animate');
        
        setTimeout(() => {
            element.classList.remove(className);
            element.classList.remove('will-animate');
            element.classList.add('animation-done');
        }, duration);
    }
    
    /* =================================================================
       Event Listeners
       ================================================================= */
    
    bindEventListeners() {
        // 3D Tilt Effect for cards
        document.addEventListener('mousemove', (e) => {
            const tiltElements = document.querySelectorAll('.card-tilt');
            tiltElements.forEach(element => {
                const rect = element.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = ((y - centerY) / centerY) * -10;
                const rotateY = ((x - centerX) / centerX) * 10;
                
                element.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
            });
        });
        
        // Reset tilt on mouse leave
        document.addEventListener('mouseleave', (e) => {
            if (e.target.matches('.card-tilt')) {
                e.target.style.transform = '';
            }
        }, true);
        
        // Hover animations
        document.addEventListener('mouseenter', (e) => {
            if (e.target.matches('[data-hover-animation]')) {
                const animation = e.target.dataset.hoverAnimation;
                this.addAnimationClass(e.target, animation);
            }
        }, true);
        
        // Click animations
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-click-animation]')) {
                const animation = e.target.dataset.clickAnimation;
                this.addAnimationClass(e.target, animation, 500);
            }
        });
        
        // Form validation animations
        document.addEventListener('invalid', (e) => {
            e.preventDefault();
            this.addAnimationClass(e.target, 'form-shake', 500);
        }, true);
        
        // Success animations
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.checkValidity()) {
                const button = form.querySelector('[type="submit"]');
                if (button) {
                    this.addAnimationClass(button, 'form-success', 1000);
                }
            }
        });
    }
    
    /* =================================================================
       Animation State Management
       ================================================================= */
    
    updateAnimationState() {
        if (this.isReducedMotion) {
            document.documentElement.setAttribute('data-reduce-motion', 'true');
            this.pauseAllAnimations();
        } else {
            document.documentElement.setAttribute('data-reduce-motion', 'false');
            this.resumeAllAnimations();
        }
    }
    
    pauseAllAnimations() {
        document.querySelectorAll('[class*="animate-"]').forEach(el => {
            el.classList.add('animation-paused');
        });
    }
    
    resumeAllAnimations() {
        document.querySelectorAll('.animation-paused').forEach(el => {
            el.classList.remove('animation-paused');
        });
    }
    
    // Clean up observers
    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
    }
}

/* =================================================================
   Page Transition Manager
   ================================================================= */

class PageTransitionManager {
    constructor() {
        this.transitioning = false;
        this.init();
    }
    
    init() {
        // Intercept navigation for smooth transitions
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href^="/"], a[href^="./"], a[href^="../"]');
            if (link && !link.target && !this.transitioning) {
                e.preventDefault();
                this.transition(link.href);
            }
        });
        
        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.transition(window.location.href, false);
        });
    }
    
    async transition(url, pushState = true) {
        if (this.transitioning) return;
        this.transitioning = true;
        
        // Fade out current content
        document.body.classList.add('page-transition-out');
        
        await this.wait(300);
        
        // Load new content
        try {
            const response = await fetch(url);
            const html = await response.text();
            
            // Parse and update content
            const parser = new DOMParser();
            const newDoc = parser.parseFromString(html, 'text/html');
            
            // Update main content
            const mainContent = document.querySelector('main, .main-content, body');
            const newContent = newDoc.querySelector('main, .main-content, body');
            
            if (mainContent && newContent) {
                mainContent.innerHTML = newContent.innerHTML;
            }
            
            // Update title
            document.title = newDoc.title;
            
            // Update URL
            if (pushState) {
                history.pushState({}, '', url);
            }
            
            // Fade in new content
            document.body.classList.remove('page-transition-out');
            document.body.classList.add('page-transition-in');
            
            // Reinitialize animations for new content
            window.animationController.init();
            
        } catch (error) {
            console.error('Page transition failed:', error);
            window.location.href = url;
        }
        
        this.transitioning = false;
    }
    
    wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

/* =================================================================
   Initialize on DOM Ready
   ================================================================= */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize animation controller
    window.animationController = new AnimationController();
    
    // Initialize page transitions (optional)
    if (document.body.dataset.enablePageTransitions === 'true') {
        window.pageTransitionManager = new PageTransitionManager();
    }
    
    // Add loaded class for initial animations
    document.body.classList.add('animations-loaded');
});

/* =================================================================
   Export for use in other modules
   ================================================================= */

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AnimationController, PageTransitionManager };
}
# Animation Accessibility Guide

## Overview
This guide ensures that the image2model animation system is accessible to all users, including those with motion sensitivities, visual impairments, or who use assistive technologies.

## Key Principles

### 1. Respect User Preferences
- Always honor `prefers-reduced-motion` settings
- Provide user controls to disable animations
- Ensure functionality without animations

### 2. Maintain Usability
- Never rely solely on animation to convey information
- Preserve keyboard navigation
- Keep focus indicators visible

### 3. Performance for All
- Optimize for low-end devices
- Reduce animations on mobile
- Provide fallbacks

## Implementation Guidelines

### Reduced Motion Support

#### CSS Implementation
```css
/* Standard animation */
.animate-element {
    animation: slideIn 0.3s ease-out;
    transition: transform 0.3s ease-out;
}

/* Reduced motion version */
@media (prefers-reduced-motion: reduce) {
    .animate-element {
        animation: none;
        transition: opacity 0.1s ease-out;
    }
}
```

#### JavaScript Detection
```javascript
// Check user preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Apply appropriate animation
if (!prefersReducedMotion) {
    element.classList.add('animate-fade-in');
} else {
    element.classList.add('simple-appear');
}
```

### Essential vs Decorative Animations

#### Essential Animations
These convey important state changes and should have reduced alternatives:
```css
/* Loading state - essential */
.loading {
    /* Full animation */
    animation: spin 1s linear infinite;
}

@media (prefers-reduced-motion: reduce) {
    .loading {
        /* Simple pulse instead of spin */
        animation: pulse 2s ease-in-out infinite;
    }
}
```

#### Decorative Animations
These can be completely removed when reduced motion is preferred:
```css
/* Decorative float effect */
.decorative-float {
    animation: float 3s ease-in-out infinite;
}

@media (prefers-reduced-motion: reduce) {
    .decorative-float {
        animation: none;
    }
}
```

### Focus Management

#### Visible Focus States
```css
/* Ensure focus is always visible */
.btn:focus-visible {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
    /* Don't rely on animation alone */
    box-shadow: 0 0 0 3px rgba(93, 173, 226, 0.3);
}

/* Enhanced focus for animated elements */
.animate-element:focus {
    animation-play-state: paused;
    outline: 3px solid var(--accent-primary);
}
```

#### Focus Trapping
```javascript
// Pause animations when element is focused
element.addEventListener('focus', () => {
    element.classList.add('animation-paused');
});

element.addEventListener('blur', () => {
    element.classList.remove('animation-paused');
});
```

### Screen Reader Compatibility

#### Loading States
```html
<!-- Announce loading state -->
<div class="loading-spinner" role="status" aria-live="polite">
    <span class="sr-only">Loading content, please wait...</span>
</div>

<!-- Announce completion -->
<div role="status" aria-live="polite" aria-atomic="true">
    <span class="sr-only">Content loaded successfully</span>
</div>
```

#### Progress Indicators
```html
<!-- Accessible progress bar -->
<div class="progress-bar" 
     role="progressbar" 
     aria-valuenow="60" 
     aria-valuemin="0" 
     aria-valuemax="100"
     aria-label="Upload progress">
    <div class="progress-bar-fill" style="width: 60%"></div>
</div>
```

#### State Changes
```html
<!-- Announce state changes -->
<button class="btn" 
        aria-pressed="false"
        aria-live="polite">
    <span class="btn-text">Subscribe</span>
    <span class="sr-only" aria-live="polite"></span>
</button>

<script>
// Update ARIA attributes with state
button.addEventListener('click', () => {
    const isPressed = button.getAttribute('aria-pressed') === 'true';
    button.setAttribute('aria-pressed', !isPressed);
    
    // Announce change
    const announcement = button.querySelector('.sr-only');
    announcement.textContent = isPressed ? 'Unsubscribed' : 'Subscribed';
});
</script>
```

### Keyboard Navigation

#### Maintaining Tab Order
```css
/* Don't affect tab order with animations */
.animate-slide-in {
    /* Use transform instead of position changes */
    transform: translateX(-100%);
    transition: transform 0.3s ease-out;
}

.animate-slide-in.active {
    transform: translateX(0);
}
```

#### Keyboard Triggers
```javascript
// Support both click and keyboard activation
element.addEventListener('click', handleActivation);
element.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleActivation(e);
    }
});
```

### Color and Contrast

#### High Contrast Mode
```css
/* Ensure animations work in high contrast */
@media (prefers-contrast: high) {
    .animate-element {
        /* Use border instead of shadow */
        border: 2px solid;
    }
    
    /* Increase focus indicators */
    .btn:focus {
        outline-width: 3px;
        outline-offset: 3px;
    }
}
```

#### Color Independence
```css
/* Don't rely on color alone */
.status-indicator {
    /* Add icon or text in addition to color */
    &::before {
        content: '✓';
        display: inline-block;
        margin-right: 0.5em;
    }
    
    &.error::before {
        content: '✗';
    }
}
```

### Timing Considerations

#### Sufficient Time
```css
/* Allow enough time to read/perceive */
.notification {
    animation: slideIn 0.3s ease-out,
               stay 5s linear 0.3s,
               slideOut 0.3s ease-out 5.3s;
}

/* Pause on hover/focus */
.notification:hover,
.notification:focus-within {
    animation-play-state: paused;
}
```

#### User Control
```html
<!-- Allow users to pause animations -->
<button class="animation-control" 
        aria-label="Pause animations"
        aria-pressed="false">
    <svg><!-- Pause icon --></svg>
</button>

<script>
const toggleAnimations = (button) => {
    const isPaused = button.getAttribute('aria-pressed') === 'true';
    
    if (isPaused) {
        document.body.classList.remove('animations-paused');
        button.setAttribute('aria-pressed', 'false');
        button.setAttribute('aria-label', 'Pause animations');
    } else {
        document.body.classList.add('animations-paused');
        button.setAttribute('aria-pressed', 'true');
        button.setAttribute('aria-label', 'Play animations');
    }
};
</script>
```

### Testing Checklist

#### Motion Sensitivity
- [ ] Test with `prefers-reduced-motion: reduce`
- [ ] Ensure no motion sickness triggers
- [ ] Verify essential animations have alternatives
- [ ] Check that decorative animations can be disabled

#### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Verify focus indicators remain visible
- [ ] Test animation triggers with keyboard
- [ ] Ensure no keyboard traps

#### Screen Readers
- [ ] Test with NVDA/JAWS (Windows)
- [ ] Test with VoiceOver (macOS/iOS)
- [ ] Verify state changes are announced
- [ ] Check loading states are communicated

#### Visual Accessibility
- [ ] Test with Windows High Contrast mode
- [ ] Verify sufficient color contrast
- [ ] Check animations work without color
- [ ] Test with browser zoom at 200%

### Implementation Examples

#### Accessible Loading Button
```html
<button class="btn btn-primary" 
        aria-busy="false"
        aria-live="polite">
    <span class="btn-text">Save Changes</span>
    <span class="btn-spinner" aria-hidden="true"></span>
    <span class="sr-only"></span>
</button>

<style>
.btn[aria-busy="true"] .btn-text {
    visibility: hidden;
}

.btn[aria-busy="true"] .btn-spinner {
    display: inline-block;
    animation: spin 1s linear infinite;
}

@media (prefers-reduced-motion: reduce) {
    .btn[aria-busy="true"] .btn-spinner {
        animation: pulse 2s ease-in-out infinite;
    }
}
</style>

<script>
async function saveChanges(button) {
    // Set loading state
    button.setAttribute('aria-busy', 'true');
    button.querySelector('.sr-only').textContent = 'Saving changes...';
    
    try {
        await performSave();
        button.querySelector('.sr-only').textContent = 'Changes saved successfully';
    } catch (error) {
        button.querySelector('.sr-only').textContent = 'Error saving changes';
    } finally {
        button.setAttribute('aria-busy', 'false');
    }
}
</script>
```

#### Accessible Card Animation
```html
<article class="card card-animated"
         role="article"
         tabindex="0"
         aria-label="Product card">
    <img src="product.jpg" alt="Product description">
    <h3>Product Name</h3>
    <p>Product details...</p>
    <button class="btn">View Details</button>
</article>

<style>
.card-animated {
    transition: transform 0.3s ease-out,
                box-shadow 0.3s ease-out;
}

.card-animated:hover,
.card-animated:focus-within {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

@media (prefers-reduced-motion: reduce) {
    .card-animated {
        transition: box-shadow 0.1s ease-out;
    }
    
    .card-animated:hover,
    .card-animated:focus-within {
        transform: none;
        box-shadow: 0 0 0 3px var(--accent-primary);
    }
}
</style>
```

### Resources

#### Testing Tools
- **axe DevTools**: Browser extension for accessibility testing
- **WAVE**: Web Accessibility Evaluation Tool
- **Lighthouse**: Chrome DevTools accessibility audit
- **Screen Readers**: NVDA (free), JAWS, VoiceOver

#### References
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [Prefers Reduced Motion Guide](https://web.dev/prefers-reduced-motion/)
- [Animation Performance Best Practices](https://web.dev/animations/)

### Summary

Making animations accessible means:
1. **Respecting user preferences** for reduced motion
2. **Providing alternatives** for essential animations
3. **Maintaining usability** without animations
4. **Ensuring compatibility** with assistive technologies
5. **Testing thoroughly** with real users and tools

Remember: An accessible animation system enhances the experience for all users, not just those with disabilities.
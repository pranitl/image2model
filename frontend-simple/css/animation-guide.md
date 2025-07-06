# image2model Animation and Interaction Design System

## Overview
The image2model Animation System provides a comprehensive set of animations, transitions, and micro-interactions that bring the brand's low-poly, geometric aesthetic to life through motion.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Animation Philosophy](#animation-philosophy)
3. [Core Files](#core-files)
4. [Animation Categories](#animation-categories)
5. [Usage Examples](#usage-examples)
6. [Performance Guidelines](#performance-guidelines)
7. [Accessibility](#accessibility)
8. [Browser Support](#browser-support)

## Getting Started

### Include the Animation System
```html
<!-- Core animation definitions -->
<link rel="stylesheet" href="css/animations.css">
<link rel="stylesheet" href="css/animation-utilities.css">

<!-- Component-specific animations -->
<link rel="stylesheet" href="css/button-animations.css">
<link rel="stylesheet" href="css/card-animations.css">
<link rel="stylesheet" href="css/form-animations.css">
<link rel="stylesheet" href="css/loading-animations.css">
<link rel="stylesheet" href="css/special-effects.css">

<!-- JavaScript controller -->
<script src="js/animations.js"></script>
```

### Quick Start
```html
<!-- Fade in animation -->
<div class="animate-fade-in">
    Content fades in
</div>

<!-- Hover lift effect -->
<button class="btn btn-primary hover-lift">
    Hover to lift
</button>

<!-- Loading spinner -->
<div class="spinner-triangle"></div>
```

## Animation Philosophy

Our animation system follows these principles:
- **Smooth & Mathematical**: Animations use carefully crafted easing curves
- **Geometric Transformations**: Reflect the low-poly brand identity
- **Subtle Depth**: Use shadows and layers to create depth
- **Progressive Disclosure**: Reveal information thoughtfully
- **Performance First**: All animations are GPU-accelerated

## Core Files

### 1. animations.css
Core keyframe definitions and timing functions:
- Standard easing curves (cubic-bezier functions)
- Duration presets (micro, short, medium, long)
- Base keyframe animations
- Performance optimizations

### 2. animation-utilities.css
Ready-to-use utility classes:
- Entrance animations (`animate-fade-in`, `animate-slide-up`)
- Hover effects (`hover-lift`, `hover-scale`, `hover-glow`)
- Loading states (`loading-spinner`, `loading-skeleton`)
- Transition utilities

### 3. Component-Specific Files
- **button-animations.css**: Button interactions and states
- **card-animations.css**: Card hover effects and transitions
- **form-animations.css**: Form field interactions and validation
- **loading-animations.css**: Spinners, progress bars, skeletons
- **special-effects.css**: Parallax, gradients, 3D effects

### 4. animations.js
JavaScript controller for advanced animations:
- Intersection Observer for scroll animations
- Parallax effects
- Number counters
- Page transitions
- Animation state management

## Animation Categories

### 1. Entrance Animations
```html
<!-- Fade animations -->
<div class="animate-fade-in">Fades in</div>
<div class="animate-fade-in-up">Fades in from below</div>
<div class="animate-fade-in-scale">Fades in with scale</div>

<!-- Slide animations -->
<div class="animate-slide-in-left">Slides from left</div>
<div class="animate-slide-in-right">Slides from right</div>

<!-- With delays -->
<div class="animate-fade-in delay-200">Delayed fade</div>
```

### 2. Hover Effects

#### Buttons
```html
<!-- Lift effect with shadow -->
<button class="btn btn-primary hover-lift">
    Lifts on hover
</button>

<!-- Scale with glow -->
<button class="btn btn-secondary hover-scale hover-glow">
    Scales and glows
</button>

<!-- 3D effect -->
<button class="btn btn-3d">
    3D perspective
</button>
```

#### Cards
```html
<!-- Card with tilt effect -->
<div class="card card-tilt">
    <h3>3D Tilt Card</h3>
    <p>Tilts on hover</p>
</div>

<!-- Card with image zoom -->
<div class="card card-image-zoom">
    <img src="image.jpg" alt="Zooms on hover">
</div>

<!-- Card with gradient border -->
<div class="card card-gradient-border">
    Animated gradient border
</div>
```

#### Links
```html
<!-- Animated underline -->
<a href="#" class="link-animated">
    Underline slides in
</a>

<!-- Glow effect -->
<a href="#" class="link-glow">
    Glows on hover
</a>
```

### 3. Loading Animations

#### Spinners
```html
<!-- Triangle spinner (brand aesthetic) -->
<div class="spinner-triangle"></div>

<!-- Cube spinner -->
<div class="spinner-cube"></div>

<!-- Hexagon spinner -->
<div class="spinner-hexagon"></div>

<!-- Simple spinner -->
<div class="loading-spinner"></div>
```

#### Progress Bars
```html
<!-- Gradient progress bar -->
<div class="progress-bar">
    <div class="progress-bar-fill" style="width: 60%"></div>
</div>

<!-- Striped animated progress -->
<div class="progress-bar progress-striped">
    <div class="progress-bar-fill" style="width: 75%"></div>
</div>

<!-- Segmented progress -->
<div class="progress-segmented">
    <div class="progress-segment active"></div>
    <div class="progress-segment active"></div>
    <div class="progress-segment"></div>
</div>
```

#### Skeleton Screens
```html
<!-- Card skeleton -->
<div class="skeleton-card">
    <div class="skeleton skeleton-image"></div>
    <div class="skeleton skeleton-title"></div>
    <div class="skeleton skeleton-text"></div>
    <div class="skeleton skeleton-text" style="width: 80%"></div>
</div>
```

### 4. Form Interactions

#### Input Fields
```html
<!-- Floating label -->
<div class="form-field">
    <input type="text" class="form-field-input" placeholder=" ">
    <label class="form-field-label">Email</label>
</div>

<!-- Input with icon -->
<div class="input-icon-wrapper">
    <input type="text" class="input" placeholder="Search...">
    <i class="input-icon">🔍</i>
</div>

<!-- Validation states -->
<input type="email" class="input is-valid">
<input type="text" class="input is-invalid">
```

#### Custom Controls
```html
<!-- Animated checkbox -->
<label class="checkbox">
    <input type="checkbox" class="checkbox-input">
    <span class="checkbox-box">
        <span class="checkbox-checkmark">✓</span>
    </span>
    <span>Remember me</span>
</label>

<!-- Toggle switch -->
<label class="toggle">
    <input type="checkbox" class="toggle-input">
    <span class="toggle-slider">
        <span class="toggle-knob"></span>
    </span>
</label>
```

### 5. Micro-interactions

#### Ripple Effect
```html
<button class="btn ripple" data-ripple>
    Click for ripple
</button>
```

#### Form Feedback
```html
<!-- Shake on error -->
<form>
    <input type="email" required class="input">
    <button type="submit" class="btn">Submit</button>
</form>

<!-- Success animation -->
<button class="btn form-success">
    Shows checkmark on success
</button>
```

### 6. Special Effects

#### Parallax
```html
<!-- Scroll parallax -->
<div class="parallax" data-parallax="0.5">
    Moves slower than scroll
</div>

<!-- Mouse parallax -->
<div class="parallax-mouse" data-parallax-mouse="1">
    Follows mouse movement
</div>
```

#### Gradient Animations
```html
<!-- Animated gradient background -->
<div class="gradient-animated">
    Shifting gradient colors
</div>

<!-- Gradient text -->
<h1 class="gradient-text">
    Animated gradient text
</h1>
```

#### Shape Morphing
```html
<!-- Blob animation -->
<div class="blob">
    Morphing blob shape
</div>

<!-- Geometric morph -->
<div class="shape-morph">
    Morphing between shapes
</div>
```

#### 3D Effects
```html
<!-- 3D card flip -->
<div class="flip-container">
    <div class="flip-card">
        <div class="flip-front">Front</div>
        <div class="flip-back">Back</div>
    </div>
</div>

<!-- 3D cube -->
<div class="cube-container">
    <div class="cube">
        <div class="cube-face"></div>
        <div class="cube-face"></div>
        <div class="cube-face"></div>
        <div class="cube-face"></div>
        <div class="cube-face"></div>
        <div class="cube-face"></div>
    </div>
</div>
```

## JavaScript Integration

### Scroll Animations
```html
<!-- Elements animate when scrolled into view -->
<div class="reveal-on-scroll">
    Fades in on scroll
</div>

<div data-animate="on-scroll" class="animate-fade-in-up">
    Custom scroll animation
</div>
```

### Number Counters
```html
<!-- Counts up to value when visible -->
<span data-count-to="1000" data-count-duration="2000">0</span>
```

### Text Reveals
```html
<!-- Letters animate in sequence -->
<h2 data-text-reveal>Animated Text</h2>
```

### Page Transitions
```html
<!-- Enable smooth page transitions -->
<body data-enable-page-transitions="true">
    <!-- Page content -->
</body>
```

## Performance Guidelines

### 1. Use GPU-Accelerated Properties
```css
/* Good - GPU accelerated */
transform: translateX(100px);
opacity: 0.5;

/* Avoid - CPU intensive */
left: 100px;
width: 200px;
```

### 2. Add Will-Change for Complex Animations
```html
<div class="will-animate">
    Complex animation
</div>
```

### 3. Clean Up After Animations
```javascript
// Animations automatically clean up
element.classList.add('animation-done');
```

### 4. Batch Animations
```javascript
// Queue multiple animations
animationController.queue([
    { element: el1, name: 'fadeIn', options: { delay: '0ms' } },
    { element: el2, name: 'fadeIn', options: { delay: '100ms' } },
    { element: el3, name: 'fadeIn', options: { delay: '200ms' } }
]);
```

## Accessibility

### 1. Respect Reduced Motion
The system automatically detects and respects `prefers-reduced-motion`:
```css
/* Animations are disabled or simplified when reduced motion is preferred */
@media (prefers-reduced-motion: reduce) {
    /* Simplified animations */
}
```

### 2. Provide Controls
```html
<!-- Animation toggle for users -->
<button onclick="animationController.updateAnimationState()">
    Toggle Animations
</button>
```

### 3. Keyboard Navigation
All interactive elements maintain keyboard accessibility:
- Focus states are preserved
- Tab order is maintained
- Screen reader announcements work correctly

### 4. ARIA Attributes
```html
<!-- Loading states -->
<div class="loading-spinner" role="status" aria-label="Loading">
    <span class="loading-text">Loading content...</span>
</div>
```

## Browser Support

### Supported Browsers
- Chrome/Edge 88+
- Firefox 78+
- Safari 14+
- iOS Safari 14+
- Chrome Android 88+

### Fallbacks
- CSS animations fall back to instant transitions
- JavaScript enhancements are progressive
- Core functionality works without animations

## Best Practices

### 1. Choose Appropriate Animations
- Use subtle animations for frequent interactions
- Reserve complex animations for special moments
- Match animation personality to brand identity

### 2. Maintain Consistency
- Use the same easing curves across similar elements
- Keep animation durations consistent
- Follow the established animation patterns

### 3. Test Performance
- Test on low-end devices
- Monitor frame rates (target 60fps)
- Use browser DevTools performance tab

### 4. Progressive Enhancement
```html
<!-- Base state works without animations -->
<div class="card">
    <!-- Enhanced with animations when available -->
    <script>
        if (window.animationController) {
            card.classList.add('card-tilt');
        }
    </script>
</div>
```

## Troubleshooting

### Animations Not Working
1. Check if CSS files are loaded
2. Verify JavaScript is initialized
3. Check browser console for errors
4. Ensure reduced motion is not enabled

### Performance Issues
1. Reduce number of animated elements
2. Use `will-change` sparingly
3. Disable complex animations on mobile
4. Check for animation loops

### Accessibility Issues
1. Test with keyboard navigation
2. Enable reduced motion preference
3. Use screen reader to verify
4. Check focus states

---

For more information or to report issues, please refer to the main project documentation.
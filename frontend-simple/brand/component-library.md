# image2model Component Library

## Navigation Components

### Navbar
```html
<nav class="navbar animate-fade-in">
    <div class="navbar-container">
        <a href="/" class="navbar-brand">
            <img src="assets/logo-cropped.png" alt="image2model" class="nav-logo" width="48" height="48" loading="eager">
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
            <li><a href="upload.html" class="btn btn-primary btn-sm">Start Creating</a></li>
        </ul>
    </div>
</nav>
```

### Footer
```html
<footer class="site-footer">
    <div class="footer-container">
        <div class="footer-content">
            <div class="footer-brand">
                <img src="assets/logo-cropped.png" alt="image2model" width="64" height="64" class="footer-logo">
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
```

## Hero Components

### Hero Section with Animated Logo
```html
<section class="hero gradient-cool-ocean">
    <div class="geometric-pattern"></div>
    <div class="container">
        <div class="hero-content animate-fade-in">
            <div class="hero-logo-animated animate-float">
                <img src="assets/logo-cropped.png" alt="image2model" width="150" height="150" class="hero-logo" loading="eager">
            </div>
            <h1 class="display gradient-text-blue animate-gradient">Transform Images Into 3D Models</h1>
            <p class="hero-description lead animate-fade-in-up delay-200">
                Turn your photos into professional 3D models instantly. No expertise required - just upload and let our AI work its magic.
            </p>
            <div class="hero-cta animate-fade-in-scale delay-400">
                <a href="upload.html" class="btn btn-primary btn-lg hover-lift">
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L11 6.414V13a1 1 0 11-2 0V6.414L7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3z"/>
                        <path d="M3 11a1 1 0 011 1v3a1 1 0 001 1h10a1 1 0 001-1v-3a1 1 0 112 0v3a3 3 0 01-3 3H5a3 3 0 01-3-3v-3a1 1 0 011-1z"/>
                    </svg>
                    Start Creating Now
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
```

## Section Components

### Section Header
```html
<div class="section-header">
    <h2 class="section-title animate-fade-in">Section Title Here</h2>
    <p class="section-subtitle text-secondary animate-fade-in-up delay-200">
        Subtitle text that provides context
    </p>
</div>
```

## Card Components

### Feature Card
```html
<div class="feature-card card card-hover reveal-on-scroll">
    <div class="feature-icon gradient-blue-medium">
        <svg width="32" height="32" fill="currentColor" viewBox="0 0 20 20">
            <!-- Icon path here -->
        </svg>
    </div>
    <h3 class="feature-title">Feature Title</h3>
    <p class="feature-description">Feature description text goes here.</p>
</div>
```

### Step Card
```html
<div class="step card card-lift reveal-on-scroll">
    <div class="step-icon gradient-blue-medium">
        <svg width="48" height="48" fill="currentColor" viewBox="0 0 20 20">
            <!-- Icon path here -->
        </svg>
    </div>
    <h3 class="step-title">Step Title</h3>
    <p class="step-description">Step description text</p>
</div>
```

### Example Card with Gallery
```html
<div class="example-card reveal-on-scroll">
    <div class="example-content">
        <div class="example-gallery">
            <div class="example-image-wrapper">
                <img src="path/to/before.jpg" alt="Description" class="example-image" loading="lazy">
                <span class="example-label">Original Photo</span>
            </div>
            <div class="example-image-wrapper">
                <img src="path/to/after.webp" alt="Description" class="example-image" loading="lazy">
                <span class="example-label">3D Model</span>
            </div>
        </div>
        <div class="example-info">
            <h3 class="example-title">Example Title</h3>
            <p class="example-description">Description of the transformation.</p>
            <a href="upload.html" class="btn btn-secondary btn-sm">Try with this image</a>
        </div>
    </div>
</div>
```

## Button Components

### Primary Button
```html
<a href="#" class="btn btn-primary">Button Text</a>
<a href="#" class="btn btn-primary btn-sm">Small Button</a>
<a href="#" class="btn btn-primary btn-lg">Large Button</a>
```

### Secondary Button
```html
<a href="#" class="btn btn-secondary">Secondary Button</a>
```

### Button with Icon
```html
<a href="#" class="btn btn-primary">
    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
        <!-- Icon SVG -->
    </svg>
    Button Text
</a>
```

## CTA Section
```html
<section class="cta-section">
    <div class="container">
        <div class="cta-content">
            <h2 class="cta-title gradient-text-blue animate-fade-in">Ready to Transform Your Images?</h2>
            <p class="cta-description animate-fade-in-up delay-200">
                Join thousands of creators who are already making amazing 3D models.
            </p>
            <div class="cta-buttons animate-fade-in-scale delay-400">
                <a href="upload.html" class="btn btn-primary btn-lg hover-lift">
                    Start Creating Now
                    <svg width="20" height="20" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </a>
            </div>
        </div>
    </div>
</section>
```

## Grid Layouts

### Feature Grid (2 columns)
```html
<div class="features-grid">
    <!-- Feature cards go here -->
</div>
```

### Steps Grid (3 columns)
```html
<div class="steps">
    <!-- Step cards go here -->
</div>
```

### Examples Grid
```html
<div class="examples-grid">
    <!-- Example cards go here -->
</div>
```

## Utility Classes

### Animation Classes
- `animate-fade-in`
- `animate-fade-in-up`
- `animate-fade-in-scale`
- `animate-float`
- `animate-gradient`
- `reveal-on-scroll`
- `delay-200`
- `delay-400`
- `delay-600`
- `delay-stagger`

### Text Classes
- `text-secondary`
- `text-muted`
- `gradient-text-blue`

### Background Classes
- `gradient-cool-ocean`
- `gradient-blue-medium`

### Interactive Classes
- `hover-lift`
- `card-hover`
- `card-lift`
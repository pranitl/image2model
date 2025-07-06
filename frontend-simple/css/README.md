# CSS Color System Documentation

## Overview

The image2model CSS color system is built on the brand guidelines and provides a comprehensive, accessible color palette for both light and dark modes.

## File Structure

```
css/
├── variables.css          # Core CSS custom properties and color definitions
├── color-utilities.css    # Utility classes for colors
├── color-accessibility.md # WCAG compliance guidelines
├── style.css             # Main stylesheet (imports variables and utilities)
└── README.md             # This file
```

## Usage

### 1. Import Order

The color system is automatically imported in `style.css`:

```css
@import url('variables.css');
@import url('color-utilities.css');
```

### 2. Using CSS Variables

```css
/* Background colors */
.my-element {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    border-color: var(--border-color);
}

/* Brand colors */
.brand-element {
    background-color: var(--brand-vibrant-red);
    color: var(--brand-white);
}

/* Semantic colors */
.success-message {
    background-color: var(--status-success-bg);
    color: var(--status-success-text);
    border: 1px solid var(--status-success-border);
}
```

### 3. Using Utility Classes

```html
<!-- Background utilities -->
<div class="bg-primary text-white">Primary background</div>
<div class="bg-gradient-warm-sunset">Gradient background</div>

<!-- Text utilities -->
<p class="text-primary">Primary text color</p>
<h1 class="text-gradient-primary">Gradient text</h1>

<!-- Status utilities -->
<div class="alert-success">Success message</div>
<div class="alert-error">Error message</div>
```

## Color Palette

### Brand Primary Colors
- **Dark Charcoal** (#3A424A) - Primary text, headers
- **Vibrant Red** (#E74C3C) - Primary actions, CTAs
- **Sky Blue** (#3498DB) - Secondary actions, links
- **Bright Cyan** (#5DADE2) - Highlights, accents
- **Sunset Orange** (#E67E22) - Warnings, special elements
- **Golden Yellow** (#F39C12) - Accent, achievements

### Semantic Colors
- **Primary**: Vibrant Red
- **Secondary**: Sky Blue
- **Accent**: Golden Yellow
- **Success**: #27AE60
- **Warning**: Golden Yellow
- **Error**: Vibrant Red
- **Info**: Sky Blue

## Dark Mode

The color system automatically switches to dark mode based on system preferences:

```css
@media (prefers-color-scheme: dark) {
    /* Dark mode colors are automatically applied */
}
```

To force dark or light mode:

```html
<body class="dark-mode">  <!-- Force dark mode -->
<body class="light-mode"> <!-- Force light mode -->
```

## Gradients

Pre-defined gradients are available:

```css
/* Linear gradients */
var(--gradient-warm-sunset)    /* Yellow to Red */
var(--gradient-cool-ocean)     /* Cyan to Blue */
var(--gradient-mountain-mist)  /* Light to Medium Gray */
var(--gradient-tech-fusion)    /* Blue to Cyan to Charcoal */
var(--gradient-creative-burst) /* Multi-color gradient */

/* Text gradients */
var(--gradient-text-primary)   /* Yellow to Red text */
var(--gradient-text-secondary) /* Cyan to Blue text */
```

## Accessibility

All color combinations follow WCAG 2.1 AA standards:

- **Normal text**: Minimum 4.5:1 contrast ratio
- **Large text**: Minimum 3:1 contrast ratio

See `color-accessibility.md` for detailed compliance information.

## Shadows

Brand-colored shadows are available:

```css
var(--shadow-sm)     /* Small neutral shadow */
var(--shadow-md)     /* Medium neutral shadow */
var(--shadow-lg)     /* Large neutral shadow */
var(--shadow-xl)     /* Extra large neutral shadow */
var(--shadow-red)    /* Red-tinted shadow */
var(--shadow-blue)   /* Blue-tinted shadow */
var(--shadow-yellow) /* Yellow-tinted shadow */
```

## Migration Guide

To update existing styles:

1. Replace hardcoded colors with CSS variables
2. Update `#5865F2` → `var(--brand-vibrant-red)`
3. Update `#0a0a0a` → `var(--bg-primary)`
4. Update `rgba()` colors with status variables

## Best Practices

1. **Always use CSS variables** instead of hardcoded colors
2. **Test in both light and dark modes**
3. **Check contrast ratios** when creating new color combinations
4. **Use semantic variables** (e.g., `--color-primary`) over specific colors
5. **Apply gradients sparingly** for visual hierarchy

## Browser Support

- Modern browsers with CSS custom properties support
- Fallbacks included for older browsers
- Tested on Chrome, Firefox, Safari, and Edge
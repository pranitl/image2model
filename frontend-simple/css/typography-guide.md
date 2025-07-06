# Typography System Guide

## Overview

The image2model typography system is built on the brand's core values: **Innovative, Accessible, Reliable, and Empowering**. We use Inter as our primary typeface - a geometric sans-serif that embodies our modern, technical aesthetic while maintaining excellent readability.

## Font Families

### Primary Font: Inter
- **Usage**: All UI text, headings, body copy
- **Weights**: 300 (Light) to 900 (Black)
- **Character**: Modern, geometric, highly readable
- **Fallback**: System fonts for performance

```css
font-family: var(--font-sans);
```

### Monospace Font: JetBrains Mono
- **Usage**: Code blocks, technical content, data
- **Weights**: 400, 500, 600
- **Character**: Clear character distinction, modern
- **Fallback**: System monospace fonts

```css
font-family: var(--font-mono);
```

## Type Scale

Our type scale follows a modular approach with fluid typography:

### Display (Hero/Marketing)
- **Size**: 48px - 96px (clamp-based)
- **Weight**: Bold (700)
- **Usage**: Hero sections, major announcements

```html
<h1 class="display">Transform Images Into Models</h1>
```

### Headings

| Level | Size Range | Weight | Usage |
|-------|------------|--------|--------|
| H1 | 32px - 48px | Bold (700) | Page titles |
| H2 | 24px - 36px | Semibold (600) | Section headers |
| H3 | 20px - 28px | Semibold (600) | Subsections |
| H4 | 18px - 24px | Medium (500) | Card titles |
| H5 | 16px - 20px | Medium (500) | Widget headers |
| H6 | 14px - 18px | Medium (500) | Labels (uppercase) |

### Body Text

| Variant | Size | Line Height | Usage |
|---------|------|-------------|--------|
| Large | 18px | 1.625 | Lead paragraphs |
| Regular | 16px | 1.625 | Standard body text |
| Small | 14px | 1.5 | Secondary content |
| Caption | 12px | 1.5 | Helper text, timestamps |

## Implementation Examples

### Basic Heading Structure
```html
<h1>Main Page Title</h1>
<p class="lead">This is a lead paragraph with larger text for emphasis.</p>
<p>Regular body text follows standard sizing and spacing.</p>
```

### Using Utility Classes
```html
<!-- Font sizes -->
<p class="text-lg">Large text (18px)</p>
<p class="text-base">Base text (16px)</p>
<p class="text-sm">Small text (14px)</p>

<!-- Font weights -->
<p class="font-semibold">Semibold text for emphasis</p>
<p class="font-medium">Medium weight for subtle emphasis</p>

<!-- Line heights -->
<p class="leading-relaxed">Relaxed line height for better readability</p>
<p class="leading-tight">Tight line height for headings</p>

<!-- Letter spacing -->
<p class="tracking-wide">Wide letter spacing</p>
<h6 class="uppercase tracking-widest">UPPERCASE LABEL</h6>
```

### Component Typography
```html
<!-- Button -->
<button class="btn btn-primary">
  <!-- Inherits: font-medium, text-base -->
  Get Started
</button>

<!-- Card -->
<div class="card">
  <h3>Card Title</h3> <!-- Uses H3 styling -->
  <p>Card content with regular body text.</p>
  <small class="caption">Posted 2 hours ago</small>
</div>
```

## Responsive Behavior

Our typography scales smoothly across devices:

### Desktop (1200px+)
- Base font size: 16px
- Display text: Up to 96px
- Optimal reading width maintained

### Tablet (768px - 1199px)
- Base font size: 16px
- Display text: Scales with viewport
- Fluid sizing in effect

### Mobile (320px - 767px)
- Base font size: 15px (small devices: 14px)
- Display text: Minimum 48px
- Full-width paragraphs

## Best Practices

### 1. Hierarchy
- Use no more than 3 heading levels per page section
- Maintain clear visual distinction between levels
- Don't skip heading levels (h1 → h3)

### 2. Readability
- Keep body text between 45-75 characters per line
- Use appropriate line height for text size
- Ensure sufficient contrast with backgrounds

### 3. Emphasis
- Use font weight for emphasis, not just size
- Combine weight with color for important elements
- Avoid overusing bold text

### 4. Consistency
- Stick to the defined type scale
- Use utility classes rather than inline styles
- Maintain consistent spacing between elements

## Accessibility Considerations

1. **Minimum Sizes**: Never go below 14px for body text
2. **Line Height**: Maintain at least 1.5 for body text
3. **Contrast**: Follow WCAG AA guidelines from brand colors
4. **Responsive**: Text remains readable when zoomed to 200%

## CSS Variables Reference

```css
/* Font Families */
--font-sans: 'Inter', -apple-system, ...
--font-mono: 'JetBrains Mono', ...

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
/* ... and more */

/* Font Weights */
--font-light: 300;
--font-regular: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;

/* Letter Spacing */
--tracking-tight: -0.025em;
--tracking-normal: 0;
--tracking-wide: 0.025em;
```

## Migration from Old System

1. Replace hardcoded `font-family` with `var(--font-sans)`
2. Update `font-weight: 500` to `font-weight: var(--font-medium)`
3. Replace pixel sizes with rem variables
4. Use clamp() values for responsive headings
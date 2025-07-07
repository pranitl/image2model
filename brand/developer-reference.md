# Developer Quick Reference

## Color Values

```css
/* Primary Colors - Blue Theme */
--primary: #5DADE2;          /* Bright Cyan - Main brand color */
--secondary: #3498DB;        /* Sky Blue - Secondary color */
--dark-charcoal: #3A424A;    /* Text and UI elements */
--vibrant-red: #E74C3C;      /* Errors and alerts only */
--sunset-orange: #E67E22;    /* Small accents only */
--golden-yellow: #F39C12;    /* Small accents only */

/* Neutral Colors */
--white: #FFFFFF;
--light-gray: #ECF0F1;
--silver-gray: #BDC3C7;
--medium-gray: #95A5A6;
--dark-gray: #7F8C8D;
--black: #000000;

/* Semantic Colors */
--success: #27AE60;
--warning: #F39C12;
--error: #E74C3C;
--info: #3498DB;

/* Dark Mode Colors */
--dark-bg-primary: #1a1f24;    /* Deep charcoal background */
--dark-bg-secondary: #141719;  /* Elevated surfaces */
--dark-bg-tertiary: #0f1113;   /* Recessed areas */
--dark-text-primary: #ECF0F1;  /* Main text */
--dark-text-secondary: #BDC3C7; /* Supporting text */
--dark-accent-primary: #5DADE2; /* Bright cyan accent */
--dark-accent-secondary: #3498DB; /* Sky blue accent */
```

## Gradients

```css
/* Blue Hero - Primary gradient */
background: linear-gradient(135deg, #1a2332 0%, #2c3e50 100%);

/* Blue Medium - Icon/feature gradient */
background: linear-gradient(135deg, #5DADE2 0%, #3498DB 100%);

/* Cool Ocean - Secondary */
background: linear-gradient(180deg, #5DADE2 0%, #3498DB 100%);

/* Mountain Mist - Neutral */
background: linear-gradient(45deg, #ECF0F1 0%, #BDC3C7 100%);
```

## Typography

```css
/* Font Stack */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
--text-5xl: 3rem;      /* 48px */

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

## Spacing

```css
/* Spacing Scale */
--space-0: 0;
--space-1: 0.25rem;    /* 4px */
--space-2: 0.5rem;     /* 8px */
--space-3: 0.75rem;    /* 12px */
--space-4: 1rem;       /* 16px */
--space-5: 1.25rem;    /* 20px */
--space-6: 1.5rem;     /* 24px */
--space-8: 2rem;       /* 32px */
--space-10: 2.5rem;    /* 40px */
--space-12: 3rem;      /* 48px */
--space-16: 4rem;      /* 64px */
```

## Border Radius

```css
--radius-none: 0;
--radius-sm: 0.125rem;  /* 2px */
--radius-base: 0.25rem; /* 4px */
--radius-md: 0.375rem;  /* 6px */
--radius-lg: 0.5rem;    /* 8px */
--radius-xl: 0.75rem;   /* 12px */
--radius-2xl: 1rem;     /* 16px */
--radius-full: 9999px;
```

## Shadows

```css
/* Box Shadows */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

## Breakpoints

```css
/* Responsive Breakpoints */
--screen-xs: 480px;
--screen-sm: 640px;
--screen-md: 768px;
--screen-lg: 1024px;
--screen-xl: 1280px;
--screen-2xl: 1536px;

/* Media Queries */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

## Component Classes

```css
/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #5DADE2;  /* Bright Cyan */
  color: #1a2332;      /* Dark text for contrast */
}

.btn-secondary {
  background: #34495e;  /* Dark secondary */
  color: #FFFFFF;
}

/* Cards */
.card {
  background: #FFFFFF;
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

/* Inputs */
.input {
  border: 1px solid #BDC3C7;
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  transition: border-color 0.3s ease;
}

.input:focus {
  border-color: #3498DB;
  outline: none;
}
```

## Icon Specifications

```css
/* Icon Sizes */
--icon-xs: 16px;
--icon-sm: 20px;
--icon-base: 24px;
--icon-lg: 32px;
--icon-xl: 48px;

/* Icon Strokes */
--stroke-xs: 1.5px;
--stroke-sm: 2px;
--stroke-base: 2px;
--stroke-lg: 2.5px;
--stroke-xl: 3px;
```

## Animation

```css
/* Transitions */
--transition-fast: 150ms;
--transition-base: 300ms;
--transition-slow: 500ms;

/* Easings */
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* Common Animations */
@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .5; }
}

@keyframes bounce {
  0%, 100% { transform: translateY(-25%); }
  50% { transform: none; }
}
```

## Quick Copy Snippets

### CSS Reset
```css
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
```

### Container
```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
```

### Gradient Text
```css
.gradient-text-blue {
  background: linear-gradient(135deg, #5DADE2 0%, #3498DB 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### Focus Ring
```css
.focus-ring {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.focus-ring:focus {
  outline-color: #3498DB;
}
```
# image2model Design System

## Core Brand Values
- **Accessible**: Making 3D content creation accessible to everyone
- **Professional**: Professional-grade results without expertise
- **Instant**: Fast processing with AI-powered technology
- **Simple**: No 3D expertise required

## Color Palette

### Theme Overview
image2model uses a **Blue Theme with Mixed Light/Dark Sections** for optimal contrast and readability.

### Primary Brand Colors
- **gradient-cool-ocean**: `linear-gradient(135deg, #1a2332 0%, #2c3e50 100%)` - Dark hero backgrounds
- **gradient-primary**: `linear-gradient(135deg, #2c3e50 0%, #34495e 100%)` - CTA sections
- **gradient-blue-medium**: `linear-gradient(135deg, #5DADE2 0%, #3498DB 100%)` - Feature icons
- **gradient-text-blue**: `linear-gradient(135deg, #3498db 0%, #5dade2 100%)` - Accent text on light backgrounds

### Section Backgrounds
- **Hero/CTA Sections**: Dark blue gradients (#1a2332 to #2c3e50)
- **Features Section**: Light gray (#f8f9fa)
- **How It Works**: Light gray (#ecf0f1)
- **Examples Section**: Light gray (#f8f9fa)
- **Cards/Content**: White (#ffffff)
- **Body Background**: Light gray (#f8f9fa)

### Text Colors
- **On Dark Backgrounds**: White (#ffffff) for headings, Light gray (#bdc3c7) for secondary
- **On Light Backgrounds**: Dark charcoal (#2c3e50) for headings, Medium gray (#34495e) for body
- **Navigation**: White (#ffffff) on dark navbar
- **Muted Text**: #95a5a6

### Button Colors
- **Primary Button**: Light blue gradient `linear-gradient(135deg, #5dade2 0%, #3498db 100%)`
- **Primary Hover**: Darker blue gradient `linear-gradient(135deg, #3498db 0%, #2874a6 100%)`
- **Secondary Button**: Light gray (#ecf0f1) background, dark text (#2c3e50)
- **Ghost Button**: Transparent with white border (on dark) or gray border (on light)

## Typography

### Font Stack
- **Primary**: Inter (sans-serif)
- **Monospace**: JetBrains Mono (for code/technical content)

### Type Scale
- **Display**: clamp(3rem, 8vw, 6rem) - Hero headlines
- **H1**: clamp(2rem, 5vw, 3rem)
- **H2**: clamp(1.5rem, 4vw, 2.25rem) - Section titles
- **H3**: clamp(1.25rem, 3vw, 1.75rem) - Feature titles
- **Body**: 1rem (16px base)
- **Body Large**: var(--text-lg) - Lead paragraphs
- **Small**: 0.875rem - Secondary text

### Text Styles
- **Section Title**: Large, centered, with margin-bottom: 3rem
- **Section Subtitle**: 
  - font-size: var(--text-lg)
  - color: #5a6c7d (text-secondary)
  - text-align: center
  - max-width: 100% (important for centering)
  - margin-top: var(--spacing-md)

## Layout Patterns

### Hero Section
- Gradient background (gradient-cool-ocean)
- Geometric pattern overlay
- Centered content with max-width container
- Animated floating logo (150x150px)
- Display headline with gradient text effect
- Lead paragraph description
- Primary CTA button with icon
- Key stats display (processing time, batch ready)

### Feature Cards
- Grid layout (2 columns on desktop, 1 on mobile)
- Card hover effects with lift animation
- Icon with gradient background
- Title and description
- Consistent padding and border radius

### Examples Section
- Gallery layout (side-by-side comparison)
- Before/After images with labels
- Card-based design with hover effects
- "Try with this image" secondary buttons

### Footer
- Horizontal navigation (Features, Pricing, Contact)
- Logo with tagline
- Simplified single-column layout
- Copyright notice

## Component Patterns

### Buttons
- **Primary**: Light blue gradient (#5dade2 to #3498db), white text, hover lift effect
- **Secondary**: Light gray (#ecf0f1) background, dark text (#2c3e50)
- **Ghost**: Transparent with border (white on dark, gray on light)
- **Size variants**: btn-sm, btn (default), btn-lg
- **Hover effects**: Darker gradient + translateY(-2px) + shadow
- **Icon support**: Gap spacing for icons in buttons

### Cards
- Background: White (#ffffff) on light sections
- Border radius: var(--radius-lg or --radius-md)
- Hover effects: translateY(-5px) + enhanced shadow
- Consistent padding: var(--spacing-lg)
- Feature cards: White background with colored gradient icons

### Navigation
- Sticky navbar with dark blue background (rgba(26, 35, 50, 0.98))
- Backdrop blur effect (10px)
- Logo (48x48) + white text branding
- White navigation links (#ecf0f1) with light blue hover (#5dade2)
- Mobile hamburger menu
- Primary CTA button in nav (blue gradient)

## Animation System

### Core Animations
- **animate-fade-in**: Basic fade in
- **animate-fade-in-up**: Fade in with upward motion
- **animate-fade-in-scale**: Fade in with scale
- **animate-float**: Continuous floating effect (for hero logo)
- **animate-gradient**: Gradient animation for text
- **reveal-on-scroll**: Intersection observer triggered animations
- **delay-stagger**: Sequential delays for grid items

### Timing
- **delay-200**: 200ms delay
- **delay-400**: 400ms delay
- **delay-600**: 600ms delay

## Spacing System
- Uses CSS custom properties (--spacing-xs through --spacing-2xl)
- Consistent spacing scale throughout
- Responsive adjustments for mobile

## Responsive Breakpoints
- Mobile: max-width: 480px
- Tablet: max-width: 768px
- Desktop: 769px and up

## Best Practices

1. **Accessibility**
   - Proper alt text for all images
   - ARIA labels for interactive elements
   - Focus visible states
   - Semantic HTML structure

2. **Performance**
   - Lazy loading for images (loading="lazy")
   - Optimized image formats (WebP for 3D renders)
   - Deferred script loading

3. **Content Guidelines**
   - Short, punchy headlines
   - Clear value propositions
   - Action-oriented CTAs
   - Technical jargon minimized

4. **Visual Hierarchy**
   - Large hero section draws attention
   - Clear section breaks
   - Consistent card heights in grids
   - Proper use of whitespace
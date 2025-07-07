# image2model Design System

## Core Brand Values
- **Accessible**: Making 3D content creation accessible to everyone
- **Professional**: Professional-grade results without expertise
- **Instant**: Fast processing with AI-powered technology
- **Simple**: No 3D expertise required

## Color Palette

### Primary Colors
- **Blue Gradient (gradient-cool-ocean)**: Primary brand gradient
- **Blue Medium (gradient-blue-medium)**: Icon backgrounds
- **Blue Text (gradient-text-blue)**: Gradient text effects

### Semantic Colors
- **Background Primary**: Dark background (#0a0a0a or similar)
- **Background Secondary**: Slightly lighter dark
- **Background Tertiary**: Card backgrounds
- **Text Primary**: White or light gray
- **Text Secondary**: #5a6c7d (muted gray-blue)
- **Text Muted**: Even lighter gray

### Accent Colors
- **Primary Button**: Blue gradient with hover effects
- **Secondary Button**: Ghost/outline style
- **Success**: Green tones
- **Error**: Red tones

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
- **Primary**: Blue gradient background, white text, hover lift effect
- **Secondary**: Ghost style with border
- **Size variants**: btn-sm, btn (default), btn-lg
- Icon support with proper spacing

### Cards
- Background: var(--bg-tertiary)
- Border radius: var(--radius-lg or --radius-md)
- Hover effects: lift animation, border highlight
- Consistent padding

### Navigation
- Fixed navbar with blur backdrop
- Logo + text branding
- Horizontal menu items
- Mobile hamburger menu
- Primary CTA button in nav

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
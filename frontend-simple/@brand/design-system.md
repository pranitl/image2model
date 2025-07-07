# image2model Design System

## Core Brand Values
- **Accessible**: Making 3D content creation accessible to everyone
- **Professional**: Professional-grade results without expertise
- **Instant**: Fast processing with AI-powered technology
- **Simple**: No 3D expertise required

## Color Palette

### Theme Overview
image2model uses a **Unified Light Theme with Blue Accents** for consistency and modern aesthetics.

### Primary Colors
- **Background Primary**: White (#ffffff)
- **Background Secondary**: Light gray (#f8f9fa)
- **Background Tertiary**: Lighter gray (#ecf0f1)
- **Text Primary**: Dark charcoal (#2c3e50)
- **Text Secondary**: Medium gray (#34495e)
- **Text Muted**: Light gray (#95a5a6)
- **Accent Primary**: Sky blue (#3498db)
- **Accent Secondary**: Light blue (#5dade2)

### Gradient Presets
- **gradient-cool-ocean**: `linear-gradient(135deg, #1a2332 0%, #2c3e50 100%)` - Hero/CTA backgrounds
- **gradient-primary**: `linear-gradient(135deg, #2c3e50 0%, #34495e 100%)` - Dark sections
- **gradient-blue-medium**: `linear-gradient(135deg, #5DADE2 0%, #3498DB 100%)` - Feature icons
- **gradient-blue-light**: `linear-gradient(135deg, #85C1E9 0%, #5DADE2 100%)` - Light accents

### Component Colors
- **Navigation**: Dark blue background (rgba(26, 35, 50, 0.98)) with white text
- **Body Background**: Light gray (#f8f9fa)
- **Cards**: White (#ffffff)
- **Borders**: Light gray (#dee2e6)

### Button Styling
- **Primary**: Light blue gradient (#5dade2 to #3498db) with white text
- **Primary Hover**: Darker blue gradient (#3498db to #2874a6)
- **Secondary**: Light gray (#ecf0f1) with dark text (#2c3e50)
- **Ghost**: Transparent with gray border

### Special Sections
- **Hero Sections**: Dark gradient background with white text
- **Feature Cards**: White background with blue gradient icons
- **Upload Zone**: White background with blue accent elements

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

### Page Structure Pattern
**IMPORTANT**: All pages follow a consistent visual hierarchy pattern:
1. **Body Background**: Light gray (#f8f9fa) from `var(--bg-secondary)`
2. **Section Backgrounds**: Main content sections also use #f8f9fa for consistency
3. **Content Containers**: White (#ffffff) cards/containers inside gray sections
4. **Visual Separation**: Achieved through white containers on gray backgrounds, not through alternating section colors

This creates a clean, unified look where content "floats" on the page background.

### Hero Section
- Gradient background (gradient-cool-ocean)
- Geometric pattern overlay
- Centered content with max-width container
- Animated floating logo (150x150px)
- Display headline with gradient text effect
- Lead paragraph description
- Primary CTA button with icon
- Key stats display (processing time, batch ready)

### Content Sections
- **Background**: Always #f8f9fa (matching body background)
- **Padding**: Typically `padding: 3rem 0` or `5rem 0`
- **Container**: Max-width container for content alignment
- **Cards/Content**: White backgrounds with subtle shadows
- **Example sections**: features-section, examples-section, upload-section, help-tips-section

### Feature Cards
- Grid layout (2 columns on desktop, 1 on mobile)
- White background on gray section
- Card hover effects with lift animation
- Icon with gradient background
- Title and description
- Consistent padding and border radius
- Subtle box-shadow for depth

### Examples Section
- Gallery layout (side-by-side comparison)
- Before/After images with labels
- Card-based design with hover effects
- "Try with this image" secondary buttons
- White cards on gray section background

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

## UI Development Patterns

### Page-Specific Overrides
When certain pages need specific styling adjustments:

1. **Inline Style Blocks**: For critical overrides that ensure visual consistency
   - Place in `<style>` tags within the HTML `<head>`
   - Use for theme-specific adjustments (e.g., blue theme overrides in index.html)
   - Keep overrides minimal and well-commented

2. **Section Background Consistency**: 
   - Use explicit background colors (#f8f9fa) rather than CSS variables when consistency is critical
   - This ensures sections match across different pages even if variables change

3. **Component Background Hierarchy**:
   - Sections: Gray background (#f8f9fa)
   - Content containers: White background (#ffffff)
   - Interactive elements: White or light backgrounds with borders/shadows

### CSS Architecture
1. **Base styles**: style.css (general styles, resets)
2. **Variables**: variables.css (color palette, spacing)
3. **Components**: components.css (reusable UI elements)
4. **Page-specific**: landing-page.css, upload-page.css, etc.
5. **Inline overrides**: When specific visual consistency is required

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
   - Clear section breaks with consistent backgrounds
   - White content cards on gray sections
   - Consistent card heights in grids
   - Proper use of whitespace

5. **Consistency Patterns**
   - Always check index.html as the source of truth for styling patterns
   - Maintain the gray section/white content pattern across all pages
   - Use subtle shadows and borders for depth, not background color changes
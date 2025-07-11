# Color Usage Guidelines

## Primary Colors - Blue Theme

### Bright Cyan (#5DADE2) - PRIMARY
- **Usage**: Primary buttons, call-to-action elements, main brand accents
- **Context**: Main brand color for all primary interactions
- **Avoid**: On light blue backgrounds, small text sizes

### Sky Blue (#3498DB) - SECONDARY
- **Usage**: Secondary buttons, hover states, gradient combinations
- **Context**: Support color for depth and variation
- **Avoid**: On cyan backgrounds without sufficient contrast

### Dark Charcoal (#3A424A)
- **Usage**: Primary text, headers, dark UI elements
- **Context**: Professional, stable elements that need high contrast
- **Avoid**: On dark backgrounds, small text sizes

### Vibrant Red (#E74C3C)
- **Usage**: Error states, critical alerts only
- **Context**: Warnings, errors, destructive actions
- **Avoid**: Primary actions, large areas, main CTAs

### Sunset Orange (#E67E22)
- **Usage**: Icons, borders, small accent elements only
- **Context**: Warmth, creativity, innovation
- **Avoid**: NEVER use as background color, error messages, critical alerts
- **Note**: Too harsh for large areas - use only for small accents

### Golden Yellow (#F39C12)
- **Usage**: Icons, small highlights, accent borders only
- **Context**: Optimism, energy, accomplishment
- **Avoid**: NEVER use as background color, on white backgrounds without borders
- **Note**: Too harsh for large areas - use only for small accents

## Color Combinations

### Recommended Pairings - Blue Theme Primary
1. **Primary CTA**: Blue Gradient (#3498db to #2874a6) + White Text (actual implementation)
2. **Hero Sections**: Dark Blue Gradient (#1a2332 to #2c3e50) + White Text
3. **Professional**: Sky Blue (#3498DB) + Light Gray (#ECF0F1)
4. **Modern**: Bright Cyan (#5DADE2) + Sky Blue (#3498DB) gradients

**Note**: Frontend implementation uses blue gradients for primary buttons instead of solid cyan.

### Avoid These Combinations
- Red + Orange (too similar, low contrast)
- Yellow + White (accessibility issues)
- Blue + Cyan (insufficient differentiation)

## Background Usage

### Light Backgrounds
- Use Dark Charcoal for primary text
- Use primary colors for accents and CTAs
- Maintain 60-30-10 rule (60% neutral, 30% secondary, 10% accent)

### Hero/Dark Sections
- Use Dark Blue Gradient (#1a2332 to #2c3e50) for hero sections
- Use White text for high contrast
- Ensure WCAG AA compliance for contrast ratios

## Special Use Cases

### Data Visualization
- Use the full spectrum for different data points
- Ensure colorblind-friendly alternatives
- Provide patterns or labels for accessibility

### UI States
- **Default**: Primary brand colors
- **Hover**: 10% darker or use gradient
- **Active**: 20% darker
- **Disabled**: 50% opacity with gray overlay


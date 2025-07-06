# Logo Usage Guidelines

## Logo Variations

### Primary Logo
- **Format**: Square with rounded corners
- **Use**: Default logo for all applications
- **File**: `logo-original.png`

### Logo Versions
1. **Full Color**: Use on light backgrounds
2. **Monochrome Dark**: Use on light backgrounds when color isn't available
3. **Monochrome Light**: Use on dark backgrounds
4. **Knockout**: White version for dark backgrounds

## Spacing and Clear Space

### Minimum Clear Space
The logo must have breathing room. The minimum clear space is defined by the "X" height:
- **X = 1/4 of logo height**
- Clear space = X on all sides

```
┌─────────────────────────┐
│          X              │
│    ┌─────────────┐      │
│  X │    LOGO     │ X    │
│    └─────────────┘      │
│          X              │
└─────────────────────────┘
```

### Minimum Sizes
- **Digital**: 48px × 48px minimum
- **Print**: 0.5" × 0.5" minimum
- **Favicon**: 16px × 16px (simplified version)

## Placement Guidelines

### Recommended Positions
1. **Top Left**: Navigation bars, headers
2. **Center**: Splash screens, loading states
3. **Bottom**: Footer, watermarks

### Alignment
- Always align to the visual center, not mathematical center
- Account for the rounded corners in spacing calculations
- Maintain equal padding when in containers

## Background Usage

### Approved Backgrounds
✅ **Do**:
- White (#FFFFFF)
- Light Gray (#ECF0F1)
- Dark Charcoal (#3A424A) - use light logo
- Subtle gradients with sufficient contrast

❌ **Don't**:
- Busy patterns
- Low contrast backgrounds
- Competing brand colors
- Photographic backgrounds without overlay

## Incorrect Usage

### Never Do This:
1. **Don't stretch or distort** the logo
2. **Don't rotate** the logo
3. **Don't add effects** (shadows, glows, bevels)
4. **Don't change colors** of individual elements
5. **Don't recreate** the logo
6. **Don't place on clashing colors**
7. **Don't add borders** unless specified
8. **Don't use at angles** other than 0°

## Co-Branding

When using with partner logos:
1. Maintain equal visual weight
2. Use consistent sizing methodology
3. Separate with vertical divider if needed
4. Ensure both logos have equal clear space

## File Formats

### Digital Use
- **SVG**: Preferred for web (scalable)
- **PNG**: For applications requiring raster
  - logo-48.png (small)
  - logo-192.png (medium)
  - logo-512.png (large)
  - logo-1024.png (extra large)

### Print Use
- **PDF**: Vector format for professional printing
- **EPS**: Legacy vector format
- **PNG**: 300 DPI for raster needs

### Special Formats
- **ICO**: Windows favicon
- **ICNS**: macOS application icon
- **Android**: Adaptive icon format

## Usage Examples

### Application Icon
```css
.app-icon {
  width: 192px;
  height: 192px;
  border-radius: 38.4px; /* 20% of size */
}
```

### Navigation Logo
```css
.nav-logo {
  height: 48px;
  width: 48px;
  margin: 16px;
}
```

### Loading Screen
```css
.loading-logo {
  width: 128px;
  height: 128px;
  animation: pulse 2s ease-in-out infinite;
}
```

## Legal Notice

The image2model logo is a trademark. Unauthorized use, reproduction, or modification is prohibited. For usage outside these guidelines, please contact the brand team.
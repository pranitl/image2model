# Typography Accessibility Guidelines

## Minimum Font Sizes

Based on WCAG 2.1 guidelines and best practices:

### Body Text
- **Minimum**: 16px (1rem) - Our default
- **Mobile**: 14px minimum on very small screens
- **Recommendation**: Never go below 14px for body text

### Headings
- **H1**: Minimum 32px on mobile (clamps from 2rem)
- **H2**: Minimum 24px on mobile (clamps from 1.5rem)
- **H3**: Minimum 20px on mobile (clamps from 1.25rem)
- **H4-H6**: Minimum 16px on mobile

### Small Text
- **Caption/Helper**: 12px (0.75rem) - Use sparingly
- **Must have**: Higher contrast when using small sizes
- **Alternative**: Consider using regular size with muted color instead

## Line Height Guidelines

Our system uses appropriate line heights for readability:

- **Headings**: 1.25-1.375 (tight to snug) - Good for large text
- **Body text**: 1.5-1.625 (normal to relaxed) - Optimal for reading
- **Small text**: 1.5 (normal) - Maintains readability

## Letter Spacing

- **Headings**: Slightly negative (-0.025em) for visual cohesion
- **Body text**: Normal (0) for optimal readability
- **Small/Caption**: Slightly positive (0.025em) for clarity
- **Uppercase**: Always add positive spacing (0.1em)

## Font Weight Considerations

### Minimum Weights for Readability
- **Light (300)**: Only for large display text
- **Regular (400)**: Standard for body text
- **Medium (500)**: Good for emphasis without bold
- **Semibold+ (600+)**: For headings and strong emphasis

### Dark Mode Adjustments
- Consider using slightly heavier weights in dark mode
- Our system maintains good contrast with current weights

## Color Contrast with Typography

When using our brand colors with text:

### High Contrast (AAA Compliant)
- Dark Charcoal (#3A424A) on White: 12.1:1 ✅
- White on Dark Charcoal: 12.1:1 ✅

### Standard Contrast (AA Compliant)
- Vibrant Red (#E74C3C) on White: 4.5:1 ✅
- Sky Blue (#3498DB) on White: 4.7:1 ✅

### Low Contrast (Decorative Only)
- Golden Yellow (#F39C12) on White: 2.1:1 ❌
- Use only for large display text or with dark backgrounds

## Responsive Considerations

Our `clamp()` functions ensure:
1. Text never gets too small on mobile
2. Text never gets too large on desktop
3. Smooth scaling between breakpoints

Example:
```css
--h1-font-size: clamp(2rem, 5vw, 3rem);
/* Minimum: 32px, Maximum: 48px, Scales with viewport */
```

## Testing Checklist

- [ ] All text is at least 14px on mobile devices
- [ ] Line height provides adequate spacing
- [ ] Font weights are distinguishable
- [ ] Text remains readable when zoomed to 200%
- [ ] Focus indicators are visible on all interactive text
- [ ] Color contrast meets WCAG AA standards
- [ ] Text can be selected and copied
- [ ] No text is presented as images

## Special Considerations

### Code Blocks
- Monospace font maintains character alignment
- Minimum 14px size for readability
- Adequate contrast in both light/dark modes

### Links
- Distinguished by more than color alone (font-weight: 500)
- Underline on hover for additional indication
- Focus state clearly visible

### Truncated Text
- Use `.truncate` class sparingly
- Ensure full text is accessible via tooltip or expansion
- Provide alternative access to full content
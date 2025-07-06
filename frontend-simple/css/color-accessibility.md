# CSS Color System - Accessibility Compliance

## WCAG AA Compliant Color Combinations

Based on the image2model brand guidelines, these color combinations meet WCAG 2.1 AA standards:

### For Normal Text (4.5:1 minimum)
- **Dark Charcoal on White**: `color: var(--brand-dark-charcoal); background: var(--brand-white);` - 12.1:1 ✅
- **White on Dark Charcoal**: `color: var(--brand-white); background: var(--brand-dark-charcoal);` - 12.1:1 ✅
- **Vibrant Red on White**: `color: var(--brand-vibrant-red); background: var(--brand-white);` - 4.5:1 ✅
- **Sky Blue on White**: `color: var(--brand-sky-blue); background: var(--brand-white);` - 4.7:1 ✅

### For Large Text Only (3:1 minimum)
- **Sunset Orange on White**: `color: var(--brand-sunset-orange); background: var(--brand-white);` - 3.2:1 ⚠️

### Non-Compliant for Text (Use for decorative elements only)
- **Golden Yellow on White**: 2.1:1 ❌
- **Bright Cyan on White**: 2.4:1 ❌

## Dark Mode Compliance

In dark mode, ensure these combinations:
- **White on Dark Background**: `color: var(--dark-text-primary); background: var(--dark-bg-primary);`
- **Light Gray on Dark**: `color: #b0b0b0; background: var(--dark-bg-primary);`

## Implementation in CSS

The variables.css file includes these accessible combinations by default:

```css
/* Light mode - accessible by default */
--text-primary: var(--gray-900); /* Dark Charcoal */
--bg-primary: var(--brand-white);

/* Dark mode - accessible by default */
--dark-text-primary: var(--brand-white);
--dark-bg-primary: #0a0a0a;
```

## Testing Checklist

- [ ] Test all button colors against their backgrounds
- [ ] Verify link colors meet 4.5:1 ratio
- [ ] Check error/success/warning messages for contrast
- [ ] Test in Windows High Contrast mode
- [ ] Verify colorblind safety using browser extensions

## Safe Color Usage Patterns

1. **Primary Actions**: Use `--brand-vibrant-red` on white backgrounds
2. **Secondary Actions**: Use `--brand-sky-blue` on white backgrounds
3. **Text**: Always use `--brand-dark-charcoal` or `--gray-900` on light backgrounds
4. **Warnings**: Use `--brand-sunset-orange` only for large text or with dark text overlay
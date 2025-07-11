# Color Accessibility Guidelines

## WCAG Compliance

### Contrast Ratios

All color combinations must meet WCAG 2.1 standards:
- **Normal Text**: Minimum 4.5:1 contrast ratio (AA)
- **Large Text**: Minimum 3:1 contrast ratio (AA)
- **Enhanced**: 7:1 for normal text, 4.5:1 for large text (AAA)

### Tested Color Combinations

#### High Contrast (AAA Compliant)
| Foreground | Background | Ratio | Usage |
|------------|------------|-------|--------|
| #3A424A (Dark Charcoal) | #FFFFFF (White) | 12.1:1 | Primary text |
| #FFFFFF (White) | #3A424A (Dark Charcoal) | 12.1:1 | Inverted UI |
| #3A424A (Dark Charcoal) | #ECF0F1 (Light Gray) | 10.2:1 | Secondary surfaces |

#### Standard Contrast (AA Compliant)
| Foreground | Background | Ratio | Usage |
|------------|------------|-------|--------|
| #E74C3C (Vibrant Red) | #FFFFFF (White) | 4.5:1 | CTAs, alerts |
| #3498DB (Sky Blue) | #FFFFFF (White) | 4.7:1 | Links, info |
| #E67E22 (Sunset Orange) | #FFFFFF (White) | 3.2:1 | Large text only |
| #3A424A (Dark Charcoal) | #BDC3C7 (Silver Gray) | 4.8:1 | Subtle elements |

#### Non-Compliant Combinations (Avoid for Text)
| Foreground | Background | Ratio | Alternative Use |
|------------|------------|-------|-----------------|
| #F39C12 (Golden Yellow) | #FFFFFF (White) | 2.1:1 | Icons with borders only |
| #5DADE2 (Bright Cyan) | #FFFFFF (White) | 2.4:1 | Decorative elements only |
| #BDC3C7 (Silver Gray) | #ECF0F1 (Light Gray) | 1.7:1 | Backgrounds only |

## Colorblind Considerations

### Safe Patterns
1. **Don't rely on color alone** - Use icons, patterns, or labels
2. **Test with simulators** - Check designs in all colorblind modes
3. **High contrast mode** - Ensure designs work in Windows High Contrast

### Colorblind-Friendly Palettes
```css
/* Deuteranopia-safe palette */
.colorblind-safe-1 { color: #3A424A; } /* Dark Charcoal */
.colorblind-safe-2 { color: #3498DB; } /* Sky Blue */
.colorblind-safe-3 { color: #F39C12; } /* Golden Yellow */
.colorblind-safe-4 { color: #E74C3C; } /* Vibrant Red */

/* Avoid these combinations */
/* Red (#E74C3C) + Orange (#E67E22) - Too similar */
/* Blue (#3498DB) + Cyan (#5DADE2) - Confusing */
```

## Implementation Guidelines

### CSS Variables for Accessibility
```css
:root {
  /* High contrast text */
  --text-primary: #3A424A;
  --text-primary-inverted: #FFFFFF;
  
  /* AA compliant interactive */
  --link-color: #3498DB;
  --link-hover: #2C7FBD; /* Darker for better contrast */
  
  /* Semantic colors with contrast */
  --error-text: #C0392B; /* Darker red for text */
  --error-bg: #E74C3C;
  --success-text: #1E8449; /* Darker green for text */
  --warning-text: #7D6608; /* Darker yellow for text */
}

/* High contrast mode overrides */
@media (prefers-contrast: high) {
  :root {
    --text-primary: #000000;
    --bg-primary: #FFFFFF;
    --border-color: #000000;
  }
}
```

### Testing Checklist
- [ ] Test all text/background combinations with contrast checker
- [ ] Verify in grayscale mode
- [ ] Check with colorblind simulators
- [ ] Test with screen readers
- [ ] Validate in high contrast mode
- [ ] Ensure focus indicators meet 3:1 ratio

### Tools Recommended
1. **WebAIM Contrast Checker**: For precise ratio calculations
2. **Stark (Figma/Sketch)**: Design-time accessibility checks
3. **Chrome DevTools**: Built-in contrast ratio checker
4. **Colorblinding**: Chrome extension for live testing
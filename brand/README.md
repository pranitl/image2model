# image2model Brand Guidelines

Welcome to the image2model brand guidelines. This comprehensive guide ensures consistent brand representation across all touchpoints.

## 📁 Directory Structure

```
brand/
├── README.md                    # This file
├── index.html                   # Interactive style guide
├── developer-reference.md       # Quick reference for developers
├── assets/
│   ├── logo-original.png       # Primary logo file
│   └── generate-logo-formats.sh # Script to generate various formats
└── guidelines/
    ├── colors.json             # Color palette definitions
    ├── color-usage.md          # Color usage guidelines
    ├── gradients.css           # Gradient definitions
    ├── accessibility.md        # WCAG compliance guide
    ├── logo-usage.md           # Logo usage rules
    ├── brand-voice.md          # Voice and tone guidelines
    └── icon-style.md           # Icon design specifications
```

## 🚀 Quick Start

1. **View the Style Guide**: Open `brand/index.html` in a web browser
2. **Get Color Values**: Check `guidelines/colors.json` or `developer-reference.md`
3. **Apply Gradients**: Import `guidelines/gradients.css` into your project
4. **Generate Logo Formats**: Run `assets/generate-logo-formats.sh`

## 🎨 Brand Overview

### Core Elements
- **Logo**: Geometric, faceted design representing transformation
- **Colors**: Vibrant palette inspired by the creative process
- **Typography**: Clean, modern, and accessible
- **Voice**: Professional yet approachable, clear and empowering

### Primary Colors
- Dark Charcoal (#3A424A)
- Vibrant Red (#E74C3C)
- Sky Blue (#3498DB)
- Bright Cyan (#5DADE2)
- Sunset Orange (#E67E22)
- Golden Yellow (#F39C12)

## 📋 Usage Guidelines

### For Designers
1. Always maintain proper logo clear space
2. Use approved color combinations for accessibility
3. Follow the geometric/faceted style for icons
4. Reference `brand-voice.md` for content creation

### For Developers
1. Import CSS variables from `developer-reference.md`
2. Use gradient classes from `gradients.css`
3. Maintain WCAG AA compliance (see `accessibility.md`)
4. Follow component patterns in the style guide

### For Marketing
1. Use consistent messaging from `brand-voice.md`
2. Apply proper logo usage per `logo-usage.md`
3. Maintain brand personality in all communications
4. Use approved social media formats

## 🛠️ Implementation

### CSS Integration
```css
/* Import brand colors */
@import url('path/to/brand/guidelines/gradients.css');

/* Use CSS variables */
.brand-element {
  color: var(--dark-charcoal);
  background: var(--light-gray);
}
```

### Logo Implementation
```html
<!-- Standard logo -->
<img src="brand/assets/logo-original.png" alt="image2model" class="logo">

<!-- With proper spacing -->
<div class="logo-container" style="padding: 24px;">
  <img src="brand/assets/logo-original.png" alt="image2model">
</div>
```

## ✅ Compliance Checklist

Before publishing any brand materials:
- [ ] Logo has proper clear space
- [ ] Colors meet WCAG contrast requirements
- [ ] Typography follows size guidelines
- [ ] Voice matches brand personality
- [ ] Icons follow geometric style
- [ ] Tested on light/dark backgrounds

## 📞 Contact

For brand-related questions or special use cases not covered in these guidelines, please contact the brand team.

## 🔄 Version History

- **v1.0** (2025) - Initial brand guidelines release
  - Complete color system
  - Logo usage guidelines
  - Voice and tone documentation
  - Icon style specifications
  - Developer resources

---

© 2024 image2model. All rights reserved.
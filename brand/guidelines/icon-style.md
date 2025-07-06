# Icon Style Guidelines

## Design Principles

### Geometric Foundation
Icons should reflect the polygonal, faceted style of the logo:
- Use angular shapes and triangular facets
- Maintain consistent stroke weights
- Apply geometric construction methods

### Visual Consistency
- **Style**: Outlined with geometric fills
- **Weight**: 2px stroke at 24x24px base size
- **Corners**: 2px radius for outer shapes
- **Angles**: Prefer 45°, 90°, 135° angles

## Icon Grid System

### Base Grid: 24x24px
```
┌─────────────────────────┐
│  ┌─────────────────┐   │ <- 2px padding
│  │                 │   │
│  │   ┌─────────┐   │   │ <- 20x20px live area
│  │   │         │   │   │
│  │   │  ICON   │   │   │ <- 16x16px content
│  │   │         │   │   │
│  │   └─────────┘   │   │
│  │                 │   │
│  └─────────────────┘   │
└─────────────────────────┘
```

### Scaling Sizes
- **Small**: 16x16px (1.5px stroke)
- **Medium**: 24x24px (2px stroke) - Default
- **Large**: 32x32px (2.5px stroke)
- **XLarge**: 48x48px (3px stroke)

## Color Application

### Monochrome Icons
```css
.icon-default {
  stroke: #3A424A; /* Dark Charcoal */
  fill: none;
}

.icon-hover {
  stroke: #3498DB; /* Sky Blue */
  fill: rgba(52, 152, 219, 0.1);
}

.icon-active {
  stroke: #E74C3C; /* Vibrant Red */
  fill: rgba(231, 76, 60, 0.15);
}
```

### Duotone Icons
Use two colors for depth:
- Primary: Stroke and main elements
- Secondary: Accent fills or secondary elements

### Full Color Icons
Follow the polygonal style with gradient fills:
```css
.icon-multicolor {
  /* Use brand gradients for fills */
  fill: url(#gradient-warm-sunset);
}
```

## Icon Categories

### Navigation Icons
- Simple, recognizable shapes
- Clear directional indicators
- Consistent metaphors

Examples:
- Home: Geometric house shape
- Menu: Three polygonal bars
- Search: Faceted magnifying glass
- Settings: Geometric gear

### Action Icons
- Bold, clear actions
- Include motion indicators
- Use arrows for direction

Examples:
- Upload: Upward arrow with cloud
- Download: Downward arrow with tray
- Transform: Rotating polygons
- Process: Interlocking triangles

### Status Icons
- Clear state indication
- Use color meaningfully
- Include accessible patterns

Examples:
- Success: Faceted checkmark
- Error: Geometric X
- Warning: Triangular alert
- Loading: Rotating polygons

### File Type Icons
- Distinctive shapes per type
- Consistent fold/corner style
- Clear type indicators

Examples:
- Image: Geometric landscape
- 3D Model: Wireframe cube
- Video: Faceted play button
- Document: Folded corner

## Construction Guidelines

### Step 1: Base Shape
Start with primary geometric form
```
┌───────┐
│       │  <- Square base
│       │
└───────┘
```

### Step 2: Add Facets
Break into triangular segments
```
┌───────┐
│ ╱ │ ╲ │  <- Diagonal divisions
│╱  │  ╲│
└───────┘
```

### Step 3: Apply Style
Add strokes and selective fills
```
┌───────┐
│ ╱ │ ╲ │  <- 2px strokes
│╱▓▓│  ╲│  <- Selective fill
└───────┘
```

## Implementation

### SVG Structure
```svg
<svg width="24" height="24" viewBox="0 0 24 24">
  <g class="icon-base">
    <path stroke="#3A424A" stroke-width="2" fill="none" d="..." />
    <polygon fill="#E74C3C" opacity="0.15" points="..." />
  </g>
</svg>
```

### CSS Classes
```css
/* Base icon styles */
.icon {
  width: 24px;
  height: 24px;
  transition: all 0.2s ease;
}

/* Size variants */
.icon-sm { width: 16px; height: 16px; }
.icon-lg { width: 32px; height: 32px; }
.icon-xl { width: 48px; height: 48px; }

/* State variants */
.icon:hover { transform: scale(1.1); }
.icon:active { transform: scale(0.95); }

/* Animation */
.icon-spin {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

## Quality Checklist

Before finalizing any icon:
- [ ] Aligns to pixel grid
- [ ] Uses consistent stroke weight
- [ ] Follows geometric/faceted style
- [ ] Works at all intended sizes
- [ ] Has appropriate padding
- [ ] Includes hover/active states
- [ ] Tested on light/dark backgrounds
- [ ] Accessible contrast ratios
- [ ] Exports cleanly as SVG

## File Naming Convention

```
icon-[category]-[name]-[variant].svg

Examples:
icon-nav-home-outline.svg
icon-action-upload-filled.svg
icon-status-success-duotone.svg
icon-file-image-color.svg
```
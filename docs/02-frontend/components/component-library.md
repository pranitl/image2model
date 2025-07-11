# Component Library Overview

> **Last Updated**: 2025-01-11  
> **Status**: Complete  
> **Version**: 1.0

## Overview

The image2model frontend uses a modular component architecture built with SvelteKit. This document provides a complete inventory of all UI components, their purpose, and implementation details. Components follow accessibility guidelines from the brand standards and maintain consistent visual patterns across the application.

## Table of Contents

- [Key Concepts](#key-concepts)
- [Architecture](#architecture)
- [Component Categories](#component-categories)
- [Component Inventory](#component-inventory)
- [Usage Patterns](#usage-patterns)
- [Best Practices](#best-practices)
- [Accessibility](#accessibility)
- [Related Documentation](#related-documentation)

## Key Concepts

**Component**: A reusable, self-contained UI element that encapsulates structure, styling, and behavior.

**Props**: Input parameters that customize component appearance and functionality.

**Events**: Custom events dispatched by components for parent-child communication.

**Slots**: Content injection points that allow flexible component composition.

**Actions**: Svelte actions for DOM manipulation and third-party integrations.

## Architecture

### Component Structure

```
frontend-svelte/
├── src/
│   ├── lib/
│   │   ├── components/          # Reusable components
│   │   │   ├── Button.svelte
│   │   │   ├── Navbar.svelte
│   │   │   └── ...
│   │   ├── stores/             # Global state management
│   │   ├── services/           # API and utilities
│   │   └── actions/            # Svelte actions
│   └── routes/                 # Page components
```

### Design Principles

1. **Single Responsibility**: Each component has one clear purpose
2. **Composability**: Components can be combined to create complex UIs
3. **Accessibility First**: WCAG 2.1 AA compliance built-in
4. **Performance**: Lazy loading and efficient re-rendering
5. **Type Safety**: JSDoc annotations for prop validation

## Component Categories

### 1. Layout Components
Core structural components that define page layout and navigation.

- **Navbar**: Fixed navigation header with responsive mobile menu
- **Footer**: Site-wide footer with links and branding
- **Hero**: Page header sections with gradients and content slots
- **Container**: Responsive width containers for content

### 2. Interactive Components
User interaction elements with state management and event handling.

- **Button**: Versatile button with multiple variants and states
- **Toast**: Non-blocking notification system
- **ProgressIndicator**: Multi-step progress visualization
- **ModelCard**: Interactive 3D model preview cards

### 3. Display Components
Presentational components for content display.

- **Icon**: SVG icon system with 30+ built-in icons
- **ImageGrid**: Responsive image gallery with actions
- **Breadcrumb**: Navigation breadcrumb trail
- **ErrorBoundary**: Error state handling wrapper

## Component Inventory

### Button Component
**Location**: `src/lib/components/Button.svelte`

**Purpose**: Primary interactive element for user actions across the application.

**Props**:
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'primary' \| 'secondary' \| 'ghost' \| 'ghost-light'` | `'primary'` | Visual style variant |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Button size |
| `disabled` | `boolean` | `false` | Disable interaction |
| `type` | `string` | `'button'` | HTML button type |
| `href` | `string \| null` | `null` | Render as link if provided |
| `fullWidth` | `boolean` | `false` | Take full container width |
| `loading` | `boolean` | `false` | Show loading spinner |

**Events**: `click`

**Example**:
```svelte
<Button 
  variant="primary" 
  size="lg"
  on:click={handleSubmit}
>
  Submit Form
</Button>
```

### Navbar Component
**Location**: `src/lib/components/Navbar.svelte`

**Purpose**: Site-wide navigation with responsive mobile menu and smooth scroll support.

**Props**:
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'default' \| 'landing'` | `'default'` | Navigation style variant |

**Features**:
- Fixed positioning with backdrop blur
- Mobile hamburger menu with animation
- Smooth scroll for anchor links
- Logo and brand integration

### Footer Component
**Location**: `src/lib/components/Footer.svelte`

**Purpose**: Consistent site-wide footer with branding and navigation links.

**Props**: None (uses static content)

**Structure**:
- Brand section with logo and tagline
- Quick navigation links
- Copyright information
- Responsive mobile layout

### Toast Component
**Location**: `src/lib/components/Toast.svelte`

**Purpose**: Non-blocking notification system for user feedback.

**Store Integration**: Uses `$lib/stores/toast.js` for global state

**Toast Types**:
- `SUCCESS`: Green checkmark icon
- `ERROR`: Red X icon  
- `WARNING`: Yellow warning triangle
- `INFO`: Blue info circle

**Features**:
- Auto-dismiss after 5 seconds
- Manual dismiss option
- Stacking support for multiple toasts
- Accessible with ARIA live regions

### ProgressIndicator Component
**Location**: `src/lib/components/ProgressIndicator.svelte`

**Purpose**: Visual representation of multi-step processes.

**Props**:
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `currentStep` | `number` | `1` | Active step (1-3) |

**Steps**: Upload → Process → Download

### Icon Component
**Location**: `src/lib/components/Icon.svelte`

**Purpose**: Centralized SVG icon system with consistent styling.

**Props**:
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `string` | required | Icon identifier |
| `size` | `number` | `24` | Icon size in pixels |
| `color` | `string` | `'currentColor'` | Icon color |
| `class` | `string` | `''` | Additional CSS classes |

**Available Icons**:
- UI: `check`, `x`, `eye`, `external-link`, `chevron-down`
- File: `folder`, `document`, `download`, `upload`
- Status: `info`, `warning`, `error`, `clock`
- 3D: `cube`
- Utility: `cog`, `key`

### ModelCard Component
**Location**: `src/lib/components/ModelCard.svelte`

**Purpose**: Display 3D model files with preview, metadata, and actions.

**Props**:
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `file` | `Object` | required | File data object |
| `jobId` | `string` | required | Associated job ID |
| `onDownload` | `Function` | `null` | Download callback |
| `onPreview` | `Function` | `null` | Preview callback |

**Events**: `download`, `preview`

### ImageGrid Component
**Location**: `src/lib/components/ImageGrid.svelte`

**Purpose**: Responsive grid layout for image collections with actions.

**Props**:
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `items` | `Array` | required | Image data array |
| `onRemove` | `Function` | required | Remove callback |
| `gridSize` | `string` | `'medium'` | Grid density |

### Hero Component
**Location**: `src/lib/components/Hero.svelte`

**Purpose**: Page header sections with gradient backgrounds and flexible content.

**Props**:
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | required | Main heading text |
| `subtitle` | `string` | optional | Supporting text |

**Slots**:
- `content`: Additional content below title/subtitle

### Breadcrumb Component
**Location**: `src/lib/components/Breadcrumb.svelte`

**Purpose**: Navigation trail showing current page context.

**Props**:
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `items` | `Array<{label, href?, current?}>` | required | Breadcrumb items |

### ErrorBoundary Component
**Location**: `src/lib/components/ErrorBoundary.svelte`

**Purpose**: Graceful error handling wrapper for component trees.

**Features**:
- Catches JavaScript errors
- Displays user-friendly error state
- Logs errors for debugging
- Retry functionality

## Usage Patterns

### Component Composition
```svelte
<Hero title="Upload Your Images" subtitle="Transform photos into 3D models">
  <div slot="content">
    <ProgressIndicator currentStep={1} />
  </div>
</Hero>
```

### Event Handling
```svelte
<script>
  import { toast } from '$lib/stores/toast';
  
  function handleClick() {
    toast.success('Action completed!');
  }
</script>

<Button on:click={handleClick}>Click Me</Button>
```

### Conditional Rendering
```svelte
{#if loading}
  <Button loading disabled>Processing...</Button>
{:else}
  <Button variant="primary">Submit</Button>
{/if}
```

## Best Practices

### ✅ DO

- Use semantic HTML elements within components
- Provide meaningful ARIA labels for interactive elements
- Test components with keyboard navigation
- Use CSS custom properties for theming
- Implement proper loading and error states
- Document all props with JSDoc comments

### ❌ DON'T

- Hard-code colors or dimensions
- Ignore accessibility requirements
- Create components with multiple responsibilities
- Use inline styles for component styling
- Skip prop validation
- Forget to clean up event listeners

## Accessibility

All components follow WCAG 2.1 AA guidelines:

### Color Contrast
- Primary buttons: 4.5:1 ratio (AA compliant)
- Text on backgrounds: 12.1:1 ratio (AAA compliant)
- Interactive elements: 3:1 minimum for focus indicators

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Focus indicators meet 3:1 contrast ratio
- Tab order follows logical flow
- Skip links for main content

### Screen Reader Support
- Semantic HTML structure
- ARIA labels for icons and buttons
- Live regions for dynamic content
- Proper heading hierarchy

### Testing Checklist
- [ ] Keyboard navigation works correctly
- [ ] Focus indicators are visible
- [ ] Screen reader announces content properly
- [ ] Color contrast meets standards
- [ ] Interactive elements have appropriate size
- [ ] Error messages are accessible

## Related Documentation

- [Button System](./button-system.md) - Detailed button component guide
- [Form Components](./form-components.md) - Form and input components
- [Layout Components](./layout-components.md) - Page structure components
- [Brand Guidelines](../../../brand/guidelines/accessibility.md) - Accessibility standards
- [CSS Architecture](../styling/css-architecture.md) - Styling patterns
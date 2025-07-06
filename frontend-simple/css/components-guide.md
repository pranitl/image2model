# Component Design System Guide

## Overview

The Image2Model Component Design System provides a comprehensive set of UI components that follow our brand guidelines and ensure consistency across the application.

## Quick Start

### Including the Components

```html
<!-- Include after variables.css and typography.css -->
<link rel="stylesheet" href="css/components.css">
<script src="js/components.js"></script>
```

## Components

### 1. Buttons

#### Basic Usage

```html
<!-- Primary Button -->
<button class="btn btn-primary">Primary Action</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">Secondary Action</button>

<!-- Ghost Button -->
<button class="btn btn-ghost">Ghost Button</button>
```

#### Button Sizes

```html
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>
```

#### Icon Buttons

```html
<button class="btn btn-primary btn-icon" aria-label="Settings">
    <svg><!-- icon --></svg>
</button>
```

#### Button States

```html
<!-- Disabled -->
<button class="btn btn-primary" disabled>Disabled</button>

<!-- Loading -->
<button class="btn btn-primary btn-loading">Loading...</button>
```

#### Button Groups

```html
<div class="btn-group">
    <button class="btn btn-secondary">Left</button>
    <button class="btn btn-secondary">Center</button>
    <button class="btn btn-secondary">Right</button>
</div>
```

### 2. Forms

#### Text Inputs

```html
<div class="form-group">
    <label class="form-label">Label</label>
    <input type="text" class="form-input" placeholder="Enter text...">
    <span class="form-help">Help text</span>
</div>

<!-- Required field -->
<label class="form-label form-label-required">Required Field</label>

<!-- Error state -->
<input type="text" class="form-input form-input-error">
<span class="form-help form-error">Error message</span>
```

#### File Upload

```html
<div class="form-file-upload">
    <input type="file" multiple accept="image/*">
    <svg class="form-file-upload-icon"><!-- icon --></svg>
    <p class="form-file-upload-text">Drop files here or click to upload</p>
    <p class="form-file-upload-hint">PNG, JPG up to 10MB</p>
    <div class="file-list"></div>
</div>
```

#### Checkboxes & Radio

```html
<label class="form-checkbox">
    <input type="checkbox">
    <span class="form-checkbox-label">Option</span>
</label>

<label class="form-radio">
    <input type="radio" name="group">
    <span class="form-radio-label">Option</span>
</label>
```

### 3. Cards

#### Basic Card

```html
<div class="card">
    <div class="card-header">
        <h3>Card Title</h3>
    </div>
    <div class="card-body">
        <p>Card content</p>
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">Action</button>
    </div>
</div>
```

#### Image Card

```html
<div class="card card-image">
    <img src="image.jpg" alt="Description">
    <div class="card-image-overlay">
        <h3>Overlay Title</h3>
    </div>
    <div class="card-body">
        <p>Content</p>
    </div>
</div>
```

#### File Card

```html
<div class="card card-file">
    <div class="card-file-icon">
        <svg><!-- icon --></svg>
    </div>
    <div class="card-file-info">
        <div class="card-file-name">filename.png</div>
        <div class="card-file-meta">2.4 MB • image/png</div>
    </div>
    <div class="card-file-actions">
        <button class="btn btn-ghost btn-sm btn-icon"><!-- actions --></button>
    </div>
</div>
```

### 4. Feedback Components

#### Alerts

```html
<div class="alert alert-success">
    <svg class="alert-icon"><!-- icon --></svg>
    <div class="alert-content">
        <div class="alert-title">Success!</div>
        <div class="alert-message">Operation completed.</div>
    </div>
</div>

<!-- Variants: alert-success, alert-error, alert-warning, alert-info -->
```

#### Toast Notifications

```javascript
// Show a toast notification
Components.showToast('Message', 'success');
// Types: 'success', 'error', 'warning', 'info'
```

#### Progress Bar

```html
<div class="progress-label">
    <span>Progress</span>
    <span>75%</span>
</div>
<div class="progress">
    <div class="progress-bar" style="width: 75%"></div>
</div>
```

#### Loading Spinner

```html
<div class="spinner"></div>
<div class="spinner spinner-sm"></div>
<div class="spinner spinner-lg"></div>
```

### 5. Navigation

#### Navbar

```html
<nav class="navbar">
    <div class="navbar-container">
        <a href="#" class="navbar-brand">Brand</a>
        <ul class="navbar-menu">
            <li><a href="#" class="navbar-link">Link</a></li>
            <li><a href="#" class="navbar-link active">Active</a></li>
        </ul>
    </div>
</nav>
```

#### Breadcrumbs

```html
<nav class="breadcrumb">
    <span class="breadcrumb-item"><a href="#">Home</a></span>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-item active">Current</span>
</nav>
```

#### Tabs

```html
<div class="tabs">
    <ul class="tab-list" role="tablist">
        <li role="presentation">
            <button class="tab-button active" role="tab">Tab 1</button>
        </li>
        <li role="presentation">
            <button class="tab-button" role="tab">Tab 2</button>
        </li>
    </ul>
</div>
<div class="tab-content">
    <div class="tab-panel active" role="tabpanel">Content 1</div>
    <div class="tab-panel" role="tabpanel">Content 2</div>
</div>
```

### 6. Modals

#### Basic Modal

```html
<button data-modal-open="my-modal">Open Modal</button>

<div class="modal-overlay" id="my-modal" aria-hidden="true">
    <div class="modal" role="dialog">
        <div class="modal-header">
            <h3 class="modal-title">Title</h3>
            <button class="modal-close" data-modal-close>×</button>
        </div>
        <div class="modal-body">
            <p>Content</p>
        </div>
        <div class="modal-footer">
            <button class="btn btn-ghost" data-modal-close>Cancel</button>
            <button class="btn btn-primary">Save</button>
        </div>
    </div>
</div>
```

#### JavaScript API

```javascript
// Open modal
Components.openModal('modal-id');

// Close modal
Components.closeModal('modal-id');
```

## Accessibility

All components follow WCAG 2.1 AA standards:

- Proper ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader compatibility
- Minimum touch targets (44x44px)

## Dark Mode

The component system fully supports dark mode:

- Automatic detection of system preference
- Manual toggle option
- Smooth transitions
- Optimized color contrasts

## Customization

Components use CSS custom properties for easy customization:

```css
/* Override in your stylesheet */
:root {
    --btn-primary-bg: /* your color */;
    --card-shadow: /* your shadow */;
}
```

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Android)

## Best Practices

1. **Consistency**: Use the provided components instead of creating custom ones
2. **Accessibility**: Always include proper ARIA labels
3. **Responsive**: Components are mobile-first and responsive by default
4. **Performance**: Load only the components you need
5. **Theming**: Use CSS variables for customization

## Migration Guide

If updating from custom components:

1. Replace custom button classes with `.btn` variants
2. Update form elements to use `.form-*` classes
3. Convert custom cards to `.card` structure
4. Use the JavaScript API for modals and toasts
5. Test in both light and dark modes
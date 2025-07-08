/**
 * Advanced example showing how visibility utilities scale to complex scenarios
 * This demonstrates testing nested components, conditional rendering, and dynamic content
 */

import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/svelte';
import {
  isElementVisible,
  expectSectionsToBeVisible,
  expectContentToBeAccessible,
  testAnimationErrorResilience
} from '../lib/visibility-test-utils.js';

// Example: Dashboard with multiple dynamic sections
describe('Complex Dashboard Visibility', () => {
  const MockDashboard = {
    render: () => {
      return {
        html: `
          <div class="dashboard">
            <aside class="sidebar" id="sidebar">
              <nav class="sidebar-nav">
                <a href="#models">My Models</a>
                <a href="#analytics">Analytics</a>
                <a href="#settings">Settings</a>
              </nav>
            </aside>
            
            <main class="dashboard-content">
              <section id="models" class="models-section">
                <h2>My 3D Models</h2>
                <div class="models-grid" data-stagger>
                  <div class="model-card" data-stagger>
                    <img src="/model1.jpg" alt="Model 1">
                    <h3>Product Model 1</h3>
                    <div class="model-actions">
                      <button>Download</button>
                      <button>Share</button>
                    </div>
                  </div>
                  <div class="model-card" data-stagger>
                    <img src="/model2.jpg" alt="Model 2">
                    <h3>Product Model 2</h3>
                    <div class="model-actions">
                      <button>Download</button>
                      <button>Share</button>
                    </div>
                  </div>
                </div>
                
                <!-- Conditional empty state -->
                <div class="empty-state" style="display: none;">
                  <p>No models yet. Upload your first image!</p>
                  <button>Upload Image</button>
                </div>
              </section>
              
              <section id="analytics" class="analytics-section">
                <h2>Usage Analytics</h2>
                <div class="analytics-cards">
                  <div class="stat-card">
                    <span class="stat-value">15</span>
                    <span class="stat-label">Models Created</span>
                  </div>
                  <div class="stat-card">
                    <span class="stat-value">1.2GB</span>
                    <span class="stat-label">Storage Used</span>
                  </div>
                </div>
                <div class="chart-container">
                  <canvas id="usage-chart"></canvas>
                </div>
              </section>
            </main>
            
            <!-- Notification system -->
            <div class="notifications">
              <div class="notification success">
                Model processed successfully!
              </div>
            </div>
          </div>
        `
      };
    }
  };

  it('should display all main dashboard sections', () => {
    const { container } = render(MockDashboard);
    
    // Test main structural sections
    expectSectionsToBeVisible(container, [
      '#sidebar',
      '#models',
      '#analytics'
    ]);
  });

  it('should show navigation and content correctly', () => {
    const { container } = render(MockDashboard);
    
    // Navigation should be accessible
    expectContentToBeAccessible(container, [
      'My Models',
      'Analytics',
      'Settings'
    ]);
    
    // Section headers should be visible
    expectContentToBeAccessible(container, [
      'My 3D Models',
      'Usage Analytics'
    ]);
  });

  it('should display model cards when models exist', () => {
    const { container } = render(MockDashboard);
    
    // Model cards should be visible
    const modelCards = container.querySelectorAll('.model-card');
    expect(modelCards.length).toBe(2);
    
    modelCards.forEach(card => {
      expect(isElementVisible(card)).toBe(true);
    });
    
    // Model content should be accessible
    expectContentToBeAccessible(container, [
      'Product Model 1',
      'Product Model 2',
      'Download',
      'Share'
    ]);
  });

  it('should hide empty state when models exist', () => {
    const { container } = render(MockDashboard);
    
    const emptyState = container.querySelector('.empty-state');
    expect(emptyState).toBeTruthy();
    
    // Empty state should be hidden when models exist
    expect(isElementVisible(emptyState)).toBe(false);
  });

  it('should show analytics data', () => {
    const { container } = render(MockDashboard);
    
    // Analytics cards should be visible
    const statCards = container.querySelectorAll('.stat-card');
    statCards.forEach(card => {
      expect(isElementVisible(card)).toBe(true);
    });
    
    // Analytics content should be accessible
    expectContentToBeAccessible(container, [
      '15',
      'Models Created',
      '1.2GB',
      'Storage Used'
    ]);
  });

  it('should display notifications when present', () => {
    const { container } = render(MockDashboard);
    
    const notification = container.querySelector('.notification');
    expect(isElementVisible(notification)).toBe(true);
    
    // Notification content should be accessible
    expectContentToBeAccessible(container, [
      'Model processed successfully!'
    ]);
  });
});

// Example: Wizard/Multi-step form visibility
describe('Multi-Step Form Visibility', () => {
  const MockWizard = {
    render: () => {
      return {
        html: `
          <div class="wizard">
            <div class="wizard-steps">
              <div class="step active">1. Upload</div>
              <div class="step">2. Configure</div>
              <div class="step">3. Review</div>
            </div>
            
            <!-- Step 1: Active -->
            <div class="wizard-content" data-step="1">
              <h2>Upload Your Images</h2>
              <div class="upload-area">
                <p>Drag and drop files here</p>
                <button>Browse Files</button>
              </div>
            </div>
            
            <!-- Step 2: Hidden -->
            <div class="wizard-content" data-step="2" style="display: none;">
              <h2>Configure Settings</h2>
              <form>
                <label>Model Quality</label>
                <select>
                  <option>High</option>
                  <option>Medium</option>
                  <option>Low</option>
                </select>
              </form>
            </div>
            
            <!-- Step 3: Hidden -->
            <div class="wizard-content" data-step="3" style="display: none;">
              <h2>Review & Generate</h2>
              <div class="summary">
                <p>Files: 3 images</p>
                <p>Quality: High</p>
              </div>
              <button>Generate 3D Model</button>
            </div>
            
            <div class="wizard-navigation">
              <button disabled>Previous</button>
              <button>Next</button>
            </div>
          </div>
        `
      };
    }
  };

  it('should show only active step content', () => {
    const { container } = render(MockWizard);
    
    // Step 1 should be visible
    const step1 = container.querySelector('[data-step="1"]');
    expect(isElementVisible(step1)).toBe(true);
    
    // Steps 2 and 3 should be hidden
    const step2 = container.querySelector('[data-step="2"]');
    const step3 = container.querySelector('[data-step="3"]');
    expect(isElementVisible(step2)).toBe(false);
    expect(isElementVisible(step3)).toBe(false);
  });

  it('should show step indicators', () => {
    const { container } = render(MockWizard);
    
    const steps = container.querySelectorAll('.wizard-steps .step');
    expect(steps.length).toBe(3);
    
    steps.forEach(step => {
      expect(isElementVisible(step)).toBe(true);
    });
  });

  it('should show correct content for active step', () => {
    const { container } = render(MockWizard);
    
    // Only step 1 content should be accessible
    expectContentToBeAccessible(container, [
      'Upload Your Images',
      'Drag and drop files here',
      'Browse Files'
    ]);
    
    // Step 2 and 3 content should not be visible
    // Note: expectContentToBeAccessible finds text even in hidden elements
    // For strict visibility, we check the containers
    const hiddenSections = container.querySelectorAll('[data-step="2"], [data-step="3"]');
    hiddenSections.forEach(section => {
      expect(isElementVisible(section)).toBe(false);
    });
  });
});

// Example: Testing responsive visibility
describe('Responsive Component Visibility', () => {
  const MockResponsiveNav = {
    render: () => {
      return {
        html: `
          <nav class="responsive-nav">
            <!-- Desktop menu -->
            <ul class="desktop-menu">
              <li><a href="/">Home</a></li>
              <li><a href="/about">About</a></li>
              <li><a href="/contact">Contact</a></li>
            </ul>
            
            <!-- Mobile menu button -->
            <button class="mobile-menu-toggle" style="display: none;">
              Menu
            </button>
            
            <!-- Mobile menu (hidden by default) -->
            <div class="mobile-menu" style="display: none;">
              <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
              </ul>
            </div>
          </nav>
        `
      };
    }
  };

  it('should show desktop menu on desktop viewport', () => {
    const { container } = render(MockResponsiveNav);
    
    const desktopMenu = container.querySelector('.desktop-menu');
    const mobileToggle = container.querySelector('.mobile-menu-toggle');
    const mobileMenu = container.querySelector('.mobile-menu');
    
    // Desktop menu visible, mobile elements hidden
    expect(isElementVisible(desktopMenu)).toBe(true);
    expect(isElementVisible(mobileToggle)).toBe(false);
    expect(isElementVisible(mobileMenu)).toBe(false);
  });
});

// Example: Testing loading states and skeletons
describe('Loading State Visibility', () => {
  const MockLoadingComponent = {
    render: () => {
      return {
        html: `
          <div class="content-area">
            <!-- Loading skeleton -->
            <div class="skeleton-loader">
              <div class="skeleton-header"></div>
              <div class="skeleton-text"></div>
              <div class="skeleton-text"></div>
            </div>
            
            <!-- Actual content (hidden while loading) -->
            <div class="actual-content" style="display: none;">
              <h2>Loaded Content</h2>
              <p>This is the real content that appears after loading.</p>
            </div>
            
            <!-- Error state (hidden by default) -->
            <div class="error-state" style="display: none;">
              <p>Failed to load content</p>
              <button>Retry</button>
            </div>
          </div>
        `
      };
    }
  };

  it('should show skeleton loader during loading', () => {
    const { container } = render(MockLoadingComponent);
    
    const skeleton = container.querySelector('.skeleton-loader');
    const content = container.querySelector('.actual-content');
    const error = container.querySelector('.error-state');
    
    // Only skeleton should be visible during loading
    expect(isElementVisible(skeleton)).toBe(true);
    expect(isElementVisible(content)).toBe(false);
    expect(isElementVisible(error)).toBe(false);
  });
});

/**
 * These examples demonstrate:
 * 
 * 1. **Complex nested structures** - Dashboard with sidebar, main content, and notifications
 * 2. **Conditional rendering** - Empty states, active/inactive wizard steps
 * 3. **Dynamic content** - Model cards that may or may not exist
 * 4. **Responsive design** - Different elements visible at different viewports
 * 5. **Loading states** - Skeletons, content, and error states
 * 
 * The generic utilities handle all these cases, making tests:
 * - Readable and maintainable
 * - Reusable across different components
 * - Consistent in their approach
 * - Easy to extend for new scenarios
 */
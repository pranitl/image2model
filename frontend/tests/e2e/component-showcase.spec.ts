import { test, expect } from '@playwright/test';

test.describe('Component Showcase', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/showcase');
  });

  test('should display all component sections', async ({ page }) => {
    // Check main heading
    await expect(page.getByRole('heading', { name: 'Component Showcase' })).toBeVisible();
    
    // Check section headings
    await expect(page.getByRole('heading', { name: 'Button Components' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Card Components' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Progress Components' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Toast Components' })).toBeVisible();
  });

  test('should test button variants and interactions', async ({ page }) => {
    // Test default button
    const defaultButton = page.getByRole('button', { name: 'Default' });
    await expect(defaultButton).toBeVisible();
    await expect(defaultButton).toBeEnabled();
    
    // Test button hover states
    await defaultButton.hover();
    
    // Test destructive button
    const destructiveButton = page.getByRole('button', { name: 'Destructive' });
    await expect(destructiveButton).toBeVisible();
    
    // Test loading button functionality
    const loadingButton = page.getByRole('button', { name: 'Toggle Loading' });
    await loadingButton.click();
    
    // Check if loading state is active
    await expect(page.locator('[data-loading="true"]')).toBeVisible();
  });

  test('should test card component variants', async ({ page }) => {
    // Check default card
    await expect(page.locator('.card-default')).toBeVisible();
    
    // Check elevated card
    await expect(page.locator('.card-elevated')).toBeVisible();
    
    // Test card hover effects on elevated variant
    const elevatedCard = page.locator('.card-elevated');
    await elevatedCard.hover();
  });

  test('should test progress components', async ({ page }) => {
    // Check linear progress
    await expect(page.locator('[role="progressbar"]').first()).toBeVisible();
    
    // Check circular progress
    await expect(page.locator('.circular-progress')).toBeVisible();
    
    // Test progress controls
    const increaseButton = page.getByRole('button', { name: 'Increase' });
    const decreaseButton = page.getByRole('button', { name: 'Decrease' });
    
    await increaseButton.click();
    await decreaseButton.click();
  });

  test('should test toast functionality', async ({ page }) => {
    // Test success toast
    const successButton = page.getByRole('button', { name: 'Success Toast' });
    await successButton.click();
    
    // Check if toast appears
    await expect(page.getByText('Success!')).toBeVisible();
    
    // Test error toast
    const errorButton = page.getByRole('button', { name: 'Error Toast' });
    await errorButton.click();
    
    await expect(page.getByText('Error occurred!')).toBeVisible();
  });

  test('should test dark mode toggle', async ({ page }) => {
    const darkModeToggle = page.getByRole('button', { name: /dark mode/i });
    await expect(darkModeToggle).toBeVisible();
    
    // Toggle dark mode
    await darkModeToggle.click();
    
    // Check if dark class is applied to html element
    await expect(page.locator('html')).toHaveClass(/dark/);
    
    // Toggle back to light mode
    await darkModeToggle.click();
    await expect(page.locator('html')).not.toHaveClass(/dark/);
  });

  test('should test accessibility features', async ({ page }) => {
    // Test keyboard navigation on buttons
    await page.keyboard.press('Tab');
    await expect(page.getByRole('button').first()).toBeFocused();
    
    // Test ARIA attributes
    const progressBar = page.locator('[role="progressbar"]').first();
    await expect(progressBar).toHaveAttribute('aria-valuemin');
    await expect(progressBar).toHaveAttribute('aria-valuemax');
    await expect(progressBar).toHaveAttribute('aria-valuenow');
  });
  
  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check if components are still visible and functional
    await expect(page.getByRole('heading', { name: 'Component Showcase' })).toBeVisible();
    
    // Test button interactions on mobile
    const button = page.getByRole('button', { name: 'Default' });
    await button.tap();
  });
});
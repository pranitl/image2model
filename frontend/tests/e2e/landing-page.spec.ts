import { test, expect } from '@playwright/test';

test.describe('Landing Page - Task 7', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display hero section with correct content', async ({ page }) => {
    // Check main heading
    await expect(page.getByRole('heading', { name: 'Transform Images to 3D Models' })).toBeVisible();
    
    // Check description text
    await expect(page.getByText('Upload any image and get a professional 3D model in minutes')).toBeVisible();
    
    // Check CTA button
    const ctaButton = page.getByRole('button', { name: 'Start Creating' });
    await expect(ctaButton).toBeVisible();
    await expect(ctaButton).toBeEnabled();
  });

  test('should display How It Works section with all steps', async ({ page }) => {
    // Check section heading
    await expect(page.getByRole('heading', { name: 'How It Works' })).toBeVisible();
    
    // Check all workflow steps
    await expect(page.getByText('Upload Image')).toBeVisible();
    await expect(page.getByText('AI Processing')).toBeVisible(); 
    await expect(page.getByText('Generate Model')).toBeVisible();
    await expect(page.getByText('Download & Use')).toBeVisible();
    
    // Check step descriptions
    await expect(page.getByText('Simply upload your image and let our AI analyze it')).toBeVisible();
    await expect(page.getByText('Advanced AI algorithms process your image')).toBeVisible();
    await expect(page.getByText('Watch as your 2D image transforms')).toBeVisible();
    await expect(page.getByText('Download your 3D model in multiple formats')).toBeVisible();
  });

  test('should be responsive on different screen sizes', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.getByRole('heading', { name: 'Transform Images to 3D Models' })).toBeVisible();
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.getByRole('heading', { name: 'Transform Images to 3D Models' })).toBeVisible();
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1366, height: 768 });
    await expect(page.getByRole('heading', { name: 'Transform Images to 3D Models' })).toBeVisible();
  });

  test('should have proper navigation functionality', async ({ page }) => {
    // Test CTA button navigation
    const ctaButton = page.getByRole('button', { name: 'Start Creating' });
    await ctaButton.click();
    
    // Should navigate to upload page
    await expect(page).toHaveURL('/upload');
  });

  test('should have animations and proper styling', async ({ page }) => {
    // Wait for page to load and animations to trigger
    await page.waitForTimeout(1000);
    
    // Check that hero section is visible (animations should have completed)
    const heroSection = page.locator('section').first();
    await expect(heroSection).toBeVisible();
    
    // Check that workflow section is visible
    const workflowSection = page.locator('section').nth(1);
    await expect(workflowSection).toBeVisible();
    
    // Verify grid layout for workflow steps
    const stepGrid = page.locator('div.grid');
    await expect(stepGrid).toBeVisible();
  });

  test('should have proper accessibility features', async ({ page }) => {
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    const ctaButton = page.getByRole('button', { name: 'Start Creating' });
    await expect(ctaButton).toBeFocused();
    
    // Test heading hierarchy
    const h1 = page.getByRole('heading', { level: 1 });
    await expect(h1).toHaveText('Transform Images to 3D Models');
    
    const h2 = page.getByRole('heading', { level: 2 });
    await expect(h2).toHaveText('How It Works');
  });

  test('should display above-fold content at 1366x768', async ({ page }) => {
    // Set to the specified test viewport
    await page.setViewportSize({ width: 1366, height: 768 });
    
    // Check that hero content is visible without scrolling
    await expect(page.getByRole('heading', { name: 'Transform Images to 3D Models' })).toBeInViewport();
    await expect(page.getByText('Upload any image and get a professional 3D model in minutes')).toBeInViewport();
    await expect(page.getByRole('button', { name: 'Start Creating' })).toBeInViewport();
  });
});
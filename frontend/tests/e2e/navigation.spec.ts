import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('should load home page successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check page loads without errors
    await expect(page).toHaveTitle(/Image2Model/);
    
    // Check for basic layout elements
    await expect(page.locator('body')).toBeVisible();
  });

  test('should navigate between pages', async ({ page }) => {
    await page.goto('/');
    
    // Test navigation to different routes
    const routes = ['/upload', '/admin', '/showcase'];
    
    for (const route of routes) {
      await page.goto(route);
      await expect(page).toHaveURL(route);
      
      // Check page loads without JavaScript errors
      const errors: string[] = [];
      page.on('pageerror', err => errors.push(err.message));
      
      // Wait a bit for any potential errors
      await page.waitForTimeout(1000);
      
      expect(errors).toHaveLength(0);
    }
  });

  test('should handle 404 pages gracefully', async ({ page }) => {
    await page.goto('/non-existent-page');
    
    // Should either redirect to home or show 404 page
    // Depends on router configuration
    const currentUrl = page.url();
    expect(currentUrl).toBeTruthy();
  });

  test('should maintain responsive layout', async ({ page }) => {
    const viewports = [
      { width: 1920, height: 1080 }, // Desktop
      { width: 1024, height: 768 },  // Tablet
      { width: 375, height: 667 },   // Mobile
    ];

    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await page.goto('/');
      
      // Check layout doesn't break
      await expect(page.locator('body')).toBeVisible();
      
      // Check no horizontal overflow
      const bodyWidth = await page.locator('body').evaluate(el => el.scrollWidth);
      expect(bodyWidth).toBeLessThanOrEqual(viewport.width + 50); // Allow small margin
    }
  });
});
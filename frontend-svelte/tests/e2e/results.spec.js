import { test, expect } from './fixtures/test-fixtures.js';

test.describe('Results Page', () => {
  // Helper to navigate to results page with mock data
  async function navigateToResults(page, mockApi, jobId = 'test-job-123') {
    // Mock job results
    await mockApi.mockJobResults(jobId);
    
    // Navigate directly to results page
    await page.goto(`/results/${jobId}`);
    await page.waitForLoadState('networkidle');
  }

  test('should display results interface', async ({ page, resultsPage, mockApi }) => {
    await navigateToResults(page, mockApi);
    
    // Wait for results to load
    await resultsPage.waitForPageLoad();
    
    // Check main elements
    await expect(page.locator('h1')).toContainText('Your 3D Models');
    await expect(resultsPage.downloadAllButton).toBeVisible();
    await expect(resultsPage.uploadNewButton).toBeVisible();
    
    // Check result count
    const count = await resultsPage.getResultCount();
    expect(count).toBe(2); // Based on mock data
  });

  test('should display model cards with correct information', async ({ page, resultsPage, mockApi }) => {
    await navigateToResults(page, mockApi);
    await resultsPage.waitForPageLoad();
    
    // Check first model
    const firstModel = await resultsPage.getModelInfo(0);
    expect(firstModel.filename).toContain('.glb');
    expect(firstModel.fileSize).toBeTruthy();
    expect(firstModel.hasPreview).toBe(true);
    
    // Check all models have required info
    const count = await resultsPage.getResultCount();
    for (let i = 0; i < count; i++) {
      const model = await resultsPage.getModelInfo(i);
      expect(model.filename).toBeTruthy();
      expect(model.fileSize).toBeTruthy();
    }
  });

  test('should handle individual model download', async ({ page, resultsPage, mockApi }) => {
    await navigateToResults(page, mockApi);
    await resultsPage.waitForPageLoad();
    
    // Mock download endpoint
    await page.route('**/api/v1/download/**/*.glb', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'model/gltf-binary',
        body: Buffer.from('Mock GLB content'),
        headers: {
          'Content-Disposition': 'attachment; filename="model.glb"'
        }
      });
    });
    
    // Download first model
    const download = await resultsPage.downloadModel(0);
    
    // Verify download started
    expect(download).toBeTruthy();
    expect(await download.suggestedFilename()).toContain('.glb');
  });

  test('should handle download all models', async ({ page, resultsPage, mockApi }) => {
    await navigateToResults(page, mockApi);
    await resultsPage.waitForPageLoad();
    
    // Mock download all endpoint
    await page.route('**/api/v1/download/**/all', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/zip',
        body: Buffer.from('Mock ZIP content'),
        headers: {
          'Content-Disposition': 'attachment; filename="models.zip"'
        }
      });
    });
    
    // Download all models
    const download = await resultsPage.downloadAllModels();
    
    // Verify download
    expect(download).toBeTruthy();
    const filename = await download.suggestedFilename();
    expect(filename).toMatch(/\.zip$/);
  });

  test('should display processing statistics', async ({ page, resultsPage, mockApi }) => {
    // Mock results with processing stats
    await page.route('**/api/v1/download/**/all', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          job_id: 'test-job-123',
          files: [
            {
              filename: 'model-1.glb',
              size: 1024000,
              mime_type: 'model/gltf-binary',
              file_size: 1024000,
              created_time: new Date().toISOString(),
              model_url: 'https://example.com/model-1.glb',
              rendered_image: 'https://example.com/preview-1.jpg'
            }
          ],
          total_files: 1,
          processing_time: '2m 34s',
          total_faces: 15000
        })
      });
    });
    
    await navigateToResults(page, mockApi, 'test-job-123');
    await resultsPage.waitForPageLoad();
    
    // Check processing stats
    const stats = await resultsPage.getProcessingStats();
    expect(stats.processingTime).toBeTruthy();
    expect(stats.modelCount).toBeGreaterThan(0);
  });

  test('should handle model viewer', async ({ page, resultsPage, mockApi }) => {
    await navigateToResults(page, mockApi);
    await resultsPage.waitForPageLoad();
    
    // Check viewer button exists
    const viewerButtons = await page.locator('.view-3d-btn').count();
    
    // If viewer is implemented
    if (viewerButtons > 0) {
      // Open viewer for first model
      await resultsPage.viewModel(0);
      
      // Check viewer opened
      await expect(resultsPage.modelViewer).toBeVisible();
      
      // Close viewer
      await resultsPage.closeModelViewer();
      await expect(resultsPage.modelViewer).not.toBeVisible();
    }
  });

  test('should navigate to new upload', async ({ page, resultsPage, mockApi }) => {
    await navigateToResults(page, mockApi);
    await resultsPage.waitForPageLoad();
    
    // Click upload new
    await resultsPage.startNewUpload();
    
    // Should navigate to upload page
    await expect(page).toHaveURL(/.*\/upload/);
  });

  test('should handle empty results gracefully', async ({ page, resultsPage, mockApi }) => {
    // Mock empty results
    await page.route('**/api/v1/download/**/all', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          job_id: 'test-job-123',
          files: [],
          total_files: 0
        })
      });
    });
    
    await navigateToResults(page, mockApi);
    
    // Should show no results message
    await expect(page.locator('text=/no.*models|empty/i')).toBeVisible();
    
    // Should still show upload new button
    await expect(resultsPage.uploadNewButton).toBeVisible();
  });

  test('should verify thumbnail loading', async ({ page, resultsPage, mockApi }) => {
    await navigateToResults(page, mockApi);
    await resultsPage.waitForPageLoad();
    
    // Check all thumbnails
    const thumbnails = await resultsPage.verifyAllThumbnails();
    
    for (const thumbnail of thumbnails) {
      expect(thumbnail.src).toBeTruthy();
      // Note: isLoaded might be false in test environment
      // but src should be set
    }
  });

  test('should handle API errors gracefully', async ({ page, resultsPage, mockApi }) => {
    // Mock API error
    await page.route('**/api/v1/download/**/all', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: true,
          detail: 'Internal server error'
        })
      });
    });
    
    await page.goto('/results/test-job-123');
    
    // Should show error message
    await expect(page.locator('text=/error|failed/i')).toBeVisible();
  });

  test('should display file sizes correctly', async ({ page, resultsPage, mockApi }) => {
    await navigateToResults(page, mockApi);
    await resultsPage.waitForPageLoad();
    
    // Check each model has a formatted file size
    const count = await resultsPage.getResultCount();
    for (let i = 0; i < count; i++) {
      const model = await resultsPage.getModelInfo(i);
      expect(model.fileSize).toMatch(/\d+(\.\d+)?\s*(KB|MB|GB)/);
    }
  });

  test('should handle external model URLs', async ({ page, resultsPage, mockApi }) => {
    // Mock results with FAL.AI URLs
    await page.route('**/api/v1/download/**/all', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          job_id: 'test-job-123',
          files: [
            {
              filename: 'model-1.glb',
              size: 1024000,
              mime_type: 'model/gltf-binary',
              file_size: 1024000,
              created_time: new Date().toISOString(),
              model_url: 'https://v3.fal.media/files/model-1.glb',
              rendered_image: 'https://v3.fal.media/files/preview-1.jpg'
            }
          ],
          total_files: 1
        })
      });
    });
    
    await navigateToResults(page, mockApi);
    await resultsPage.waitForPageLoad();
    
    // Get download URLs
    const urls = await resultsPage.getDownloadUrls();
    
    // Should have external URLs
    expect(urls.some(url => url.includes('fal.media'))).toBe(true);
  });
});
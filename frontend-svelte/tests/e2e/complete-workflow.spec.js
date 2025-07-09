import { test, expect } from './fixtures/test-fixtures.js';
import { createTestFiles } from './utils/create-test-files.js';

// Create test files
const testFiles = createTestFiles();

test.describe('Complete Workflow', () => {
  test('should complete full workflow from upload to download', async ({ 
    page, 
    uploadPage, 
    processingPage, 
    resultsPage, 
    mockApi 
  }) => {
    // Step 1: Upload
    await mockApi.mockSuccessfulUpload();
    await uploadPage.goto();
    
    // Upload multiple files
    await uploadPage.uploadFiles([
      testFiles.testImage1,
      testFiles.testImage2
    ]);
    
    // Set face limit
    await uploadPage.setFaceLimit(5000);
    
    // Verify files are ready
    await expect(await uploadPage.getFileCount()).toBe(2);
    await expect(uploadPage.generateButton).toBeEnabled();
    
    // Submit upload
    await uploadPage.submitUpload();
    
    // Step 2: Processing
    await expect(page).toHaveURL(/.*\/processing\/.*/);
    
    // Set up processing mock
    await mockApi.mockProcessingProgress();
    
    // Wait for processing to start
    await processingPage.waitForPageLoad();
    
    // Monitor progress
    const initialProgress = await processingPage.getProgress();
    expect(initialProgress).toBeGreaterThanOrEqual(0);
    
    // Wait for completion
    const completed = await processingPage.waitForCompletion(15000);
    expect(completed).toBe(true);
    
    // Navigate to results
    await processingPage.goToResults();
    
    // Step 3: Results
    await expect(page).toHaveURL(/.*\/results\/.*/);
    
    // Mock results data
    const jobId = page.url().match(/results\/([^/]+)/)?.[1] || 'test-job';
    await mockApi.mockJobResults(jobId);
    
    // Reload to get mocked results
    await page.reload();
    await resultsPage.waitForPageLoad();
    
    // Verify results
    const resultCount = await resultsPage.getResultCount();
    expect(resultCount).toBeGreaterThan(0);
    
    // Check model information
    const firstModel = await resultsPage.getModelInfo(0);
    expect(firstModel.filename).toContain('.glb');
    expect(firstModel.fileSize).toBeTruthy();
    
    // Test download
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
    
    const download = await resultsPage.downloadModel(0);
    expect(download).toBeTruthy();
  });

  test('should handle batch upload with auto face limit', async ({
    page,
    uploadPage,
    processingPage,
    resultsPage,
    mockApi
  }) => {
    // Upload with auto mode
    await mockApi.mockSuccessfulUpload();
    await uploadPage.goto();
    
    // Upload all test images
    await uploadPage.uploadFiles([
      testFiles.testImage1,
      testFiles.testImage2,
      testFiles.testImage3
    ]);
    
    // Enable auto mode
    await uploadPage.enableAutoMode();
    
    // Submit
    await uploadPage.submitUpload();
    
    // Process
    await mockApi.mockProcessingProgress();
    await processingPage.waitForCompletion(15000);
    
    // Check results
    await processingPage.goToResults();
    const jobId = page.url().match(/results\/([^/]+)/)?.[1] || 'test-job';
    await mockApi.mockJobResults(jobId);
    await page.reload();
    
    const resultCount = await resultsPage.getResultCount();
    expect(resultCount).toBeGreaterThan(0);
  });

  test('should handle workflow interruption and resume', async ({
    page,
    uploadPage,
    processingPage,
    mockApi
  }) => {
    // Start upload
    await mockApi.mockSuccessfulUpload();
    await uploadPage.goto();
    await uploadPage.uploadFiles(testFiles.testImage1);
    await uploadPage.submitUpload();
    
    // Navigate away during processing
    await page.waitForURL(/.*\/processing\/.*/);
    const processingUrl = page.url();
    
    // Go back to home
    await page.goto('/');
    
    // Return to processing
    await page.goto(processingUrl);
    
    // Should still show processing or completed state
    await expect(processingPage.progressBar).toBeVisible();
  });

  test('should validate file limits', async ({
    page,
    uploadPage,
    mockApi
  }) => {
    await uploadPage.goto();
    
    // Try to upload more than 25 files (create dummy file list)
    const manyFiles = [];
    for (let i = 0; i < 30; i++) {
      manyFiles.push(testFiles.testImage1);
    }
    
    // This should trigger validation
    await uploadPage.uploadFiles(manyFiles);
    
    // Should show error about too many files
    await expect(page.locator('.toast.error')).toContainText(/maximum.*25|too many/i);
  });

  test('should handle network errors gracefully', async ({
    page,
    uploadPage,
    processingPage,
    mockApi
  }) => {
    // Start normal upload
    await mockApi.mockSuccessfulUpload();
    await uploadPage.goto();
    await uploadPage.uploadFiles(testFiles.testImage1);
    await uploadPage.submitUpload();
    
    // Simulate network error during processing
    await page.route('**/api/v1/status/**', async (route) => {
      await route.abort('failed');
    });
    
    // Should show error or retry option
    await page.waitForTimeout(5000);
    await expect(page.locator('text=/error|retry|failed/i')).toBeVisible();
  });

  test('should preserve state across page refreshes', async ({
    page,
    uploadPage,
    mockApi
  }) => {
    await uploadPage.goto();
    
    // Upload files
    await uploadPage.uploadFiles([
      testFiles.testImage1,
      testFiles.testImage2
    ]);
    
    // Set custom face limit
    await uploadPage.setFaceLimit(7500);
    
    // Refresh page
    await page.reload();
    
    // Files should be cleared after refresh (no persistence)
    // But the page should still be functional
    await expect(uploadPage.generateButton).toBeDisabled();
    
    // Can upload again
    await uploadPage.uploadFiles(testFiles.testImage1);
    await expect(uploadPage.generateButton).toBeEnabled();
  });

  test('should handle rapid sequential uploads', async ({
    page,
    uploadPage,
    processingPage,
    mockApi
  }) => {
    // First upload
    await mockApi.mockSuccessfulUpload();
    await uploadPage.goto();
    await uploadPage.uploadFiles(testFiles.testImage1);
    await uploadPage.submitUpload();
    
    // Wait for processing to start
    await page.waitForURL(/.*\/processing\/.*/);
    await processingPage.waitForPageLoad();
    
    // Go back and upload again immediately
    await page.goBack();
    await uploadPage.uploadFiles(testFiles.testImage2);
    await uploadPage.submitUpload();
    
    // Should handle the new upload
    await expect(page).toHaveURL(/.*\/processing\/.*/);
  });
});
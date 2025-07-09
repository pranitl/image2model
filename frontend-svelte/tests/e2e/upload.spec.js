import { test, expect } from './fixtures/test-fixtures.js';
import { createTestFiles } from './utils/create-test-files.js';

// Create test files before running tests
const testFiles = createTestFiles();

test.describe('Upload Page', () => {
  test.beforeEach(async ({ uploadPage, mockApi }) => {
    // Set up default mocks
    await mockApi.mockSuccessfulUpload();
    
    // Navigate to upload page
    await uploadPage.goto();
  });

  test('should display upload interface correctly', async ({ page, uploadPage }) => {
    // Check main elements
    await expect(page).toHaveTitle(/Upload.*Image2Model/i);
    await expect(page.locator('h1')).toContainText('Upload Your Images');
    await expect(uploadPage.uploadArea).toBeVisible();
    await expect(uploadPage.generateButton).toBeDisabled();
    
    // Check help text
    await expect(page.getByText('Tips for Best Results')).toBeVisible();
  });

  test('should handle single file upload', async ({ uploadPage, page }) => {
    // Upload a single file
    await uploadPage.uploadFiles(testFiles.testImage1);
    
    // Verify file preview appears
    await expect(uploadPage.filePreviewSection).toBeVisible();
    await expect(await uploadPage.getFileCount()).toBe(1);
    
    // Verify generate button is enabled
    await expect(uploadPage.generateButton).toBeEnabled();
    
    // Submit upload
    await uploadPage.submitUpload();
    
    // Should navigate to processing page
    await expect(page).toHaveURL(/.*\/processing\/.*/);
  });

  test('should handle multiple file upload', async ({ uploadPage, page }) => {
    // Upload multiple files
    await uploadPage.uploadFiles([
      testFiles.testImage1,
      testFiles.testImage2,
      testFiles.testImage3
    ]);
    
    // Verify all files appear
    await expect(await uploadPage.getFileCount()).toBe(3);
    
    // Remove one file
    await uploadPage.removeFile(1);
    await expect(await uploadPage.getFileCount()).toBe(2);
    
    // Submit should still work
    await expect(uploadPage.generateButton).toBeEnabled();
  });

  test('should validate file types', async ({ uploadPage, page }) => {
    // Try to upload invalid file
    await uploadPage.uploadFiles(testFiles.invalidFile);
    
    // Should show error toast
    await expect(page.locator('.toast.error')).toContainText(/invalid.*file.*type/i);
    
    // File should not be added
    await expect(uploadPage.filePreviewSection).not.toBeVisible();
    await expect(uploadPage.generateButton).toBeDisabled();
  });

  test('should handle large file validation', async ({ uploadPage, page }) => {
    // Try to upload large file
    await uploadPage.uploadFiles(testFiles.largeImage);
    
    // Should show error about file size
    await expect(page.locator('.toast.error')).toContainText(/file.*too.*large|exceeds.*limit/i);
    
    // File should not be added
    await expect(uploadPage.filePreviewSection).not.toBeVisible();
  });

  test('should handle advanced settings', async ({ uploadPage, page }) => {
    // Upload a file first
    await uploadPage.uploadFiles(testFiles.testImage1);
    
    // Open advanced settings
    await uploadPage.advancedSettingsToggle.click();
    
    // Check face limit control is visible
    await expect(uploadPage.faceLimitSlider).toBeVisible();
    await expect(uploadPage.faceLimitValue).toContainText('10,000');
    
    // Change face limit
    await uploadPage.setFaceLimit(5000);
    await expect(uploadPage.faceLimitValue).toContainText('5,000');
    
    // Enable auto mode
    await uploadPage.enableAutoMode();
    await expect(uploadPage.faceLimitSlider).toBeDisabled();
  });

  test('should handle drag and drop', async ({ uploadPage, page }) => {
    // Simulate drag over
    await uploadPage.uploadArea.hover();
    await page.mouse.down();
    await uploadPage.uploadArea.hover();
    
    // Check drag state
    await expect(uploadPage.uploadArea).toHaveClass(/drag-over/);
    
    await page.mouse.up();
  });

  test('should handle upload errors gracefully', async ({ uploadPage, page, mockApi }) => {
    // Set up error mock
    await mockApi.clearMocks();
    await mockApi.mockUploadError();
    
    // Upload file
    await uploadPage.uploadFiles(testFiles.testImage1);
    
    // Try to submit
    await uploadPage.submitUpload();
    
    // Should show error message
    await expect(page.locator('.toast.error')).toContainText(/upload.*failed|invalid.*file/i);
    
    // Should remain on upload page
    await expect(page).toHaveURL(/.*\/upload/);
  });

  test('should show upload limits', async ({ page }) => {
    // Check file info text
    await expect(page.getByText(/Max 10MB per file/)).toBeVisible();
    await expect(page.getByText(/Up to 25 images/)).toBeVisible();
  });

  test('should prevent upload without files', async ({ uploadPage }) => {
    // Generate button should be disabled initially
    await expect(uploadPage.generateButton).toBeDisabled();
    
    // Clicking should not do anything
    await uploadPage.generateButton.click({ force: true });
    
    // Should still be on upload page
    await expect(uploadPage.page).toHaveURL(/.*\/upload/);
  });
});
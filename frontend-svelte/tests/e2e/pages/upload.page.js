export class UploadPage {
  constructor(page) {
    this.page = page;
    
    // Selectors
    this.uploadArea = page.locator('.upload-area');
    this.fileInput = page.locator('input[type="file"]');
    this.generateButton = page.getByText('Generate 3D Models');
    this.advancedSettingsToggle = page.getByText('Advanced Settings');
    this.faceLimitSlider = page.locator('input[type="range"]');
    this.faceLimitValue = page.locator('.value-display');
    this.autoModeCheckbox = page.getByLabel('Auto');
    this.filePreviewSection = page.locator('.file-preview-section');
    this.removeFileButtons = page.locator('.remove-file');
  }

  async goto() {
    await this.page.goto('/upload');
    await this.page.waitForLoadState('networkidle');
  }

  async uploadFiles(filePaths) {
    // Convert single file to array
    const files = Array.isArray(filePaths) ? filePaths : [filePaths];
    
    // Upload files using file input
    await this.fileInput.setInputFiles(files);
    
    // Wait for file preview to appear
    await this.filePreviewSection.waitFor({ state: 'visible' });
  }

  async dragAndDropFiles(filePaths) {
    // Create a data transfer for drag and drop
    const files = Array.isArray(filePaths) ? filePaths : [filePaths];
    
    // Simulate drag and drop
    const dataTransfer = await this.page.evaluateHandle((files) => {
      const dt = new DataTransfer();
      files.forEach(filePath => {
        // Create a file object (this is simplified, real implementation would need actual file data)
        const file = new File([''], filePath.split('/').pop(), { type: 'image/jpeg' });
        dt.items.add(file);
      });
      return dt;
    }, files);

    await this.uploadArea.dispatchEvent('drop', { dataTransfer });
  }

  async setFaceLimit(value) {
    await this.advancedSettingsToggle.click();
    await this.faceLimitSlider.fill(value.toString());
  }

  async enableAutoMode() {
    await this.advancedSettingsToggle.click();
    await this.autoModeCheckbox.check();
  }

  async removeFile(index) {
    const buttons = await this.removeFileButtons.all();
    if (buttons[index]) {
      await buttons[index].click();
    }
  }

  async submitUpload() {
    // Ensure button is enabled
    await expect(this.generateButton).toBeEnabled();
    await this.generateButton.click();
  }

  async getFileCount() {
    const previews = await this.page.locator('.file-preview').count();
    return previews;
  }

  async getErrorMessage() {
    const toast = await this.page.locator('.toast.error').textContent();
    return toast;
  }

  async waitForUploadComplete() {
    // Wait for navigation to processing page
    await this.page.waitForURL('**/processing/**', { timeout: 30000 });
  }
}
export class ProcessingPage {
  constructor(page) {
    this.page = page;
    
    // Selectors
    this.progressBar = page.locator('.progress-bar');
    this.progressFill = page.locator('.progress-fill');
    this.progressText = page.locator('.progress-text');
    this.statusMessage = page.locator('.status-message');
    this.fileProgressItems = page.locator('.file-progress-item');
    this.errorMessage = page.locator('.error-message');
    this.cancelButton = page.getByText('Cancel Processing');
    this.viewResultsButton = page.getByText('View Results');
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await this.progressBar.waitFor({ state: 'visible' });
  }

  async getProgress() {
    const progressText = await this.progressText.textContent();
    const match = progressText?.match(/(\d+)%/);
    return match ? parseInt(match[1]) : 0;
  }

  async getStatusMessage() {
    return await this.statusMessage.textContent();
  }

  async getFileStatuses() {
    const items = await this.fileProgressItems.all();
    const statuses = [];
    
    for (const item of items) {
      const filename = await item.locator('.filename').textContent();
      const status = await item.locator('.status').textContent();
      statuses.push({ filename, status });
    }
    
    return statuses;
  }

  async waitForCompletion(timeout = 120000) {
    try {
      // Wait for either success or error
      await Promise.race([
        this.viewResultsButton.waitFor({ state: 'visible', timeout }),
        this.errorMessage.waitFor({ state: 'visible', timeout })
      ]);
      
      // Check if we have an error
      const hasError = await this.errorMessage.isVisible();
      if (hasError) {
        const error = await this.errorMessage.textContent();
        throw new Error(`Processing failed: ${error}`);
      }
      
      return true;
    } catch (error) {
      console.error('Processing did not complete:', error);
      return false;
    }
  }

  async cancelProcessing() {
    if (await this.cancelButton.isVisible()) {
      await this.cancelButton.click();
      // Wait for confirmation or redirect
      await this.page.waitForLoadState('networkidle');
    }
  }

  async goToResults() {
    await this.viewResultsButton.click();
    await this.page.waitForURL('**/results/**');
  }

  async getEstimatedTime() {
    const timeElement = await this.page.locator('.estimated-time');
    if (await timeElement.isVisible()) {
      return await timeElement.textContent();
    }
    return null;
  }

  async isProcessing() {
    return await this.progressBar.isVisible() && !(await this.viewResultsButton.isVisible());
  }
}
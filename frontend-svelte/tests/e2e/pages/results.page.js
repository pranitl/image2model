export class ResultsPage {
  constructor(page) {
    this.page = page;
    
    // Selectors
    this.resultCards = page.locator('.result-card');
    this.downloadButtons = page.locator('.download-btn');
    this.downloadAllButton = page.getByText('Download All Models');
    this.viewerButtons = page.locator('.view-3d-btn');
    this.thumbnails = page.locator('.model-thumbnail img');
    this.uploadNewButton = page.getByText('Upload New Images');
    this.modelViewer = page.locator('.model-viewer-modal');
    this.modelViewerClose = page.locator('.modal-close');
    this.processingTime = page.locator('.processing-stats .time');
    this.modelCount = page.locator('.processing-stats .count');
  }

  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await this.resultCards.first().waitFor({ state: 'visible' });
  }

  async getResultCount() {
    return await this.resultCards.count();
  }

  async getModelInfo(index) {
    const card = this.resultCards.nth(index);
    const filename = await card.locator('.filename').textContent();
    const fileSize = await card.locator('.file-size').textContent();
    const hasPreview = await card.locator('.model-thumbnail img').isVisible();
    
    return {
      filename,
      fileSize,
      hasPreview
    };
  }

  async downloadModel(index) {
    // Set up download promise before clicking
    const downloadPromise = this.page.waitForEvent('download');
    
    await this.downloadButtons.nth(index).click();
    
    // Wait for download to start
    const download = await downloadPromise;
    
    // Optionally save to specific path
    // await download.saveAs('/path/to/save/file');
    
    return download;
  }

  async downloadAllModels() {
    const downloadPromise = this.page.waitForEvent('download');
    await this.downloadAllButton.click();
    const download = await downloadPromise;
    return download;
  }

  async viewModel(index) {
    await this.viewerButtons.nth(index).click();
    await this.modelViewer.waitFor({ state: 'visible' });
  }

  async closeModelViewer() {
    await this.modelViewerClose.click();
    await this.modelViewer.waitFor({ state: 'hidden' });
  }

  async getProcessingStats() {
    const time = await this.processingTime.textContent();
    const count = await this.modelCount.textContent();
    
    return {
      processingTime: time,
      modelCount: parseInt(count.match(/\d+/)?.[0] || '0')
    };
  }

  async startNewUpload() {
    await this.uploadNewButton.click();
    await this.page.waitForURL('**/upload');
  }

  async verifyAllThumbnails() {
    const thumbnails = await this.thumbnails.all();
    const results = [];
    
    for (const thumbnail of thumbnails) {
      const src = await thumbnail.getAttribute('src');
      const isLoaded = await thumbnail.evaluate(img => img.complete && img.naturalHeight !== 0);
      results.push({ src, isLoaded });
    }
    
    return results;
  }

  async getDownloadUrls() {
    const buttons = await this.downloadButtons.all();
    const urls = [];
    
    for (const button of buttons) {
      const url = await button.getAttribute('href');
      if (url) urls.push(url);
    }
    
    return urls;
  }
}
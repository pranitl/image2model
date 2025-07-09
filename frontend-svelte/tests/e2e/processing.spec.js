import { test, expect } from './fixtures/test-fixtures.js';

test.describe('Processing Page', () => {
  // Helper to navigate to processing page with a job
  async function navigateToProcessing(page, mockApi, jobId = 'test-job-123', taskId = 'test-task-123') {
    // Mock the upload response
    await mockApi.mockSuccessfulUpload();
    
    // Navigate directly to processing page with IDs
    await page.goto(`/processing/${jobId}/${taskId}`);
    await page.waitForLoadState('networkidle');
  }

  test.beforeEach(async ({ page, mockApi }) => {
    // Set up progress mocking
    await mockApi.mockProcessingProgress();
  });

  test('should display processing interface', async ({ page, processingPage, mockApi }) => {
    await navigateToProcessing(page, mockApi);
    
    // Check main elements
    await expect(page.locator('h1')).toContainText('Processing Your Images');
    await expect(processingPage.progressBar).toBeVisible();
    await expect(processingPage.statusMessage).toBeVisible();
  });

  test('should show real-time progress updates', async ({ page, processingPage, mockApi }) => {
    await navigateToProcessing(page, mockApi);
    
    // Initial progress should be low
    const initialProgress = await processingPage.getProgress();
    expect(initialProgress).toBeLessThanOrEqual(20);
    
    // Wait for progress to increase
    await page.waitForTimeout(500);
    const midProgress = await processingPage.getProgress();
    expect(midProgress).toBeGreaterThan(initialProgress);
    
    // Wait for completion
    const completed = await processingPage.waitForCompletion(10000);
    expect(completed).toBe(true);
    
    // Should show view results button
    await expect(processingPage.viewResultsButton).toBeVisible();
  });

  test('should handle processing completion', async ({ page, processingPage, mockApi }) => {
    await navigateToProcessing(page, mockApi);
    
    // Wait for processing to complete
    await processingPage.waitForCompletion(10000);
    
    // Check completion state
    await expect(processingPage.viewResultsButton).toBeVisible();
    await expect(processingPage.statusMessage).toContainText(/complete|finished|done/i);
    
    // Navigate to results
    await processingPage.goToResults();
    await expect(page).toHaveURL(/.*\/results\/.*/);
  });

  test('should show file progress for batch processing', async ({ page, processingPage, mockApi }) => {
    // Mock batch processing with multiple files
    await page.route('**/api/v1/status/tasks/**/stream', async (route) => {
      const encoder = new TextEncoder();
      const events = [
        { type: 'file_update', filename: 'image1.jpg', status: 'processing', progress: 30 },
        { type: 'file_update', filename: 'image2.jpg', status: 'queued', progress: 0 },
        { type: 'file_update', filename: 'image3.jpg', status: 'queued', progress: 0 },
        { type: 'task_progress', progress: 30, status: 'processing' },
        { type: 'file_update', filename: 'image1.jpg', status: 'completed', progress: 100 },
        { type: 'file_update', filename: 'image2.jpg', status: 'processing', progress: 50 },
        { type: 'task_progress', progress: 60, status: 'processing' },
        { type: 'file_update', filename: 'image2.jpg', status: 'completed', progress: 100 },
        { type: 'file_update', filename: 'image3.jpg', status: 'processing', progress: 80 },
        { type: 'task_progress', progress: 90, status: 'processing' },
        { type: 'file_update', filename: 'image3.jpg', status: 'completed', progress: 100 },
        { type: 'task_completed', progress: 100, status: 'completed' }
      ];
      
      const stream = new ReadableStream({
        async start(controller) {
          for (const event of events) {
            const message = `event: ${event.type}\ndata: ${JSON.stringify(event)}\n\n`;
            controller.enqueue(encoder.encode(message));
            await new Promise(resolve => setTimeout(resolve, 200));
          }
          controller.close();
        }
      });
      
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: stream
      });
    });
    
    await navigateToProcessing(page, mockApi);
    
    // Wait for file progress items to appear
    await processingPage.fileProgressItems.first().waitFor({ state: 'visible' });
    
    // Check file statuses
    const fileStatuses = await processingPage.getFileStatuses();
    expect(fileStatuses.length).toBeGreaterThan(0);
    
    // Wait for all files to complete
    await processingPage.waitForCompletion(10000);
    
    // All files should be completed
    const finalStatuses = await processingPage.getFileStatuses();
    for (const status of finalStatuses) {
      expect(status.status).toContain('completed');
    }
  });

  test('should handle processing errors', async ({ page, processingPage, mockApi }) => {
    // Mock error response
    await page.route('**/api/v1/status/tasks/**/stream', async (route) => {
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        async start(controller) {
          const errorEvent = `event: task_failed\ndata: ${JSON.stringify({
            status: 'failed',
            error: 'Processing failed: Insufficient memory',
            timestamp: new Date().toISOString()
          })}\n\n`;
          
          controller.enqueue(encoder.encode(errorEvent));
          controller.close();
        }
      });
      
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: stream
      });
    });
    
    await navigateToProcessing(page, mockApi);
    
    // Wait for error to appear
    await processingPage.errorMessage.waitFor({ state: 'visible', timeout: 10000 });
    
    // Check error message
    await expect(processingPage.errorMessage).toContainText(/failed|error/i);
    
    // Should not show view results button
    await expect(processingPage.viewResultsButton).not.toBeVisible();
  });

  test('should handle cancel operation', async ({ page, processingPage, mockApi }) => {
    // Mock a slow processing stream
    let streamCancelled = false;
    
    await page.route('**/api/v1/status/tasks/**/stream', async (route) => {
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        async start(controller) {
          for (let i = 0; i <= 100 && !streamCancelled; i += 5) {
            const event = `data: ${JSON.stringify({
              status: 'processing',
              progress: i,
              timestamp: new Date().toISOString()
            })}\n\n`;
            
            controller.enqueue(encoder.encode(event));
            await new Promise(resolve => setTimeout(resolve, 500));
          }
          controller.close();
        }
      });
      
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: stream
      });
    });
    
    // Mock cancel endpoint
    await page.route('**/api/v1/tasks/**/cancel', async (route) => {
      streamCancelled = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Task cancelled' })
      });
    });
    
    await navigateToProcessing(page, mockApi);
    
    // Wait for processing to start
    await page.waitForTimeout(1000);
    
    // Cancel should be visible during processing
    await expect(processingPage.cancelButton).toBeVisible();
    
    // Click cancel
    await processingPage.cancelProcessing();
    
    // Should redirect or show cancelled state
    await expect(page.locator('text=/cancel/i')).toBeVisible();
  });

  test('should show estimated time remaining', async ({ page, processingPage, mockApi }) => {
    // Mock progress with time estimates
    await page.route('**/api/v1/status/tasks/**/stream', async (route) => {
      const encoder = new TextEncoder();
      const events = [
        { status: 'processing', progress: 10, estimated_time_remaining: '2 minutes' },
        { status: 'processing', progress: 50, estimated_time_remaining: '1 minute' },
        { status: 'processing', progress: 90, estimated_time_remaining: '10 seconds' },
        { status: 'completed', progress: 100 }
      ];
      
      const stream = new ReadableStream({
        async start(controller) {
          for (const event of events) {
            const message = `data: ${JSON.stringify(event)}\n\n`;
            controller.enqueue(encoder.encode(message));
            await new Promise(resolve => setTimeout(resolve, 300));
          }
          controller.close();
        }
      });
      
      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: stream
      });
    });
    
    await navigateToProcessing(page, mockApi);
    
    // Check for time estimate
    const estimatedTime = await processingPage.getEstimatedTime();
    expect(estimatedTime).toBeTruthy();
  });

  test('should handle connection loss gracefully', async ({ page, processingPage, mockApi }) => {
    // Mock a connection that drops
    await page.route('**/api/v1/status/tasks/**/stream', async (route) => {
      // Immediately close connection
      await route.abort('failed');
    });
    
    // Mock fallback polling endpoint
    let pollCount = 0;
    await page.route('**/api/v1/status/tasks/**', async (route) => {
      if (!route.request().url().includes('stream')) {
        pollCount++;
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            status: pollCount < 3 ? 'processing' : 'completed',
            progress: Math.min(pollCount * 30, 100),
            timestamp: new Date().toISOString()
          })
        });
      }
    });
    
    await navigateToProcessing(page, mockApi);
    
    // Should fall back to polling and still complete
    const completed = await processingPage.waitForCompletion(15000);
    expect(completed).toBe(true);
  });
});
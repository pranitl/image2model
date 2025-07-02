import { test, expect } from '@playwright/test';
import { promises as fs } from 'fs';
import path from 'path';

test.describe('Upload and Processing Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to upload page
    await page.goto('/upload');
  });

  test('should successfully upload single file and navigate to processing', async ({ page }) => {
    // Create a test image file
    const testImagePath = path.join(__dirname, '..', 'fixtures', 'test-image.jpg');
    
    // Mock the API responses to test our frontend logic
    await page.route('**/api/v1/upload/batch', async (route) => {
      // Simulate successful batch upload response (even for single file)
      const mockResponse = {
        batch_id: 'test-batch-123',
        job_id: 'test-task-456', // This is the key field for SSE
        uploaded_files: [{
          file_id: 'test-file-789',
          filename: 'test-image.jpg',
          file_size: 12345,
          content_type: 'image/jpeg',
          status: 'uploaded'
        }],
        face_limit: null,
        total_files: 1,
        status: 'uploaded',
        message: 'Files uploaded successfully, processing started'
      };
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockResponse)
      });
    });

    // Mock SSE endpoint to test connection
    await page.route('**/api/v1/status/tasks/test-task-456/stream**', async (route) => {
      // Mock SSE stream response
      const sseData = [
        'event: task_queued\ndata: {"status": "queued", "progress": 0, "message": "Task is queued and waiting to start", "task_id": "test-task-456"}\n\n',
        'event: task_progress\ndata: {"status": "processing", "progress": 50, "message": "Processing image...", "task_id": "test-task-456"}\n\n',
        'event: task_completed\ndata: {"status": "completed", "progress": 100, "message": "Task completed successfully", "task_id": "test-task-456"}\n\n'
      ].join('');
      
      await route.fulfill({
        status: 200,
        headers: {
          'content-type': 'text/event-stream',
          'cache-control': 'no-cache',
          'connection': 'keep-alive'
        },
        body: sseData
      });
    });

    // Upload a file
    const fileInput = page.getByRole('button', { name: /choose files|browse/i }).or(page.locator('input[type="file"]'));
    
    // Create a simple test file if it doesn't exist
    try {
      await fs.access(testImagePath);
    } catch {
      // Create a minimal test image file
      const testImageContent = Buffer.from('fake-jpeg-content');
      await fs.writeFile(testImagePath, testImageContent);
    }
    
    await fileInput.setInputFiles(testImagePath);
    
    // Click upload button
    const uploadButton = page.getByRole('button', { name: /upload/i });
    await uploadButton.click();

    // Should navigate to processing page with correct task ID
    await expect(page).toHaveURL('/processing/test-task-456');
    
    // Processing page should display task information
    await expect(page.getByText('Task ID: test-task-456')).toBeVisible();
    
    // Should show initial queued status
    await expect(page.getByText(/queued|processing/i)).toBeVisible();
    
    // Should show progress information
    await expect(page.locator('[role="progressbar"]').or(page.getByText('Progress'))).toBeVisible();
  });

  test('should handle task ID extraction correctly', async ({ page }) => {
    // Test the frontend task ID extraction logic with different response formats
    
    // Mock batch upload response
    await page.route('**/api/v1/upload/batch', async (route) => {
      const mockResponse = {
        batch_id: 'batch-abc-123',
        job_id: 'uuid-task-id-456', // Should extract this as taskId
        uploaded_files: [{
          file_id: 'file-def-789',
          filename: 'test.jpg',
          file_size: 5000,
          content_type: 'image/jpeg',
          status: 'uploaded'
        }],
        total_files: 1,
        status: 'uploaded'
      };
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockResponse)
      });
    });

    // Add console listener to check for JavaScript errors
    const jsErrors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        jsErrors.push(msg.text());
      }
    });

    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./tests/fixtures/test-image.jpg');
    
    const uploadButton = page.getByRole('button', { name: /upload/i });
    await uploadButton.click();

    // Should extract job_id correctly and navigate
    await expect(page).toHaveURL('/processing/uuid-task-id-456');
    
    // Should not have JavaScript errors related to undefined task ID
    const taskIdErrors = jsErrors.filter(error => 
      error.includes('undefined') && error.includes('task')
    );
    expect(taskIdErrors).toHaveLength(0);
  });

  test('should show error when upload response missing job_id', async ({ page }) => {
    // Mock malformed response to test error handling
    await page.route('**/api/v1/upload/batch', async (route) => {
      const mockResponse = {
        // Missing job_id field to test error handling
        batch_id: 'batch-123',
        uploaded_files: [],
        total_files: 0,
        status: 'uploaded'
      };
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockResponse)
      });
    });

    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./tests/fixtures/test-image.jpg');
    
    const uploadButton = page.getByRole('button', { name: /upload/i });
    await uploadButton.click();

    // Should show error message instead of navigating
    await expect(page.getByText(/upload.*failed|error/i)).toBeVisible();
    
    // Should not navigate to processing page
    await expect(page).not.toHaveURL(/\/processing\/.*/);
  });

  test('should handle SSE connection with correct endpoint', async ({ page }) => {
    const testTaskId = 'sse-test-task-123';
    
    // Mock upload response
    await page.route('**/api/v1/upload/batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          batch_id: 'batch-123',
          job_id: testTaskId,
          uploaded_files: [{ file_id: 'file-123', filename: 'test.jpg', status: 'uploaded' }],
          total_files: 1,
          status: 'uploaded'
        })
      });
    });

    // Track SSE connection attempts
    const sseRequests: string[] = [];
    await page.route('**/api/v1/status/tasks/**', async (route) => {
      sseRequests.push(route.request().url());
      
      await route.fulfill({
        status: 200,
        headers: { 'content-type': 'text/event-stream' },
        body: 'event: task_queued\ndata: {"status": "queued", "task_id": "' + testTaskId + '"}\n\n'
      });
    });

    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./tests/fixtures/test-image.jpg');
    
    const uploadButton = page.getByRole('button', { name: /upload/i });
    await uploadButton.click();

    // Wait for navigation and SSE connection
    await page.waitForURL(`/processing/${testTaskId}`);
    await page.waitForTimeout(1000); // Give time for SSE connection

    // Verify SSE endpoint was called with correct path
    const correctEndpoint = sseRequests.find(url => 
      url.includes(`/api/v1/status/tasks/${testTaskId}/stream`)
    );
    expect(correctEndpoint).toBeTruthy();
    
    // Should not call old incorrect endpoint
    const incorrectEndpoint = sseRequests.find(url => 
      url.includes('/api/status/') && !url.includes('/v1/')
    );
    expect(incorrectEndpoint).toBeFalsy();
  });

  test('should retry SSE connection on failure', async ({ page }) => {
    const testTaskId = 'retry-test-task-456';
    
    // Mock upload response
    await page.route('**/api/v1/upload/batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          batch_id: 'batch-456',
          job_id: testTaskId,
          uploaded_files: [{ file_id: 'file-456', filename: 'test.jpg', status: 'uploaded' }],
          total_files: 1,
          status: 'uploaded'
        })
      });
    });

    // Mock SSE endpoint to fail first few times, then succeed
    let connectionAttempts = 0;
    await page.route(`**/api/v1/status/tasks/${testTaskId}/stream**`, async (route) => {
      connectionAttempts++;
      
      if (connectionAttempts <= 2) {
        // Fail first 2 attempts
        await route.fulfill({
          status: 500,
          body: 'Internal Server Error'
        });
      } else {
        // Succeed on 3rd attempt
        await route.fulfill({
          status: 200,
          headers: { 'content-type': 'text/event-stream' },
          body: 'event: task_queued\ndata: {"status": "queued", "task_id": "' + testTaskId + '"}\n\n'
        });
      }
    });

    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('./tests/fixtures/test-image.jpg');
    
    const uploadButton = page.getByRole('button', { name: /upload/i });
    await uploadButton.click();

    // Wait for navigation
    await page.waitForURL(`/processing/${testTaskId}`);
    
    // Should show retry attempts
    await expect(page.getByText(/reconnection|retry/i)).toBeVisible();
    
    // Should eventually connect successfully
    await expect(page.getByText(/queued|connected/i)).toBeVisible({ timeout: 10000 });
    
    // Should have made multiple connection attempts
    expect(connectionAttempts).toBeGreaterThan(1);
  });

  test('should handle multiple file upload consistently', async ({ page }) => {
    // Test that multiple files still use batch endpoint and get correct task ID
    
    await page.route('**/api/v1/upload/batch', async (route) => {
      const mockResponse = {
        batch_id: 'multi-batch-789',
        job_id: 'multi-task-101112', // Task ID for multiple files
        uploaded_files: [
          { file_id: 'file-1', filename: 'image1.jpg', status: 'uploaded' },
          { file_id: 'file-2', filename: 'image2.jpg', status: 'uploaded' },
          { file_id: 'file-3', filename: 'image3.jpg', status: 'uploaded' }
        ],
        total_files: 3,
        status: 'uploaded'
      };
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockResponse)
      });
    });

    // Upload multiple files
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles([
      './tests/fixtures/test-image.jpg',
      './tests/fixtures/test-image.jpg', // Use same file multiple times for testing
      './tests/fixtures/test-image.jpg'
    ]);
    
    const uploadButton = page.getByRole('button', { name: /upload/i });
    await uploadButton.click();

    // Should navigate with batch job_id as task ID
    await expect(page).toHaveURL('/processing/multi-task-101112');
    
    // Should display batch information
    await expect(page.getByText(/3.*files|batch/i)).toBeVisible();
  });
});

test.describe('Processing Page SSE Integration', () => {
  test('should display task information correctly', async ({ page }) => {
    const testTaskId = 'display-test-123';
    
    // Mock SSE endpoint
    await page.route(`**/api/v1/status/tasks/${testTaskId}/stream**`, async (route) => {
      const sseData = 'event: task_progress\ndata: {"status": "processing", "progress": 75, "message": "Generating 3D model...", "task_id": "' + testTaskId + '", "timestamp": ' + Date.now() + '}\n\n';
      
      await route.fulfill({
        status: 200,
        headers: { 'content-type': 'text/event-stream' },
        body: sseData
      });
    });

    // Navigate directly to processing page
    await page.goto(`/processing/${testTaskId}`);

    // Should display task ID (not undefined)
    await expect(page.getByText(`Task ID: ${testTaskId}`)).toBeVisible();
    
    // Should display status and progress
    await expect(page.getByText('processing')).toBeVisible();
    await expect(page.getByText('75%')).toBeVisible();
    await expect(page.getByText('Generating 3D model...')).toBeVisible();
    
    // Should show timestamp
    await expect(page.getByText(/started|timestamp/i)).toBeVisible();
  });

  test('should show connection status', async ({ page }) => {
    const testTaskId = 'connection-test-456';
    
    // Mock initially failing SSE endpoint
    let shouldFail = true;
    await page.route(`**/api/v1/status/tasks/${testTaskId}/stream**`, async (route) => {
      if (shouldFail) {
        shouldFail = false;
        await route.fulfill({ status: 500 });
      } else {
        await route.fulfill({
          status: 200,
          headers: { 'content-type': 'text/event-stream' },
          body: 'event: task_queued\ndata: {"status": "queued", "task_id": "' + testTaskId + '"}\n\n'
        });
      }
    });

    await page.goto(`/processing/${testTaskId}`);

    // Should show initial connection attempt
    await expect(page.getByText(/connecting|disconnected/i)).toBeVisible();
    
    // Should show retry attempt
    await expect(page.getByText(/reconnection|retry/i)).toBeVisible();
    
    // Should eventually connect
    await expect(page.getByText(/connected|queued/i)).toBeVisible({ timeout: 10000 });
  });
});
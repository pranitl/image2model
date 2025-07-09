import { test as base } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
import { UploadPage } from '../pages/upload.page.js';
import { ProcessingPage } from '../pages/processing.page.js';
import { ResultsPage } from '../pages/results.page.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Extend basic test by providing page objects
export const test = base.extend({
  // Page objects
  uploadPage: async ({ page }, use) => {
    await use(new UploadPage(page));
  },
  
  processingPage: async ({ page }, use) => {
    await use(new ProcessingPage(page));
  },
  
  resultsPage: async ({ page }, use) => {
    await use(new ResultsPage(page));
  },

  // Test data fixtures
  testImages: async ({}, use) => {
    // Create sample image paths (you'll need to add actual test images)
    const images = {
      single: path.join(__dirname, 'images', 'test-image-1.jpg'),
      multiple: [
        path.join(__dirname, 'images', 'test-image-1.jpg'),
        path.join(__dirname, 'images', 'test-image-2.jpg'),
        path.join(__dirname, 'images', 'test-image-3.jpg'),
      ],
      invalid: path.join(__dirname, 'images', 'invalid-file.txt'),
      large: path.join(__dirname, 'images', 'large-image.jpg'), // > 10MB
    };
    
    await use(images);
  },

  // API mocking setup
  mockApi: async ({ page }, use) => {
    const mocks = {
      // Mock successful upload
      mockSuccessfulUpload: async () => {
        await page.route('**/api/v1/upload/', async (route) => {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              job_id: 'mock-job-123',
              task_id: 'mock-task-123',
              batch_id: 'mock-batch-123',
              total_files: 1,
              message: 'Upload successful'
            })
          });
        });
      },

      // Mock processing progress
      mockProcessingProgress: async () => {
        let progressCount = 0;
        
        await page.route('**/api/v1/status/tasks/**/stream', async (route) => {
          const encoder = new TextEncoder();
          const stream = new ReadableStream({
            async start(controller) {
              // Send progress updates
              for (let i = 0; i <= 100; i += 20) {
                const event = `data: ${JSON.stringify({
                  status: i < 100 ? 'processing' : 'completed',
                  progress: i,
                  timestamp: new Date().toISOString(),
                  message: i < 100 ? `Processing... ${i}%` : 'Processing complete!'
                })}\n\n`;
                
                controller.enqueue(encoder.encode(event));
                await new Promise(resolve => setTimeout(resolve, 100));
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
      },

      // Mock job results
      mockJobResults: async (jobId = 'mock-job-123') => {
        await page.route(`**/api/v1/download/${jobId}/all`, async (route) => {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              job_id: jobId,
              files: [
                {
                  filename: 'model-1.glb',
                  size: 1024000,
                  mime_type: 'model/gltf-binary',
                  file_size: 1024000,
                  created_time: new Date().toISOString(),
                  model_url: 'https://example.com/model-1.glb',
                  rendered_image: 'https://example.com/preview-1.jpg'
                },
                {
                  filename: 'model-2.glb',
                  size: 2048000,
                  mime_type: 'model/gltf-binary',
                  file_size: 2048000,
                  created_time: new Date().toISOString(),
                  model_url: 'https://example.com/model-2.glb',
                  rendered_image: 'https://example.com/preview-2.jpg'
                }
              ],
              total_files: 2
            })
          });
        });
      },

      // Mock API errors
      mockUploadError: async () => {
        await page.route('**/api/v1/upload/', async (route) => {
          await route.fulfill({
            status: 400,
            contentType: 'application/json',
            body: JSON.stringify({
              error: true,
              detail: 'Invalid file format'
            })
          });
        });
      },

      // Clear all mocks
      clearMocks: async () => {
        await page.unroute('**/*');
      }
    };
    
    await use(mocks);
  },

  // Authenticated context
  authenticatedContext: async ({ browser }, use) => {
    const context = await browser.newContext({
      // Add auth headers or cookies here
      extraHTTPHeaders: {
        'Authorization': `Bearer ${process.env.API_KEY}`
      }
    });
    
    await use(context);
  }
});

export { expect } from '@playwright/test';
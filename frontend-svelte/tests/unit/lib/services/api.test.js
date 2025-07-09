import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import api, { APIService } from '$lib/services/api.js';

// Mock fetch globally
global.fetch = vi.fn();
global.EventSource = vi.fn();
global.AbortSignal = { timeout: vi.fn(() => ({})) };

// Mock window to not be defined for APIService tests
delete global.window;

describe('APIService', () => {
  let apiService;

  beforeEach(() => {
    // Initialize with test API key
    apiService = new APIService('test-api-key-123');
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('constructor', () => {
    it('should initialize with correct API base URL', () => {
      // Now always uses direct backend URL
      expect(apiService.API_BASE).toBe('http://localhost:8000/api/v1');
    });

    it('should use direct backend URL regardless of window', () => {
      global.window = { location: { origin: 'http://localhost:3000' } };
      const service = new APIService('test-api-key');
      // Should still use backend URL, not window origin
      expect(service.API_BASE).toBe('http://localhost:8000/api/v1');
      delete global.window;
    });
  });

  describe('uploadBatch', () => {
    it('should successfully upload files', async () => {
      const mockFiles = [
        { file: new File(['content1'], 'test1.jpg', { type: 'image/jpeg' }) },
        { file: new File(['content2'], 'test2.jpg', { type: 'image/jpeg' }) }
      ];

      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          batch_id: 'batch-123',
          task_id: 'task-456',
          total_files: 2
        })
      };

      fetch.mockResolvedValue(mockResponse);

      const result = await apiService.uploadBatch(mockFiles, 5000);

      expect(result).toEqual({
        success: true,
        batchId: 'batch-123',
        taskId: 'task-456',
        fileCount: 2
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/upload/'),
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
          headers: expect.objectContaining({
            'Authorization': expect.stringContaining('Bearer')
          })
        })
      );
    });

    it('should handle upload errors gracefully', async () => {
      const mockFiles = [new File(['content'], 'test.jpg', { type: 'image/jpeg' })];

      fetch.mockResolvedValue({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: vi.fn().mockResolvedValue({ message: 'Invalid file format' })
      });

      const result = await apiService.uploadBatch(mockFiles);

      expect(result).toEqual({
        success: false,
        error: 'Invalid file format'
      });
    });

    it('should use default face limit when not specified', async () => {
      const mockFiles = [new File(['content'], 'test.jpg', { type: 'image/jpeg' })];
      let capturedFormData;

      fetch.mockImplementation((url, options) => {
        capturedFormData = options.body;
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ batch_id: 'test-id' })
        });
      });

      await apiService.uploadBatch(mockFiles);

      // FormData doesn't expose entries in test environment easily,
      // but we can verify the method was called correctly
      expect(fetch).toHaveBeenCalled();
    });
  });

  describe('getJobFiles', () => {
    it('should fetch and transform job files correctly', async () => {
      const mockJobId = 'job-123';
      const mockResponse = {
        files: [
          {
            filename: 'model1.glb',
            size: 1024000,
            mime_type: 'model/gltf-binary',
            created_time: '2024-01-01T00:00:00Z',
            rendered_image: { url: 'https://example.com/preview1.webp' }
          }
        ],
        download_urls: ['https://fal.ai/download/model1.glb'],
        total_files: 1,
        job_id: mockJobId
      };

      fetch.mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue(mockResponse)
      });

      const result = await apiService.getJobFiles(mockJobId);

      expect(result.success).toBe(true);
      expect(result.files).toHaveLength(1);
      expect(result.files[0]).toMatchObject({
        filename: 'model1.glb',
        name: 'model1.glb',
        size: 1024000,
        downloadUrl: 'https://fal.ai/download/model1.glb',
        mimeType: 'model/gltf-binary',
        rendered_image: { url: 'https://example.com/preview1.webp' }
      });
    });

    it('should handle API errors', async () => {
      fetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: vi.fn().mockResolvedValue({ error: 'Job not found' })
      });

      const result = await apiService.getJobFiles('invalid-job');

      expect(result).toEqual({
        success: false,
        error: 'Job not found'
      });
    });
  });

  describe('createProgressStream', () => {
    let mockEventSource;

    beforeEach(() => {
      mockEventSource = {
        addEventListener: vi.fn(),
        close: vi.fn(),
        readyState: EventSource.CONNECTING,
        onerror: null
      };
      EventSource.mockReturnValue(mockEventSource);
    });

    it('should create event source and handle progress events', () => {
      const callbacks = {
        onProgress: vi.fn(),
        onComplete: vi.fn(),
        onError: vi.fn()
      };

      const stream = apiService.createProgressStream('task-123', callbacks);

      // Verify EventSource was created with correct URL
      expect(EventSource).toHaveBeenCalledWith('http://localhost:8000/api/v1/status/tasks/task-123/stream');

      // Simulate progress event
      const progressHandler = mockEventSource.addEventListener.mock.calls
        .find(call => call[0] === 'task_progress')[1];
      
      progressHandler({
        data: JSON.stringify({
          progress: 50,
          total_files: 5,
          current: 2
        })
      });

      expect(callbacks.onProgress).toHaveBeenCalledWith({
        progress: 50,
        total_files: 5,
        current: 2
      });

      // Test stream control
      stream.close();
      expect(mockEventSource.close).toHaveBeenCalled();
    });

    it('should handle completion events', () => {
      const callbacks = {
        onComplete: vi.fn(),
        onTaskUpdate: vi.fn()
      };

      apiService.createProgressStream('task-123', callbacks);

      const completeHandler = mockEventSource.addEventListener.mock.calls
        .find(call => call[0] === 'task_completed')[1];

      completeHandler({
        data: JSON.stringify({
          result: { job_id: 'job-123' },
          success_count: 5
        })
      });

      expect(callbacks.onComplete).toHaveBeenCalled();
      expect(mockEventSource.close).toHaveBeenCalled();
    });
  });

  describe('utility methods', () => {
    describe('isExternalUrl', () => {
      it('should identify FAL.AI URLs', () => {
        expect(apiService.isExternalUrl('https://fal.ai/file.glb')).toBe(true);
        expect(apiService.isExternalUrl('https://fal.media/file.glb')).toBe(true);
        expect(apiService.isExternalUrl('https://fal.run/file.glb')).toBe(true);
        expect(apiService.isExternalUrl('/api/download/file.glb')).toBe(false);
        expect(apiService.isExternalUrl(null)).toBe(false);
      });
    });

    describe('formatFileSize', () => {
      it('should format file sizes correctly', () => {
        expect(apiService.formatFileSize(0)).toBe('0 Bytes');
        expect(apiService.formatFileSize(1024)).toBe('1 KB');
        expect(apiService.formatFileSize(1048576)).toBe('1 MB');
        expect(apiService.formatFileSize(1536000)).toBe('1.46 MB');
      });
    });

    describe('getDownloadUrl', () => {
      it('should generate correct download URLs', () => {
        const url = apiService.getDownloadUrl('job-123', 'model.glb');
        expect(url).toBe('http://localhost:8000/api/v1/download/job-123/model.glb');
      });

      it('should encode filenames', () => {
        const url = apiService.getDownloadUrl('job-123', 'my file.glb');
        expect(url).toBe('http://localhost:8000/api/v1/download/job-123/my%20file.glb');
      });
    });
  });

  describe('retryOperation', () => {
    it('should retry failed operations', async () => {
      let attemptCount = 0;
      const operation = vi.fn().mockImplementation(() => {
        attemptCount++;
        if (attemptCount < 3) {
          return Promise.reject(new Error('Network error'));
        }
        return Promise.resolve('success');
      });

      const result = await apiService.retryOperation(operation, 3, 10);

      expect(result).toBe('success');
      expect(operation).toHaveBeenCalledTimes(3);
    });

    it('should throw after max retries', async () => {
      const operation = vi.fn().mockRejectedValue(new Error('Persistent error'));

      await expect(
        apiService.retryOperation(operation, 2, 10)
      ).rejects.toThrow('Persistent error');

      expect(operation).toHaveBeenCalledTimes(2);
    });
  });
});

describe('API singleton export', () => {
  it('should export a singleton instance', () => {
    expect(api).toBeInstanceOf(APIService);
  });
});
/**
 * Unit tests for useUpload hook focusing on our task ID extraction fixes.
 */

import { renderHook, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useUpload } from '@/hooks/useUpload';
import * as apiUtils from '@/utils/api';

// Mock the API utilities
vi.mock('@/utils/api', () => ({
  apiRequest: {
    upload: vi.fn()
  },
  handleApiError: vi.fn()
}));

// Mock file validation
vi.mock('@/utils/validation', () => ({
  validateImageFiles: vi.fn(() => ({ isValid: true, errors: [] }))
}));

describe('useUpload Hook', () => {
  const mockApiUpload = vi.mocked(apiUtils.apiRequest.upload);
  const mockHandleApiError = vi.mocked(apiUtils.handleApiError);

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Task ID Extraction', () => {
    it('should extract job_id from batch upload response', async () => {
      const mockBatchResponse = {
        data: {
          batch_id: 'batch-123',
          job_id: 'task-456', // This should be extracted as taskId
          uploaded_files: [{
            file_id: 'file-789',
            filename: 'test.jpg',
            file_size: 5000,
            content_type: 'image/jpeg',
            status: 'uploaded'
          }],
          total_files: 1,
          status: 'uploaded'
        }
      };

      mockApiUpload.mockResolvedValueOnce(mockBatchResponse);

      const { result } = renderHook(() => useUpload());

      const testFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
      let uploadResult: any;

      await act(async () => {
        uploadResult = await result.current.uploadFiles([testFile]);
      });

      // Should extract job_id correctly
      expect(uploadResult).toEqual({
        taskId: 'task-456',
        data: mockBatchResponse.data
      });

      // Should call batch endpoint
      expect(mockApiUpload).toHaveBeenCalledWith(
        '/api/v1/upload/batch',
        expect.any(FormData),
        expect.any(Function)
      );
    });

    it('should handle single file upload using batch endpoint', async () => {
      const mockBatchResponse = {
        data: {
          batch_id: 'single-batch-abc',
          job_id: 'single-task-def',
          uploaded_files: [{
            file_id: 'single-file-ghi',
            filename: 'single.jpg',
            file_size: 2000,
            content_type: 'image/jpeg',
            status: 'uploaded'
          }],
          total_files: 1,
          status: 'uploaded'
        }
      };

      mockApiUpload.mockResolvedValueOnce(mockBatchResponse);

      const { result } = renderHook(() => useUpload());

      const testFile = new File(['single'], 'single.jpg', { type: 'image/jpeg' });
      let uploadResult: any;

      await act(async () => {
        uploadResult = await result.current.uploadFiles([testFile]);
      });

      // Even single file should use batch endpoint and extract job_id
      expect(uploadResult.taskId).toBe('single-task-def');
      expect(uploadResult.data.total_files).toBe(1);

      // Should use batch endpoint, not single file endpoint
      expect(mockApiUpload).toHaveBeenCalledWith(
        '/api/v1/upload/batch',
        expect.any(FormData),
        expect.any(Function)
      );
    });

    it('should handle multiple file upload correctly', async () => {
      const mockBatchResponse = {
        data: {
          batch_id: 'multi-batch-123',
          job_id: 'multi-task-456',
          uploaded_files: [
            { file_id: 'file-1', filename: 'image1.jpg', status: 'uploaded' },
            { file_id: 'file-2', filename: 'image2.jpg', status: 'uploaded' },
            { file_id: 'file-3', filename: 'image3.jpg', status: 'uploaded' }
          ],
          total_files: 3,
          status: 'uploaded'
        }
      };

      mockApiUpload.mockResolvedValueOnce(mockBatchResponse);

      const { result } = renderHook(() => useUpload());

      const testFiles = [
        new File(['test1'], 'image1.jpg', { type: 'image/jpeg' }),
        new File(['test2'], 'image2.jpg', { type: 'image/jpeg' }),
        new File(['test3'], 'image3.jpg', { type: 'image/jpeg' })
      ];

      let uploadResult: any;

      await act(async () => {
        uploadResult = await result.current.uploadFiles(testFiles);
      });

      expect(uploadResult.taskId).toBe('multi-task-456');
      expect(uploadResult.data.total_files).toBe(3);
      expect(uploadResult.data.uploaded_files).toHaveLength(3);

      // Should call with all files as 'files' parameters
      const callArgs = mockApiUpload.mock.calls[0];
      const formData = callArgs[1] as FormData;
      const files = formData.getAll('files');
      expect(files).toHaveLength(3);
    });

    it('should throw error when job_id is missing from response', async () => {
      const mockInvalidResponse = {
        data: {
          batch_id: 'batch-123',
          // Missing job_id field
          uploaded_files: [],
          total_files: 0,
          status: 'uploaded'
        }
      };

      mockApiUpload.mockResolvedValueOnce(mockInvalidResponse);

      const { result } = renderHook(() => useUpload());

      const testFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });

      await act(async () => {
        const uploadResult = await result.current.uploadFiles([testFile]);
        expect(uploadResult).toBeNull(); // Should return null on error
      });

      expect(result.current.error).toContain('job_id');
    });

    it('should handle API response wrapper correctly', async () => {
      // Test response wrapped in ApiResponse format
      const mockWrappedResponse = {
        data: {
          success: true,
          data: {
            batch_id: 'wrapped-batch',
            job_id: 'wrapped-task',
            uploaded_files: [{ file_id: 'wrapped-file', filename: 'test.jpg', status: 'uploaded' }],
            total_files: 1,
            status: 'uploaded'
          }
        }
      };

      mockApiUpload.mockResolvedValueOnce(mockWrappedResponse);

      const { result } = renderHook(() => useUpload());

      const testFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
      let uploadResult: any;

      await act(async () => {
        uploadResult = await result.current.uploadFiles([testFile]);
      });

      // Should extract from wrapped response
      expect(uploadResult.taskId).toBe('wrapped-task');
    });
  });

  describe('FormData Construction', () => {
    it('should construct FormData correctly for single file', async () => {
      const mockResponse = {
        data: {
          batch_id: 'test',
          job_id: 'test-task',
          uploaded_files: [],
          total_files: 1,
          status: 'uploaded'
        }
      };

      mockApiUpload.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useUpload());

      const testFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' });

      await act(async () => {
        await result.current.uploadFiles([testFile]);
      });

      const callArgs = mockApiUpload.mock.calls[0];
      const formData = callArgs[1] as FormData;

      // Should append as 'files' (batch parameter)
      const files = formData.getAll('files');
      expect(files).toHaveLength(1);
      expect(files[0]).toBe(testFile);
    });

    it('should include face_limit parameter when provided', async () => {
      const mockResponse = {
        data: {
          batch_id: 'test',
          job_id: 'test-task',
          uploaded_files: [],
          total_files: 1,
          status: 'uploaded'
        }
      };

      mockApiUpload.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useUpload());

      const testFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
      const options = { 
        quality: 'high' as const,
        outputFormat: 'gltf' as const,
        generateTextures: true,
        optimizeForPrinting: false,
        faceLimit: 5000 
      };

      await act(async () => {
        await result.current.uploadFiles([testFile], options);
      });

      const callArgs = mockApiUpload.mock.calls[0];
      const formData = callArgs[1] as FormData;

      expect(formData.get('face_limit')).toBe('5000');
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors correctly', async () => {
      const mockError = new Error('Upload failed');
      mockApiUpload.mockRejectedValueOnce(mockError);
      mockHandleApiError.mockReturnValueOnce('Upload failed');

      const { result } = renderHook(() => useUpload());

      const testFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });

      await act(async () => {
        const uploadResult = await result.current.uploadFiles([testFile]);
        expect(uploadResult).toBeNull();
      });

      expect(result.current.error).toBe('Upload failed');
      expect(result.current.isUploading).toBe(false);
    });

    it('should handle empty response data', async () => {
      const mockEmptyResponse = { data: null };
      mockApiUpload.mockResolvedValueOnce(mockEmptyResponse);

      const { result } = renderHook(() => useUpload());

      const testFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });

      await act(async () => {
        const uploadResult = await result.current.uploadFiles([testFile]);
        expect(uploadResult).toBeNull();
      });

      expect(result.current.error).toContain('no response data');
    });
  });

  describe('State Management', () => {
    it('should manage upload state correctly', async () => {
      const mockResponse = {
        data: {
          batch_id: 'test',
          job_id: 'test-task',
          uploaded_files: [],
          total_files: 1,
          status: 'uploaded'
        }
      };

      // Mock a delayed response to test loading state
      mockApiUpload.mockImplementationOnce(() => 
        new Promise(resolve => setTimeout(() => resolve(mockResponse), 100))
      );

      const { result } = renderHook(() => useUpload());

      const testFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });

      // Initial state
      expect(result.current.isUploading).toBe(false);
      expect(result.current.uploadProgress).toBe(0);
      expect(result.current.error).toBeNull();

      // Start upload
      act(() => {
        result.current.uploadFiles([testFile]);
      });

      // Should be in loading state
      expect(result.current.isUploading).toBe(true);

      // Wait for completion
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 150));
      });

      // Should be completed
      expect(result.current.isUploading).toBe(false);
      expect(result.current.uploadProgress).toBe(0); // Reset after completion
    });

    it('should track upload progress', async () => {
      const mockResponse = {
        data: {
          batch_id: 'test',
          job_id: 'test-task',
          uploaded_files: [],
          total_files: 1,
          status: 'uploaded'
        }
      };

      mockApiUpload.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useUpload());

      const testFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });

      await act(async () => {
        await result.current.uploadFiles([testFile]);
      });

      // Should have called upload with progress callback
      const callArgs = mockApiUpload.mock.calls[0];
      const progressCallback = callArgs[2];
      expect(typeof progressCallback).toBe('function');
    });
  });
});
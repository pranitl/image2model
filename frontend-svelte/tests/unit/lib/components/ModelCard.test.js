import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, cleanup, fireEvent } from '@testing-library/svelte';
import ModelCard from '$lib/components/ModelCard.svelte';

describe('ModelCard Component', () => {
  const mockFile = {
    filename: 'test-model.glb',
    name: 'test-model.glb',
    size: 1048576, // 1 MB
    downloadUrl: '/api/v1/download/job-123/test-model.glb',
    mimeType: 'model/gltf-binary',
    rendered_image: {
      url: 'https://example.com/preview.webp'
    }
  };

  const mockFileExternal = {
    ...mockFile,
    downloadUrl: 'https://fal.ai/models/test-model.glb'
  };

  beforeEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render model information correctly', () => {
      const { getByText } = render(ModelCard, {
        props: {
          file: mockFile,
          jobId: 'job-123'
        }
      });

      expect(getByText('test-model.glb')).toBeTruthy();
      expect(getByText('1 MB')).toBeTruthy();
      expect(getByText('GLB')).toBeTruthy(); // File format badge
    });

    it('should display preview image when available', () => {
      const { container } = render(ModelCard, {
        props: {
          file: mockFile,
          jobId: 'job-123'
        }
      });

      const img = container.querySelector('img');
      expect(img).toBeTruthy();
      expect(img.src).toBe('https://example.com/preview.webp');
      expect(img.alt).toBe('Preview of test-model.glb');
      expect(img.getAttribute('loading')).toBe('lazy');
    });

    it('should show placeholder when no preview image', () => {
      const fileWithoutPreview = { ...mockFile, rendered_image: null };
      
      const { container, getByText } = render(ModelCard, {
        props: {
          file: fileWithoutPreview,
          jobId: 'job-123'
        }
      });

      expect(container.querySelector('img')).toBeFalsy();
      expect(container.querySelector('.model-preview-placeholder')).toBeTruthy();
      expect(getByText('3D Model')).toBeTruthy();
    });
  });

  describe('File Format Detection', () => {
    const formatTests = [
      { filename: 'model.glb', expected: 'GLB' },
      { filename: 'model.GLB', expected: 'GLB' },
      { filename: 'model.obj', expected: 'OBJ' },
      { filename: 'model.stl', expected: 'STL' },
      { filename: 'model.unknown', expected: '3D' }
    ];

    formatTests.forEach(({ filename, expected }) => {
      it(`should display ${expected} for ${filename}`, () => {
        const { getByText } = render(ModelCard, {
          props: {
            file: { ...mockFile, filename },
            jobId: 'job-123'
          }
        });

        expect(getByText(expected)).toBeTruthy();
      });
    });
  });

  describe('Download Functionality', () => {
    it('should render download button for local files', () => {
      const { getByText, container } = render(ModelCard, {
        props: {
          file: mockFile,
          jobId: 'job-123'
        }
      });

      const downloadBtn = getByText('Download').closest('a');
      expect(downloadBtn).toBeTruthy();
      expect(downloadBtn.href).toContain('/api/v1/download/job-123/test-model.glb');
      expect(downloadBtn.download).toBe('test-model.glb');
      expect(downloadBtn.target).not.toBe('_blank');
    });

    it('should open external files in new tab', () => {
      const { getByText } = render(ModelCard, {
        props: {
          file: mockFileExternal,
          jobId: 'job-123'
        }
      });

      const downloadBtn = getByText('Download').closest('a');
      expect(downloadBtn).toBeTruthy();
      expect(downloadBtn.href).toBe('https://fal.ai/models/test-model.glb');
      expect(downloadBtn.target).toBe('_blank');
      expect(downloadBtn.rel).toBe('noopener noreferrer');
    });

    it('should handle download click event', async () => {
      const onDownload = vi.fn();
      const { getByText } = render(ModelCard, {
        props: {
          file: mockFile,
          jobId: 'job-123',
          onDownload
        }
      });

      const downloadBtn = getByText('Download');
      await fireEvent.click(downloadBtn);

      expect(onDownload).toHaveBeenCalledWith(mockFile);
    });
  });

  describe('Preview Functionality', () => {
    it('should render preview button', () => {
      const { getByText } = render(ModelCard, {
        props: {
          file: mockFile,
          jobId: 'job-123'
        }
      });

      const previewBtn = getByText('Preview');
      expect(previewBtn).toBeTruthy();
    });

    it('should handle preview click event', async () => {
      const onPreview = vi.fn();
      const { getByText } = render(ModelCard, {
        props: {
          file: mockFile,
          jobId: 'job-123',
          onPreview
        }
      });

      const previewBtn = getByText('Preview');
      await fireEvent.click(previewBtn);

      expect(onPreview).toHaveBeenCalledWith(mockFile);
    });
  });

  describe('Responsive Behavior', () => {
    it('should apply hover effects class', () => {
      const { container } = render(ModelCard, {
        props: {
          file: mockFile,
          jobId: 'job-123'
        }
      });

      const card = container.querySelector('.model-card');
      expect(card.classList.contains('hover-lift')).toBe(true);
    });

    it('should truncate long filenames', () => {
      const longFilename = 'this-is-a-very-long-filename-that-should-be-truncated.glb';
      const { container } = render(ModelCard, {
        props: {
          file: { ...mockFile, filename: longFilename },
          jobId: 'job-123'
        }
      });

      const filenameElement = container.querySelector('.model-name');
      expect(filenameElement.title).toBe(longFilename);
      // Text overflow is handled by CSS, not inline styles
      const computedStyle = window.getComputedStyle(filenameElement);
      expect(computedStyle.textOverflow || 'ellipsis').toBe('ellipsis');
    });
  });

  describe('Error Handling', () => {
    it('should handle missing file data gracefully', () => {
      const incompleteFile = {
        filename: 'test.glb',
        size: 0
      };

      const { getByText } = render(ModelCard, {
        props: {
          file: incompleteFile,
          jobId: 'job-123'
        }
      });

      expect(getByText('test.glb')).toBeTruthy();
      expect(getByText('0 Bytes')).toBeTruthy();
    });

    it('should handle image loading errors', async () => {
      const { container } = render(ModelCard, {
        props: {
          file: mockFile,
          jobId: 'job-123'
        }
      });

      const img = container.querySelector('img');
      
      // Simulate image error
      await fireEvent.error(img);

      // Should fall back to placeholder
      expect(container.querySelector('.model-preview-placeholder')).toBeTruthy();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      const { container } = render(ModelCard, {
        props: {
          file: mockFile,
          jobId: 'job-123'
        }
      });

      const downloadBtn = container.querySelector('a[download]');
      expect(downloadBtn.getAttribute('aria-label')).toBe('Download test-model.glb');

      const previewBtn = container.querySelector('button');
      expect(previewBtn.getAttribute('aria-label')).toBe('Preview test-model.glb');
    });

    it('should have keyboard navigation support', async () => {
      const onDownload = vi.fn();
      const onPreview = vi.fn();

      const { container } = render(ModelCard, {
        props: {
          file: mockFile,
          jobId: 'job-123',
          onDownload,
          onPreview
        }
      });

      const downloadBtn = container.querySelector('a[download]');
      const previewBtn = container.querySelector('button');

      // Test keyboard interaction
      downloadBtn.focus();
      expect(document.activeElement).toBe(downloadBtn);

      previewBtn.focus();
      expect(document.activeElement).toBe(previewBtn);
    });
  });
});
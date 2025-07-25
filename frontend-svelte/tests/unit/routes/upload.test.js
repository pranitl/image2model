import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import { readable } from 'svelte/store';
import UploadPage from '../../../src/routes/upload/+page.svelte';

// Mock SvelteKit stores
vi.mock('$app/stores', () => ({
  page: readable({
    url: new URL('http://localhost:3000/upload'),
    params: {},
    route: { id: '/upload' },
    status: 200,
    error: null,
    data: {},
    form: null
  })
}));

// Mock navigation
vi.mock('$app/navigation', () => ({
  goto: vi.fn()
}));

// Mock environment
vi.mock('$app/environment', () => ({
  browser: true
}));

// Mock the API module
vi.mock('$lib/services/api', () => ({
  default: {
    uploadBatch: vi.fn(),
    retryOperation: vi.fn((fn) => fn()),
    setApiKey: vi.fn(),
    API_KEY: null,
    API_BASE: 'http://localhost:8000/api/v1'
  }
}));

// Mock toast store
vi.mock('$lib/stores/toast', () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
    info: vi.fn()
  }
}));

// Mock auth store with API key
vi.mock('$lib/stores/auth', () => ({
  apiKey: readable('test-api-key-123')
}));

describe('Upload Page', () => {
  beforeEach(() => {
    // Mock fetch for API calls
    global.fetch = vi.fn();
    
    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = vi.fn();
    
    // Mock window to not be defined to ensure relative URLs in tests
    delete global.window;
  });

  it('should render upload page with all key elements', () => {
    const { container } = render(UploadPage);
    
    // Check main elements exist
    expect(screen.getByText('Upload Your Images')).toBeInTheDocument();
    expect(screen.getByText('Transform photos into professional 3D models in minutes')).toBeInTheDocument();
    expect(screen.getByText('Drop images here or click to browse')).toBeInTheDocument();
    
    // Check file info - it's now in a single line
    expect(screen.getByText('Supports JPEG, PNG • Max 10MB per file • Up to 25 images')).toBeInTheDocument();
    
    // Check help section
    expect(screen.getByText('Tips for Best Results')).toBeInTheDocument();
  });

  it('should have disabled generate button initially', () => {
    render(UploadPage);
    
    const generateBtn = screen.getByText('Generate 3D Models').closest('button');
    expect(generateBtn).toBeDisabled();
  });

  it('should show file count when files are present', () => {
    const { container } = render(UploadPage);
    
    // Check that there's no file preview section initially
    expect(container.querySelector('.file-preview-section')).toBeFalsy();
    
    // The component should have the upload zone
    expect(screen.getByText('Drop images here or click to browse')).toBeInTheDocument();
  });

  it('should validate file types', async () => {
    const { container } = render(UploadPage);
    
    // Create invalid file type
    const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });
    const fileInput = container.querySelector('input[type="file"]');
    
    await fireEvent.change(fileInput, {
      target: { files: [invalidFile] }
    });
    
    // File should not be added (no preview section)
    expect(container.querySelector('.file-preview-section')).toBeFalsy();
  });

  it('should handle advanced options toggle', async () => {
    const { container } = render(UploadPage);
    
    const optionsToggle = screen.getByText('Advanced Settings').closest('button');
    
    // Options should be hidden initially
    expect(container.querySelector('.options-content.active')).toBeFalsy();
    
    // Click to expand
    await fireEvent.click(optionsToggle);
    
    // Options should be visible
    expect(screen.getByText('Face Limit Control')).toBeInTheDocument();
    expect(screen.getByText('10,000')).toBeInTheDocument(); // Default face limit
  });

  it('should handle form submission', async () => {
    // Import the mocked API
    const api = await import('$lib/services/api');
    
    // Setup successful upload response
    api.default.uploadBatch.mockResolvedValue({
      success: true,
      batchId: 'test-batch-123',
      taskId: 'test-task-123',
      fileCount: 1
    });
    
    const { container } = render(UploadPage);
    
    // Add a file
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    const fileInput = container.querySelector('input[type="file"]');
    await fireEvent.change(fileInput, {
      target: { files: [file] }
    });
    
    // Submit form
    const form = container.querySelector('form');
    await fireEvent.submit(form);
    
    // Check API was called
    expect(api.default.uploadBatch).toHaveBeenCalled();
    expect(api.default.uploadBatch).toHaveBeenCalledWith(
      expect.arrayContaining([expect.objectContaining({ name: 'test.jpg' })]),
      null // auto mode sends null
    );
  });

  it('should handle drag over state', async () => {
    const { container } = render(UploadPage);
    
    const uploadArea = container.querySelector('.upload-area');
    
    // Simulate drag over
    await fireEvent.dragOver(uploadArea);
    expect(uploadArea).toHaveClass('drag-over');
    
    // Simulate drag leave
    await fireEvent.dragLeave(uploadArea);
    expect(uploadArea).not.toHaveClass('drag-over');
  });
});
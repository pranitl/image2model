import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/svelte';
import { tick } from 'svelte';

// Mock modules with inline functions
vi.mock('$app/navigation', () => ({
  goto: vi.fn()
}));

vi.mock('$lib/stores/toast.js', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}));

vi.mock('$app/stores', () => ({
  page: {
    subscribe: vi.fn((callback) => {
      // Default behavior - return taskId
      callback({
        url: {
          searchParams: {
            get: vi.fn((param) => {
              if (param === 'taskId') return 'test-task-123';
              return null;
            })
          }
        }
      });
      return () => {};
    })
  }
}));

// Import component and mocked modules after vi.mock
import ProcessingPage from '../../../src/routes/processing/+page.svelte';
import { goto } from '$app/navigation';
import { page } from '$app/stores';
import { toast } from '$lib/stores/toast.js';

describe('Processing Page', () => {
  beforeEach(() => {
    // Clear all mocks
    vi.clearAllMocks();
    
    // Reset page store to default with taskId
    page.subscribe.mockClear();
    page.subscribe.mockImplementation((callback) => {
      callback({
        url: {
          searchParams: {
            get: vi.fn((param) => {
              if (param === 'taskId') return 'test-task-123';
              return null;
            })
          }
        }
      });
      return () => {};
    });
  });

  // Test 1: Basic rendering
  it('should render core page elements', async () => {
    render(ProcessingPage);
    await tick();
    
    // Check for main heading
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
    
    // Check for progress indicator step 2
    expect(screen.getByText('2')).toBeInTheDocument();
    
    // Check for section headings
    expect(screen.getByText('Overall Progress')).toBeInTheDocument();
    expect(screen.getByText('Processing Status')).toBeInTheDocument();
  });

  // Test 2: Task ID display
  it('should display task ID', async () => {
    render(ProcessingPage);
    await tick();
    
    expect(screen.getByText(/test-task-123/)).toBeInTheDocument();
  });

  // Test 3: Missing task ID handling
  it('should redirect when task ID is missing', async () => {
    // Mock page store without task ID
    page.subscribe.mockImplementation((callback) => {
      callback({
        url: {
          searchParams: {
            get: vi.fn(() => null)
          }
        }
      });
      return () => {};
    });
    
    render(ProcessingPage);
    await tick();
    
    expect(toast.error).toHaveBeenCalledWith('No task ID provided');
    expect(goto).toHaveBeenCalledWith('/upload');
  });

  // Test 4: Tips carousel
  it('should display tips section', async () => {
    render(ProcessingPage);
    await tick();
    
    expect(screen.getByText(/Did You Know/i)).toBeInTheDocument();
  });

  // Test 5: Hero component usage
  it('should use Hero component with correct props', async () => {
    render(ProcessingPage);
    await tick();
    
    expect(screen.getByText('Processing Your Images')).toBeInTheDocument();
    expect(screen.getByText('Your 3D models are being generated')).toBeInTheDocument();
  });

  // Test 6: Progress bar display
  it('should display progress bar', async () => {
    render(ProcessingPage);
    await tick();
    
    // Check for initial progress display
    expect(screen.getByText('0%')).toBeInTheDocument();
    expect(screen.getByText('0 of 0 files completed')).toBeInTheDocument();
  });

  // Test 7: Cancel button presence
  it('should have a cancel button', async () => {
    render(ProcessingPage);
    await tick();
    
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    expect(cancelButton).toBeInTheDocument();
    expect(cancelButton).toHaveTextContent('Cancel Processing');
  });

  // Test 8: Breadcrumb navigation
  it('should show breadcrumb navigation', async () => {
    render(ProcessingPage);
    await tick();
    
    // Check breadcrumb items - use getAllByText since Upload appears multiple times
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getAllByText('Upload')).toHaveLength(2); // In breadcrumb and progress indicator
    expect(screen.getByText('Processing')).toBeInTheDocument();
    expect(screen.getByText('Results')).toBeInTheDocument();
  });

  // Test 9: Batch parameter support in URL parsing
  it('should support batch query parameter', async () => {
    // Mock page store with batch parameter
    page.subscribe.mockImplementation((callback) => {
      callback({
        url: {
          searchParams: {
            get: vi.fn((param) => {
              if (param === 'taskId') return null;
              if (param === 'batch') return 'batch-456';
              return null;
            })
          }
        }
      });
      return () => {};
    });
    
    render(ProcessingPage);
    await tick();
    
    expect(screen.getByText(/batch-456/)).toBeInTheDocument();
  });
  
  // Test 10: View toggle buttons
  it('should have view toggle buttons', async () => {
    render(ProcessingPage);
    await tick();
    
    // Check for grid/list view toggle buttons
    const viewButtons = screen.getAllByRole('button').filter(btn => 
      btn.getAttribute('title')?.includes('view')
    );
    expect(viewButtons).toHaveLength(2);
  });

  // Test 11: Processing section structure
  it('should have all main sections', async () => {
    render(ProcessingPage);
    await tick();
    
    // Check for main sections
    expect(screen.getByText('Task ID')).toBeInTheDocument();
    expect(screen.getByText('Files')).toBeInTheDocument();
    expect(screen.getByText('Started')).toBeInTheDocument();
    expect(screen.getByText('Elapsed')).toBeInTheDocument();
  });
});
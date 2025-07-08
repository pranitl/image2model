import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { writable } from 'svelte/store';
import ErrorPage from './+error.svelte';

// Mock the $app/stores module
vi.mock('$app/stores', () => ({
  page: writable({
    status: 404,
    error: { message: 'Not found' }
  })
}));

describe('Error Page', () => {
  it('should render 404 error correctly', () => {
    render(ErrorPage);
    
    expect(screen.getByText('Page Not Found')).toBeInTheDocument();
    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText("The page you're looking for doesn't exist.")).toBeInTheDocument();
  });
  
  it('should render action buttons', () => {
    render(ErrorPage);
    
    expect(screen.getByText('Go to Homepage')).toBeInTheDocument();
    expect(screen.getByText('Go Back')).toBeInTheDocument();
  });
});
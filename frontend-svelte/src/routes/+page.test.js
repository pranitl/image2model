import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Page from './+page.svelte';

describe('Landing Page', () => {
  it('should render the hero section', () => {
    render(Page);
    
    const heading = screen.getByRole('heading', { 
      name: /Transform Images Into 3D Models/i 
    });
    expect(heading).toBeInTheDocument();
  });
  
  it('should render the navigation menu', () => {
    render(Page);
    
    expect(screen.getByText('Features')).toBeInTheDocument();
    expect(screen.getByText('How It Works')).toBeInTheDocument();
    expect(screen.getByText('Examples')).toBeInTheDocument();
    expect(screen.getByText('Pricing')).toBeInTheDocument();
  });
  
  it('should render all main sections', () => {
    render(Page);
    
    // Check for section headings
    expect(screen.getByText('Why Choose image2model?')).toBeInTheDocument();
    expect(screen.getByText('Simple Three-Step Process')).toBeInTheDocument();
    expect(screen.getByText('See the Magic in Action')).toBeInTheDocument();
    expect(screen.getByText('Ready to Transform Your First Image?')).toBeInTheDocument();
  });
  
  it('should have call-to-action buttons', () => {
    render(Page);
    
    const ctaButtons = screen.getAllByText('Start Creating');
    expect(ctaButtons.length).toBeGreaterThan(0);
  });
});
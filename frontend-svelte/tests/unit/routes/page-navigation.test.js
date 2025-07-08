import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Page from '../../../src/routes/+page.svelte';

// Mock scrollIntoView since it's not available in jsdom
Element.prototype.scrollIntoView = vi.fn();

describe('Landing Page Navigation', () => {
  it('should have working anchor links to all sections', async () => {
    render(Page);
    
    // Get navigation links
    const navbar = screen.getByRole('navigation');
    const featuresLink = navbar.querySelector('a[href="#features"]');
    const howItWorksLink = navbar.querySelector('a[href="#how-it-works"]');
    const examplesLink = navbar.querySelector('a[href="#examples"]');
    
    expect(featuresLink).toBeTruthy();
    expect(howItWorksLink).toBeTruthy();
    expect(examplesLink).toBeTruthy();
  });
  
  it('should have proper section IDs for navigation', () => {
    const { container } = render(Page);
    
    // Check that sections have proper IDs
    const featuresSection = container.querySelector('#features');
    const howItWorksSection = container.querySelector('#how-it-works');
    const examplesSection = container.querySelector('#examples');
    
    expect(featuresSection).toBeTruthy();
    expect(howItWorksSection).toBeTruthy();
    expect(examplesSection).toBeTruthy();
    
    // Verify the content is in the right sections
    expect(featuresSection.textContent).toContain('Why Choose image2model?');
    expect(howItWorksSection.textContent).toContain('Simple Three-Step Process');
    expect(examplesSection.textContent).toContain('See the Magic in Action');
  });
  
  it('should render all feature cards', () => {
    render(Page);
    
    // Check all feature cards are present
    expect(screen.getByText('AI-Powered Precision')).toBeInTheDocument();
    expect(screen.getByText('Lightning Fast')).toBeInTheDocument();
    expect(screen.getByText('Batch Processing')).toBeInTheDocument();
    expect(screen.getByText('Secure & Private')).toBeInTheDocument();
  });
  
  it('should render all process steps', () => {
    render(Page);
    
    // Check all steps are present
    expect(screen.getByText('Upload Your Images')).toBeInTheDocument();
    expect(screen.getByText('AI Processing Magic')).toBeInTheDocument();
    expect(screen.getByText('Download & Create')).toBeInTheDocument();
  });
  
  it('should render all example cards', () => {
    render(Page);
    
    // Check all example types are present
    expect(screen.getByText('Artifacts / Museum Objects')).toBeInTheDocument();
    expect(screen.getByText('Product Photography')).toBeInTheDocument();
    expect(screen.getByText('Furniture')).toBeInTheDocument();
  });
});
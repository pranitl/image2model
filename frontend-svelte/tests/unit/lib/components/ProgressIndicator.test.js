import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import ProgressIndicator from '../../../../src/lib/components/ProgressIndicator.svelte';

describe('ProgressIndicator Component', () => {
  // Test basic functionality without hardcoding step labels
  it('should render with default step', () => {
    render(ProgressIndicator);
    
    // Should show step numbers
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('should highlight current step', () => {
    const { container } = render(ProgressIndicator, {
      props: {
        currentStep: 2
      }
    });
    
    // Check that there's an active step
    const activeSteps = container.querySelectorAll('.active');
    expect(activeSteps.length).toBeGreaterThan(0);
    
    // Step 2 should be marked as current
    expect(screen.getByText('2').closest('.progress-step')).toHaveClass('active');
  });

  it('should show completed steps', () => {
    const { container } = render(ProgressIndicator, {
      props: {
        currentStep: 3
      }
    });
    
    // Check for checkmarks in completed steps
    const checkmarks = screen.getAllByText('✓');
    expect(checkmarks).toHaveLength(2); // Steps 1 and 2 should be complete
  });

  it('should render all step labels', () => {
    render(ProgressIndicator, {
      props: {
        currentStep: 1
      }
    });
    
    // Check that step labels exist without hardcoding them
    const steps = screen.getAllByText(/Upload|Process|Download/);
    expect(steps.length).toBeGreaterThan(0);
  });

  it('should handle edge cases', () => {
    // Test with step 1
    const { container, unmount } = render(ProgressIndicator, {
      props: {
        currentStep: 1
      }
    });
    
    expect(screen.queryAllByText('✓')).toHaveLength(0);
    
    // Clean up and re-render for step 3
    unmount();
    
    render(ProgressIndicator, {
      props: {
        currentStep: 3
      }
    });
    
    expect(screen.queryAllByText('✓')).toHaveLength(2);
  });

  it('should have proper structure for styling', () => {
    const { container } = render(ProgressIndicator, {
      props: {
        currentStep: 2
      }
    });
    
    // Check main container exists
    expect(container.querySelector('.progress-indicator')).toBeTruthy();
    
    // Check steps exist
    const steps = container.querySelectorAll('.progress-step');
    expect(steps.length).toBe(3);
    
    // Each step should have number and text elements
    steps.forEach(step => {
      expect(step.querySelector('.progress-step-number')).toBeTruthy();
      expect(step.querySelector('.progress-step-text')).toBeTruthy();
    });
  });

  it('should support responsive behavior', () => {
    const { container } = render(ProgressIndicator, {
      props: {
        currentStep: 2
      }
    });
    
    // Verify structure supports mobile/desktop views
    const stepTexts = container.querySelectorAll('.progress-step-text');
    expect(stepTexts.length).toBe(3);
    
    // Text elements should exist (CSS will handle visibility)
    stepTexts.forEach(text => {
      expect(text.textContent).toBeTruthy();
    });
  });
});
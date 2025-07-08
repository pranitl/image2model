import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, cleanup } from '@testing-library/svelte';
import Icon from '$lib/components/Icon.svelte';

describe('Icon Component', () => {
  beforeEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('should render a known icon', () => {
      const { container } = render(Icon, {
        props: {
          name: 'check',
          size: 24,
          color: 'currentColor'
        }
      });

      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
      expect(svg.getAttribute('width')).toBe('24');
      expect(svg.getAttribute('height')).toBe('24');
      expect(svg.getAttribute('fill')).toBe('currentColor');
    });

    it('should render with custom size', () => {
      const { container } = render(Icon, {
        props: {
          name: 'download',
          size: 48
        }
      });

      const svg = container.querySelector('svg');
      expect(svg.getAttribute('width')).toBe('48');
      expect(svg.getAttribute('height')).toBe('48');
    });

    it('should render with custom color', () => {
      const { container } = render(Icon, {
        props: {
          name: 'error',
          color: '#ff0000'
        }
      });

      const svg = container.querySelector('svg');
      expect(svg.getAttribute('fill')).toBe('#ff0000');
    });

    it('should apply custom CSS classes', () => {
      const { container } = render(Icon, {
        props: {
          name: 'folder',
          class: 'custom-icon-class'
        }
      });

      const svg = container.querySelector('svg');
      expect(svg.classList.contains('custom-icon-class')).toBe(true);
    });
  });

  describe('Icon Library', () => {
    const iconNames = [
      'check', 'check-circle', 'folder', 'document', 
      'download', 'upload', 'clock', 'eye', 'x', 
      'info', 'warning', 'error', 'cube'
    ];

    iconNames.forEach(iconName => {
      it(`should render ${iconName} icon`, () => {
        const { container } = render(Icon, {
          props: { name: iconName }
        });

        const path = container.querySelector('svg path');
        expect(path).toBeTruthy();
        expect(path.getAttribute('d')).toBeTruthy();
      });
    });
  });

  describe('Fallback Behavior', () => {
    it('should show placeholder for unknown icon', () => {
      // Spy on console.warn
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});

      const { container } = render(Icon, {
        props: { name: 'non-existent-icon' }
      });

      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
      
      // Should show placeholder circle and question mark
      const circle = container.querySelector('circle');
      const text = container.querySelector('text');
      expect(circle).toBeTruthy();
      expect(text).toBeTruthy();
      expect(text.textContent).toBe('?');

      // Should warn about missing icon
      expect(warnSpy).toHaveBeenCalledWith('Icon "non-existent-icon" not found in Icon component');

      warnSpy.mockRestore();
    });

    it('should render empty state when no name provided', () => {
      const { container } = render(Icon, {
        props: {}
      });

      const svg = container.querySelector('svg');
      expect(svg).toBeTruthy();
      
      // Should show placeholder
      const circle = container.querySelector('circle');
      expect(circle).toBeTruthy();
    });
  });

  describe('Custom SVG via Slot', () => {
    it('should render custom SVG content via slot', () => {
      const { container } = render(Icon, {
        props: {
          size: 32,
          color: 'blue'
        },
        slots: {
          default: '<rect x="4" y="4" width="12" height="12" />'
        }
      });

      const svg = container.querySelector('svg');
      const rect = container.querySelector('rect');
      
      expect(svg).toBeTruthy();
      expect(svg.getAttribute('width')).toBe('32');
      expect(svg.getAttribute('fill')).toBe('blue');
      expect(rect).toBeTruthy();
      expect(rect.getAttribute('x')).toBe('4');
    });
  });

  describe('Props Spreading', () => {
    it('should spread additional props to SVG element', () => {
      const { container } = render(Icon, {
        props: {
          name: 'check',
          'data-testid': 'test-icon',
          'aria-label': 'Success icon',
          role: 'img'
        }
      });

      const svg = container.querySelector('svg');
      expect(svg.getAttribute('data-testid')).toBe('test-icon');
      expect(svg.getAttribute('aria-label')).toBe('Success icon');
      expect(svg.getAttribute('role')).toBe('img');
    });
  });

  describe('Accessibility', () => {
    it('should have proper viewBox for all icons', () => {
      const { container } = render(Icon, {
        props: { name: 'download' }
      });

      const svg = container.querySelector('svg');
      expect(svg.getAttribute('viewBox')).toBe('0 0 20 20');
    });

    it('should support aria attributes', () => {
      const { container } = render(Icon, {
        props: {
          name: 'warning',
          'aria-hidden': 'true'
        }
      });

      const svg = container.querySelector('svg');
      expect(svg.getAttribute('aria-hidden')).toBe('true');
    });
  });

  describe('Performance Considerations', () => {
    it('should not re-render when props do not change', () => {
      const { container, component } = render(Icon, {
        props: { name: 'check' }
      });

      const initialSvg = container.querySelector('svg').outerHTML;
      
      // Trigger a reactive update with same props
      component.$set({ name: 'check' });
      
      const updatedSvg = container.querySelector('svg').outerHTML;
      expect(updatedSvg).toBe(initialSvg);
    });

    it('should update when icon name changes', () => {
      const { container, component } = render(Icon, {
        props: { name: 'check' }
      });

      const checkPath = container.querySelector('path').getAttribute('d');
      
      component.$set({ name: 'x' });
      
      const xPath = container.querySelector('path').getAttribute('d');
      expect(xPath).not.toBe(checkPath);
    });
  });
});
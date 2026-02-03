/**
 * FACTLY - Accessibility Utilities
 * Helper functions for improving accessibility across the application
 */

/**
 * Focus management utilities
 */
export const focusUtils = {
  /**
   * Trap focus within a modal or dialog element
   * @param {HTMLElement} element - The container element to trap focus within
   * @returns {Function} Cleanup function to remove event listeners
   */
  trapFocus(element) {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    const handleKeyDown = (e) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          e.preventDefault();
          lastFocusable.focus();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          e.preventDefault();
          firstFocusable.focus();
        }
      }
    };

    element.addEventListener('keydown', handleKeyDown);
    firstFocusable?.focus();

    return () => {
      element.removeEventListener('keydown', handleKeyDown);
    };
  },

  /**
   * Save and restore focus
   * @returns {Object} Object with save and restore methods
   */
  createFocusManager() {
    let savedFocus = null;

    return {
      save: () => {
        savedFocus = document.activeElement;
      },
      restore: () => {
        if (savedFocus && savedFocus.focus) {
          savedFocus.focus();
        }
      },
    };
  },

  /**
   * Focus first invalid field in a form
   * @param {HTMLFormElement} form - The form element
   */
  focusFirstInvalid(form) {
    const invalidField = form.querySelector(':invalid');
    if (invalidField) {
      invalidField.focus();
      invalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  },
};

/**
 * Announce messages to screen readers
 */
export const announce = {
  /**
   * Create an ARIA live region for announcements
   */
  createLiveRegion(priority = 'polite') {
    const region = document.createElement('div');
    region.setAttribute('aria-live', priority);
    region.setAttribute('aria-atomic', 'true');
    region.className = 'sr-only';
    document.body.appendChild(region);
    return region;
  },

  /**
   * Announce a message to screen readers
   * @param {string} message - The message to announce
   * @param {string} priority - 'polite' or 'assertive'
   */
  message(message, priority = 'polite') {
    const region = this.createLiveRegion(priority);
    
    // Clear previous content and set new message
    setTimeout(() => {
      region.textContent = message;
    }, 100);

    // Remove after announcement
    setTimeout(() => {
      region.remove();
    }, 1000);
  },
};

/**
 * Keyboard navigation utilities
 */
export const keyboard = {
  /**
   * Check if event is an activation key (Enter or Space)
   * @param {KeyboardEvent} event
   * @returns {boolean}
   */
  isActivationKey(event) {
    return event.key === 'Enter' || event.key === ' ';
  },

  /**
   * Check if event is an escape key
   * @param {KeyboardEvent} event
   * @returns {boolean}
   */
  isEscapeKey(event) {
    return event.key === 'Escape';
  },

  /**
   * Handle keyboard activation for non-button elements
   * @param {KeyboardEvent} event
   * @param {Function} callback
   */
  handleActivation(event, callback) {
    if (this.isActivationKey(event)) {
      event.preventDefault();
      callback();
    }
  },
};

/**
 * Color contrast utilities
 */
export const contrast = {
  /**
   * Calculate relative luminance of a color
   * @param {number} r - Red (0-255)
   * @param {number} g - Green (0-255)
   * @param {number} b - Blue (0-255)
   * @returns {number}
   */
  getLuminance(r, g, b) {
    const [rs, gs, bs] = [r, g, b].map((val) => {
      val = val / 255;
      return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  },

  /**
   * Calculate contrast ratio between two colors
   * @param {string} color1 - Hex color
   * @param {string} color2 - Hex color
   * @returns {number}
   */
  getContrastRatio(color1, color2) {
    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      } : null;
    };

    const rgb1 = hexToRgb(color1);
    const rgb2 = hexToRgb(color2);

    if (!rgb1 || !rgb2) return 0;

    const lum1 = this.getLuminance(rgb1.r, rgb1.g, rgb1.b);
    const lum2 = this.getLuminance(rgb2.r, rgb2.g, rgb2.b);

    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);

    return (brightest + 0.05) / (darkest + 0.05);
  },

  /**
   * Check if color combination meets WCAG AA standard
   * @param {string} foreground - Hex color
   * @param {string} background - Hex color
   * @param {boolean} isLargeText - Whether text is large (18pt+ or 14pt+ bold)
   * @returns {boolean}
   */
  meetsWCAGAA(foreground, background, isLargeText = false) {
    const ratio = this.getContrastRatio(foreground, background);
    return isLargeText ? ratio >= 3 : ratio >= 4.5;
  },

  /**
   * Check if color combination meets WCAG AAA standard
   * @param {string} foreground - Hex color
   * @param {string} background - Hex color
   * @param {boolean} isLargeText - Whether text is large
   * @returns {boolean}
   */
  meetsWCAGAAA(foreground, background, isLargeText = false) {
    const ratio = this.getContrastRatio(foreground, background);
    return isLargeText ? ratio >= 4.5 : ratio >= 7;
  },
};

/**
 * Skip link utility
 */
export const skipLink = {
  /**
   * Create and inject a skip link
   * @param {string} targetId - ID of the element to skip to
   * @param {string} label - Label for the skip link
   */
  create(targetId, label = 'Skip to main content') {
    const existingLink = document.querySelector('.skip-link');
    if (existingLink) return;

    const link = document.createElement('a');
    link.href = `#${targetId}`;
    link.className = 'skip-link';
    link.textContent = label;
    
    document.body.insertBefore(link, document.body.firstChild);

    // Handle click to ensure focus
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.getElementById(targetId);
      if (target) {
        target.tabIndex = -1;
        target.focus();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  },
};

/**
 * Prefers reduced motion check
 */
export const motion = {
  /**
   * Check if user prefers reduced motion
   * @returns {boolean}
   */
  prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },

  /**
   * Get animation duration based on user preference
   * @param {number} normalDuration - Normal animation duration in ms
   * @returns {number}
   */
  getDuration(normalDuration) {
    return this.prefersReducedMotion() ? 0 : normalDuration;
  },
};

/**
 * High contrast mode check
 */
export const highContrast = {
  /**
   * Check if user prefers high contrast
   * @returns {boolean}
   */
  prefersHighContrast() {
    return window.matchMedia('(prefers-contrast: high)').matches;
  },
};

/**
 * ARIA utilities
 */
export const aria = {
  /**
   * Generate unique ID for ARIA attributes
   * @param {string} prefix - Prefix for the ID
   * @returns {string}
   */
  generateId(prefix = 'aria') {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  },

  /**
   * Set expanded state on an element
   * @param {HTMLElement} element
   * @param {boolean} expanded
   */
  setExpanded(element, expanded) {
    element.setAttribute('aria-expanded', expanded.toString());
  },

  /**
   * Set hidden state on an element
   * @param {HTMLElement} element
   * @param {boolean} hidden
   */
  setHidden(element, hidden) {
    element.setAttribute('aria-hidden', hidden.toString());
  },
};

export default {
  focusUtils,
  announce,
  keyboard,
  contrast,
  skipLink,
  motion,
  highContrast,
  aria,
};

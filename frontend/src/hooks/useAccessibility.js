/**
 * FACTLY - Accessibility Hooks
 * React hooks for accessibility features
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { accessibility } from '../utils';

/**
 * Hook to manage focus trap within a modal/dialog
 * @param {boolean} isActive - Whether the focus trap is active
 * @returns {React.RefObject} Ref to attach to the container element
 */
export const useFocusTrap = (isActive) => {
  const containerRef = useRef(null);
  const cleanupRef = useRef(null);

  useEffect(() => {
    if (isActive && containerRef.current) {
      cleanupRef.current = accessibility.focusUtils.trapFocus(containerRef.current);
    }

    return () => {
      if (cleanupRef.current) {
        cleanupRef.current();
      }
    };
  }, [isActive]);

  return containerRef;
};

/**
 * Hook to announce messages to screen readers
 * @returns {Function} Announce function
 */
export const useAnnouncer = () => {
  return useCallback((message, priority = 'polite') => {
    accessibility.announce.message(message, priority);
  }, []);
};

/**
 * Hook to detect reduced motion preference
 * @returns {boolean} Whether user prefers reduced motion
 */
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
};

/**
 * Hook to detect high contrast preference
 * @returns {boolean} Whether user prefers high contrast
 */
export const useHighContrast = () => {
  const [prefersHighContrast, setPrefersHighContrast] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    setPrefersHighContrast(mediaQuery.matches);

    const handleChange = (e) => {
      setPrefersHighContrast(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersHighContrast;
};

/**
 * Hook to manage skip link
 * @param {string} targetId - ID of the main content element
 */
export const useSkipLink = (targetId) => {
  useEffect(() => {
    accessibility.skipLink.create(targetId);
  }, [targetId]);
};

/**
 * Hook to handle keyboard shortcuts
 * @param {Object} keyMap - Map of key combinations to handlers
 * @param {Object} options - Options for the hook
 */
export const useKeyboardShortcuts = (keyMap, options = {}) => {
  const { disabled = false } = options;

  useEffect(() => {
    if (disabled) return;

    const handleKeyDown = (e) => {
      const key = e.key.toLowerCase();
      const ctrl = e.ctrlKey || e.metaKey;
      const alt = e.altKey;
      const shift = e.shiftKey;

      for (const [shortcut, handler] of Object.entries(keyMap)) {
        const parts = shortcut.toLowerCase().split('+');
        const shortcutKey = parts[parts.length - 1];
        const needsCtrl = parts.includes('ctrl') || parts.includes('cmd');
        const needsAlt = parts.includes('alt');
        const needsShift = parts.includes('shift');

        if (
          key === shortcutKey &&
          ctrl === needsCtrl &&
          alt === needsAlt &&
          shift === needsShift
        ) {
          e.preventDefault();
          handler(e);
          break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [keyMap, disabled]);
};

/**
 * Hook to manage aria-expanded state
 * @param {boolean} initialState - Initial expanded state
 * @returns {Array} [expanded, toggle, setExpanded]
 */
export const useExpanded = (initialState = false) => {
  const [expanded, setExpanded] = useState(initialState);

  const toggle = useCallback(() => {
    setExpanded((prev) => !prev);
  }, []);

  return [expanded, toggle, setExpanded];
};

/**
 * Hook to detect if element is in viewport
 * @param {Object} options - IntersectionObserver options
 * @returns {Array} [ref, isInViewport]
 */
export const useInViewport = (options = {}) => {
  const ref = useRef(null);
  const [isInViewport, setIsInViewport] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      setIsInViewport(entry.isIntersecting);
    }, options);

    observer.observe(element);
    return () => observer.disconnect();
  }, [options]);

  return [ref, isInViewport];
};

/**
 * Hook to manage live region announcements
 * @returns {Object} Live region props and announce function
 */
export const useLiveRegion = () => {
  const [message, setMessage] = useState('');
  const [priority, setPriority] = useState('polite');

  const announce = useCallback((msg, prio = 'polite') => {
    setMessage(msg);
    setPriority(prio);
  }, []);

  const liveRegionProps = {
    'aria-live': priority,
    'aria-atomic': 'true',
    className: 'sr-only',
  };

  return { announce, liveRegionProps, message };
};

export default {
  useFocusTrap,
  useAnnouncer,
  useReducedMotion,
  useHighContrast,
  useSkipLink,
  useKeyboardShortcuts,
  useExpanded,
  useInViewport,
  useLiveRegion,
};

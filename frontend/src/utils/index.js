/**
 * FACTLY - Utilities Index
 * Central export for all utility functions
 */

export { default as accessibility } from './accessibility';
export { default as performance } from './performance';

// Re-export individual utilities for convenience
export const {
  focusUtils,
  announce,
  keyboard,
  contrast,
  skipLink,
  motion,
  highContrast,
  aria,
} = accessibility;

export const {
  debounce,
  throttle,
  memoize,
  lazyLoadImages,
  preloadResources,
  prefetchResources,
  performanceMetrics,
  animationOptimizer,
  cache,
  network,
  imageOptimizer,
} = performance;

/**
 * FACTLY - Utilities Index
 * Central export for all utility functions
 */

import { focusUtils, announce, keyboard, contrast, skipLink, motion, highContrast, aria } from './accessibility';
export { focusUtils, announce, keyboard, contrast, skipLink, motion, highContrast, aria };
export { default as accessibility } from './accessibility';
export { default as performance } from './performance';

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

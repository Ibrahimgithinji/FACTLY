/**
 * FACTLY - Performance Utilities
 * Helper functions for optimizing application performance
 */

/**
 * Debounce function to limit how often a function can fire
 * @param {Function} func - The function to debounce
 * @param {number} wait - Milliseconds to wait
 * @param {boolean} immediate - Whether to trigger on leading edge
 * @returns {Function}
 */
export const debounce = (func, wait = 300, immediate = false) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func(...args);
  };
};

/**
 * Throttle function to limit execution rate
 * @param {Function} func - The function to throttle
 * @param {number} limit - Milliseconds between executions
 * @returns {Function}
 */
export const throttle = (func, limit = 300) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Memoize function to cache results
 * @param {Function} fn - The function to memoize
 * @returns {Function}
 */
export const memoize = (fn) => {
  const cache = new Map();
  return (...args) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
};

/**
 * Lazy load images using Intersection Observer
 */
export const lazyLoadImages = () => {
  if (!('IntersectionObserver' in window)) {
    // Fallback for browsers without IntersectionObserver
    const images = document.querySelectorAll('img[data-src]');
    images.forEach((img) => {
      img.src = img.dataset.src;
      img.removeAttribute('data-src');
    });
    return;
  }

  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        imageObserver.unobserve(img);
      }
    });
  });

  document.querySelectorAll('img[data-src]').forEach((img) => {
    imageObserver.observe(img);
  });
};

/**
 * Preload critical resources
 * @param {Array<string>} urls - Array of URLs to preload
 * @param {string} as - Resource type (script, style, image, etc.)
 */
export const preloadResources = (urls, as = 'script') => {
  urls.forEach((url) => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    link.as = as;
    if (as === 'font') {
      link.crossOrigin = 'anonymous';
    }
    document.head.appendChild(link);
  });
};

/**
 * Prefetch resources for anticipated navigation
 * @param {Array<string>} urls - Array of URLs to prefetch
 */
export const prefetchResources = (urls) => {
  urls.forEach((url) => {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
  });
};

/**
 * Measure performance metrics
 */
export const performanceMetrics = {
  /**
   * Get Core Web Vitals
   * @returns {Object}
   */
  getCoreWebVitals() {
    const metrics = {};

    // Largest Contentful Paint
    if ('web-vitals' in window) {
      // Would use web-vitals library in production
    }

    // First Contentful Paint
    const fcpEntry = performance.getEntriesByName('first-contentful-paint')[0];
    if (fcpEntry) {
      metrics.fcp = fcpEntry.startTime;
    }

    // Time to First Byte
    const navigationEntry = performance.getEntriesByType('navigation')[0];
    if (navigationEntry) {
      metrics.ttfb = navigationEntry.responseStart;
      metrics.domContentLoaded = navigationEntry.domContentLoadedEventEnd;
      metrics.loadComplete = navigationEntry.loadEventEnd;
    }

    return metrics;
  },

  /**
   * Measure function execution time
   * @param {Function} fn - Function to measure
   * @param {string} label - Label for the measurement
   */
  measure(fn, label = 'Function') {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    console.log(`${label} took ${(end - start).toFixed(2)}ms`);
    return result;
  },

  /**
   * Mark performance timeline
   * @param {string} name - Mark name
   */
  mark(name) {
    if (performance && performance.mark) {
      performance.mark(name);
    }
  },

  /**
   * Measure between marks
   * @param {string} name - Measure name
   * @param {string} startMark - Start mark name
   * @param {string} endMark - End mark name
   */
  measureMarks(name, startMark, endMark) {
    if (performance && performance.measure) {
      performance.measure(name, startMark, endMark);
      const entries = performance.getEntriesByName(name);
      return entries[entries.length - 1];
    }
  },
};

/**
 * Optimize animations for performance
 */
export const animationOptimizer = {
  /**
   * Use requestAnimationFrame with fallback
   * @param {Function} callback
   * @returns {number}
   */
  raf(callback) {
    return (
      window.requestAnimationFrame ||
      window.webkitRequestAnimationFrame ||
      ((cb) => setTimeout(cb, 16))
    )(callback);
  },

  /**
   * Cancel animation frame
   * @param {number} id
   */
  cancelRaf(id) {
    (
      window.cancelAnimationFrame ||
      window.webkitCancelAnimationFrame ||
      ((id) => clearTimeout(id))
    )(id);
  },

  /**
   * Batch DOM reads and writes
   * @param {Function} readFn - Function for reading DOM
   * @param {Function} writeFn - Function for writing DOM
   */
  batchDom(readFn, writeFn) {
    // Read phase
    const readValues = readFn();
    
    // Write phase in next frame
    this.raf(() => {
      writeFn(readValues);
    });
  },
};

/**
 * Cache management utilities
 */
export const cache = {
  /**
   * Simple in-memory cache with TTL
   */
  createCache(ttl = 5 * 60 * 1000) { // 5 minutes default
    const store = new Map();

    return {
      get(key) {
        const item = store.get(key);
        if (!item) return null;
        
        if (Date.now() > item.expiry) {
          store.delete(key);
          return null;
        }
        
        return item.value;
      },

      set(key, value) {
        store.set(key, {
          value,
          expiry: Date.now() + ttl,
        });
      },

      delete(key) {
        store.delete(key);
      },

      clear() {
        store.clear();
      },
    };
  },

  /**
   * LocalStorage wrapper with error handling
   */
  localStorage: {
    get(key) {
      try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
      } catch (e) {
        console.warn('Error reading from localStorage:', e);
        return null;
      }
    },

    set(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
      } catch (e) {
        console.warn('Error writing to localStorage:', e);
        return false;
      }
    },

    remove(key) {
      try {
        localStorage.removeItem(key);
        return true;
      } catch (e) {
        console.warn('Error removing from localStorage:', e);
        return false;
      }
    },
  },
};

/**
 * Network utilities
 */
export const network = {
  /**
   * Check if user is online
   * @returns {boolean}
   */
  isOnline() {
    return navigator.onLine;
  },

  /**
   * Get connection info
   * @returns {Object}
   */
  getConnectionInfo() {
    const connection = navigator.connection ||
      navigator.mozConnection ||
      navigator.webkitConnection;

    if (connection) {
      return {
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt,
        saveData: connection.saveData,
      };
    }

    return null;
  },

  /**
   * Check if user has slow connection
   * @returns {boolean}
   */
  isSlowConnection() {
    const connection = this.getConnectionInfo();
    if (!connection) return false;
    
    return connection.saveData ||
      connection.effectiveType === '2g' ||
      connection.effectiveType === 'slow-2g';
  },
};

/**
 * Image optimization utilities
 */
export const imageOptimizer = {
  /**
   * Generate responsive image srcset
   * @param {string} baseUrl - Base image URL
   * @param {Array<number>} widths - Array of widths
   * @returns {string}
   */
  generateSrcset(baseUrl, widths = [320, 640, 960, 1280]) {
    return widths
      .map((width) => `${baseUrl}?w=${width} ${width}w`)
      .join(', ');
  },

  /**
   * Get optimal image format based on browser support
   * @returns {string}
   */
  getOptimalFormat() {
    const canvas = document.createElement('canvas');
    if (canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0) {
      return 'webp';
    }
    return 'jpeg';
  },
};

export default {
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
};

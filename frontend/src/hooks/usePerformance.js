/**
 * FACTLY - Performance Hooks
 * React hooks for performance optimization
 */

import { useEffect, useRef, useCallback, useState, useMemo } from 'react';
import { performance as perfUtils } from '../utils';

/**
 * Hook for debounced value
 * @param {*} value - Value to debounce
 * @param {number} delay - Debounce delay in ms
 * @returns {*} Debounced value
 */
export const useDebounce = (value, delay = 300) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

/**
 * Hook for throttled callback
 * @param {Function} callback - Function to throttle
 * @param {number} limit - Throttle limit in ms
 * @returns {Function} Throttled function
 */
export const useThrottle = (callback, limit = 300) => {
  const throttleRef = useRef(null);

  return useCallback(
    (...args) => {
      if (!throttleRef.current) {
        callback(...args);
        throttleRef.current = true;
        setTimeout(() => {
          throttleRef.current = false;
        }, limit);
      }
    },
    [callback, limit]
  );
};

/**
 * Hook to detect if component is mounted
 * @returns {boolean} Whether component is mounted
 */
export const useIsMounted = () => {
  const isMounted = useRef(false);

  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);

  return useCallback(() => isMounted.current, []);
};

/**
 * Hook for lazy loading images
 * @param {string} src - Image source
 * @param {string} placeholder - Placeholder image
 * @returns {Object} Image loading state and ref
 */
export const useLazyImage = (src, placeholder = '') => {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [isLoaded, setIsLoaded] = useState(false);
  const imageRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setImageSrc(src);
          observer.disconnect();
        }
      });
    });

    if (imageRef.current) {
      observer.observe(imageRef.current);
    }

    return () => observer.disconnect();
  }, [src]);

  const handleLoad = useCallback(() => {
    setIsLoaded(true);
  }, []);

  return { imageRef, imageSrc, isLoaded, handleLoad };
};

/**
 * Hook to measure component render performance
 * @param {string} componentName - Name of the component
 */
export const useRenderPerformance = (componentName) => {
  const renderCount = useRef(0);
  const startTime = useRef(performance.now());

  useEffect(() => {
    renderCount.current += 1;
    const endTime = performance.now();
    const renderTime = endTime - startTime.current;

    if (process.env.NODE_ENV === 'development') {
      console.log(
        `[Performance] ${componentName} rendered ${renderCount.current} times. ` +
        `Last render: ${renderTime.toFixed(2)}ms`
      );
    }

    startTime.current = endTime;
  });
};

/**
 * Hook for infinite scroll
 * @param {Function} onLoadMore - Callback when more items should be loaded
 * @param {boolean} hasMore - Whether there are more items to load
 * @returns {React.RefObject} Ref to attach to the sentinel element
 */
export const useInfiniteScroll = (onLoadMore, hasMore) => {
  const sentinelRef = useRef(null);

  useEffect(() => {
    if (!hasMore) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          onLoadMore();
        }
      },
      { rootMargin: '100px' }
    );

    if (sentinelRef.current) {
      observer.observe(sentinelRef.current);
    }

    return () => observer.disconnect();
  }, [onLoadMore, hasMore]);

  return sentinelRef;
};

/**
 * Hook to detect online/offline status
 * @returns {boolean} Whether user is online
 */
export const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
};

/**
 * Hook to detect slow connection
 * @returns {boolean} Whether connection is slow
 */
export const useSlowConnection = () => {
  const [isSlow, setIsSlow] = useState(false);

  useEffect(() => {
    const connection = navigator.connection ||
      navigator.mozConnection ||
      navigator.webkitConnection;

    if (connection) {
      const checkConnection = () => {
        setIsSlow(
          connection.saveData ||
          connection.effectiveType === '2g' ||
          connection.effectiveType === 'slow-2g'
        );
      };

      checkConnection();
      connection.addEventListener('change', checkConnection);
      return () => connection.removeEventListener('change', checkConnection);
    }
  }, []);

  return isSlow;
};

/**
 * Hook for memoized callback with dependency tracking
 * @param {Function} factory - Factory function
 * @param {Array} deps - Dependencies
 * @returns {*} Memoized value
 */
export const useMemoized = (factory, deps) => {
  return useMemo(factory, deps);
};

/**
 * Hook for RAF-based animation
 * @param {Function} callback - Animation callback
 * @param {boolean} isActive - Whether animation is active
 */
export const useAnimationFrame = (callback, isActive) => {
  const requestRef = useRef();
  const previousTimeRef = useRef();

  useEffect(() => {
    if (!isActive) return;

    const animate = (time) => {
      if (previousTimeRef.current !== undefined) {
        const deltaTime = time - previousTimeRef.current;
        callback(deltaTime);
      }
      previousTimeRef.current = time;
      requestRef.current = requestAnimationFrame(animate);
    };

    requestRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(requestRef.current);
  }, [isActive, callback]);
};

/**
 * Hook for window size with debounce
 * @param {number} debounceMs - Debounce time in ms
 * @returns {Object} Window width and height
 */
export const useWindowSize = (debounceMs = 250) => {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    const handleResize = perfUtils.debounce(() => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }, debounceMs);

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [debounceMs]);

  return size;
};

/**
 * Hook for scroll position with throttle
 * @param {number} throttleMs - Throttle time in ms
 * @returns {Object} Scroll X and Y
 */
export const useScrollPosition = (throttleMs = 100) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleScroll = perfUtils.throttle(() => {
      setPosition({
        x: window.scrollX,
        y: window.scrollY,
      });
    }, throttleMs);

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [throttleMs]);

  return position;
};

export default {
  useDebounce,
  useThrottle,
  useIsMounted,
  useLazyImage,
  useRenderPerformance,
  useInfiniteScroll,
  useOnlineStatus,
  useSlowConnection,
  useMemoized,
  useAnimationFrame,
  useWindowSize,
  useScrollPosition,
};

/**
 * FACTLY - Intelligent Data Fetching Hook (STABLE VERSION)
 * 
 * Provides robust data fetching with:
 * - AbortController for request cancellation on unmount
 * - 30-second timeout to prevent UI hangs
 * - Deduplication for identical in-flight requests
 * - Exponential backoff retry (max 2 retries) for network errors only
 * - Never retries 4xx HTTP errors
 * - Stable refs to prevent infinite re-render loops
 * 
 * @version 4.0.0
 * @date 2026-03-31
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// ============================================================================
// Module-Level Request Deduplication Map
// ============================================================================

/** @type {Map<string, {abortController: AbortController, promise: Promise<any>}>} */
const inFlightRequests = new Map();

/**
 * Generate a unique key for request deduplication.
 */
const getRequestKey = (method, url, body = null) => {
  if (body) {
    try {
      const bodyHash = JSON.stringify(body);
      return `${method.toUpperCase()}:${url}:${bodyHash}`;
    } catch (e) {
      return `${method.toUpperCase()}:${url}`;
    }
  }
  return `${method.toUpperCase()}:${url}`;
};

// ============================================================================
// Cache Storage with TTL
// ============================================================================

/** @type {Map<string, {data: any, timestamp: number}>} */
const cacheStore = new Map();

/** Cache time-to-live in milliseconds (5 minutes) */
const CACHE_TTL_MS = 5 * 60 * 1000;

const getCachedData = (cacheKey) => {
  const cached = cacheStore.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
    return cached.data;
  }
  if (cached) {
    cacheStore.delete(cacheKey);
  }
  return null;
};

const setCachedData = (cacheKey, data) => {
  cacheStore.set(cacheKey, {
    data,
    timestamp: Date.now()
  });
};

// ============================================================================
// Exponential Backoff (max 2 retries)
// ============================================================================

const calculateDelay = (attempt) => {
  const delays = [2000, 4000];
  return delays[attempt] || 2000;
};

// ============================================================================
// Error Classification - Only retry network errors
// ============================================================================

const classifyError = (error, response) => {
  if (!response) {
    return {
      recoverable: true,
      retry: true,
      message: 'Network connection failed. Please check your internet connection.'
    };
  }

  if (response.status >= 400 && response.status < 500) {
    return {
      recoverable: false,
      retry: false,
      message: getClientErrorMessage(response.status, error.message)
    };
  }

  if (response.status >= 500) {
    return {
      recoverable: true,
      retry: true,
      message: 'Server error. The service is temporarily unavailable.'
    };
  }

  return {
    recoverable: true,
    retry: false,
    message: error.message || 'An unexpected error occurred.'
  };
};

const getClientErrorMessage = (status, defaultMessage) => {
  const messages = {
    400: 'Invalid request. Please check your input.',
    401: 'Authentication required. Please log in again.',
    403: 'Access denied. You do not have permission.',
    404: 'Resource not found.',
    422: 'Validation error. Please check your input.',
    429: 'Too many requests. Please wait before retrying.'
  };
  return messages[status] || defaultMessage || 'An error occurred.';
};

// ============================================================================
// Main Hook Implementation
// ============================================================================

export const useIntelligentFetch = (url, options = {}) => {
  const {
    method = 'GET',
    body = null,
    headers = {},
    autoFetch = false,
    retryAttempts = 2,
    useCache = true,
    onSuccess = null,
    onError = null,
  } = options;

  // State - exactly as required: data, loading, error
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Refs for all values that can change
  const methodRef = useRef(method);
  const urlRef = useRef(url);
  const bodyRef = useRef(body);
  const headersRef = useRef(headers);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  const retryAttemptsRef = useRef(retryAttempts);

  // Keep refs synchronized
  useEffect(() => {
    methodRef.current = method;
  }, [method]);

  useEffect(() => {
    urlRef.current = url;
  }, [url]);

  useEffect(() => {
    bodyRef.current = body;
  }, [body]);

  useEffect(() => {
    headersRef.current = headers;
  }, [headers]);

  useEffect(() => {
    onSuccessRef.current = onSuccess;
  }, [onSuccess]);

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  useEffect(() => {
    retryAttemptsRef.current = retryAttempts;
  }, [retryAttempts]);

  // Refs for lifecycle management
  const abortControllerRef = useRef(null);
  const timeoutRef = useRef(null);
  const mountedRef = useRef(true);

  // Stable key generation using refs
  const getCacheKey = useCallback(() => {
    return `fetch_${methodRef.current}_${urlRef.current}`;
  }, []);

  const getDedupKey = useCallback(() => {
    return getRequestKey(methodRef.current, urlRef.current, bodyRef.current);
  }, []);

  const cancelExistingRequest = useCallback((dedupKey) => {
    const existing = inFlightRequests.get(dedupKey);
    if (existing) {
      if (existing.abortController && existing.abortController.abort) {
        existing.abortController.abort();
      }
      inFlightRequests.delete(dedupKey);
    }
  }, []);

  /**
   * Main fetch function with retry logic.
   */
  const fetchData = useCallback(async () => {
    const dedupKey = getDedupKey();
    const cacheKey = getCacheKey();

    if (!mountedRef.current) {
      return;
    }

    cancelExistingRequest(dedupKey);

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    inFlightRequests.set(dedupKey, { abortController });

    // 30-second timeout
    const REQUEST_TIMEOUT_MS = 30000;
    timeoutRef.current = setTimeout(() => {
      if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
        abortController.abort();
      }
    }, REQUEST_TIMEOUT_MS);

    setLoading(true);
    setData(null);
    setError(null);

    // Check cache first
    if (useCache) {
      const cachedData = getCachedData(cacheKey);
      if (cachedData) {
        inFlightRequests.delete(dedupKey);
        if (timeoutRef.current) clearTimeout(timeoutRef.current);
        
        setData(cachedData);
        setLoading(false);
        return cachedData;
      }
    }

    let lastError = null;

    for (let attempt = 0; attempt <= retryAttemptsRef.current; attempt++) {
      try {
        if (!mountedRef.current) {
          inFlightRequests.delete(dedupKey);
          return;
        }

        if (abortController.signal.aborted) {
          inFlightRequests.delete(dedupKey);
          return;
        }

        const fetchOptions = {
          method: methodRef.current.toUpperCase(),
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...headersRef.current
          },
          signal: abortController.signal
        };

        if (bodyRef.current && (methodRef.current.toUpperCase() === 'POST' || methodRef.current.toUpperCase() === 'PUT')) {
          fetchOptions.body = JSON.stringify(bodyRef.current);
        }

        const response = await fetch(urlRef.current, fetchOptions);

        inFlightRequests.delete(dedupKey);

        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }

        if (!mountedRef.current) {
          return;
        }

        if (abortController.signal.aborted) {
          return;
        }

        if (!response.ok) {
          const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
          error.status = response.status;
          
          const classifiedError = classifyError(error, response);

          if (classifiedError.retry && attempt < retryAttemptsRef.current) {
            const delay = calculateDelay(attempt);
            
            await new Promise(resolve => {
              timeoutRef.current = setTimeout(resolve, delay);
            });

            if (!mountedRef.current || abortController.signal.aborted) {
              return;
            }
            continue;
          }
          
          setError(classifiedError.message);
          setLoading(false);
          return null;
        }

        const responseData = await response.json();

        if (!mountedRef.current) {
          return;
        }

        if (useCache && response.ok) {
          setCachedData(cacheKey, responseData);
        }

        setData(responseData);
        setLoading(false);

        if (onSuccessRef.current) {
          onSuccessRef.current(responseData);
        }

        return responseData;

      } catch (err) {
        inFlightRequests.delete(dedupKey);

        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = null;
        }

        if (err.name === 'AbortError') {
          return;
        }

        lastError = err;

        if (attempt >= retryAttemptsRef.current) {
          break;
        }
      } finally {
        // Only set loading to false if not aborted
        if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
          setLoading(false);
        }
      }
    }

    if (!mountedRef.current) {
      return;
    }

    if (useCache) {
      const cachedData = getCachedData(cacheKey);
      if (cachedData) {
        setData(cachedData);
        setLoading(false);
        
        if (onErrorRef.current) {
          onErrorRef.current(lastError, { usedFallback: true });
        }
        return cachedData;
      }
    }

    const errorMessage = lastError?.message || 'An unexpected error occurred.';
    setError(errorMessage);
    setLoading(false);

    if (onErrorRef.current) {
      onErrorRef.current(lastError, { usedFallback: false });
    }

    return null;
  }, [
    getDedupKey,
    getCacheKey,
    cancelExistingRequest,
    useCache
  ]);

  const refetch = useCallback(async () => {
    return fetchData();
  }, [fetchData]);

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    cancelExistingRequest(getDedupKey());
    setLoading(false);
  }, [cancelExistingRequest, getDedupKey]);

  const clearCache = useCallback(() => {
    const cacheKey = getCacheKey();
    cacheStore.delete(cacheKey);
  }, [getCacheKey]);

  // Auto-fetch effect
  useEffect(() => {
    if (!autoFetch || !url) {
      return;
    }

    mountedRef.current = true;
    
    // Fix: abort the actual in-flight request instead of creating new one
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    fetchData();

    return () => {
      mountedRef.current = false;
      
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      cancelExistingRequest(getDedupKey());
    };
  }, [autoFetch, url]); // Only stable deps

  // Cleanup on unmount
  useEffect(() => {
    mountedRef.current = true;
    
    return () => {
      mountedRef.current = false;
      
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      cancelExistingRequest(getDedupKey());
    };
  }, [cancelExistingRequest, getDedupKey]);

  return {
    data,
    loading,
    error,
    refetch
  };
};

export default useIntelligentFetch;

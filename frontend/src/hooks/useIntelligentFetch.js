/**
 * FACTLY - Intelligent Data Fetching Hook
 * Provides robust data fetching with retry mechanisms, caching, and error handling
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// Cache storage for offline support
const cacheStore = new Map();
const CACHE_EXPIRY = 5 * 60 * 1000; // 5 minutes

/**
 * Intelligent error classification for AI-powered error handling
 */
const classifyError = (error, response) => {
  // Network errors
  if (!response) {
    return {
      type: 'NETWORK_ERROR',
      severity: 'high',
      message: 'Network connection failed. Please check your internet connection.',
      recoverable: true,
      retryStrategy: 'exponential'
    };
  }

  // HTTP status-based classification
  if (response.status === 401) {
    return {
      type: 'AUTH_ERROR',
      severity: 'high',
      message: 'Authentication required. Please log in again.',
      recoverable: false,
      retryStrategy: 'none'
    };
  }

  if (response.status === 403) {
    return {
      type: 'PERMISSION_ERROR',
      severity: 'high',
      message: 'Access denied. You do not have permission to access this resource.',
      recoverable: false,
      retryStrategy: 'none'
    };
  }

  if (response.status === 404) {
    return {
      type: 'NOT_FOUND',
      severity: 'medium',
      message: 'The requested resource was not found.',
      recoverable: false,
      retryStrategy: 'none'
    };
  }

  if (response.status >= 500) {
    return {
      type: 'SERVER_ERROR',
      severity: 'high',
      message: 'Server error. The service is temporarily unavailable.',
      recoverable: true,
      retryStrategy: 'exponential'
    };
  }

  if (response.status === 429) {
    return {
      type: 'RATE_LIMIT',
      severity: 'medium',
      message: 'Too many requests. Please wait a moment before trying again.',
      recoverable: true,
      retryStrategy: 'rate_limited'
    };
  }

  // Parse error message from response
  return {
    type: 'UNKNOWN_ERROR',
    severity: 'medium',
    message: error.message || 'An unexpected error occurred.',
    recoverable: true,
    retryStrategy: 'simple'
  };
};

/**
 * Calculate delay with exponential backoff and jitter
 */
const calculateDelay = (attempt, baseDelay = 1000, maxDelay = 30000, strategy = 'exponential') => {
  if (strategy === 'rate_limited') {
    // For rate limiting, use a longer fixed delay
    return Math.min(baseDelay * 10, maxDelay);
  }
  
  // Exponential backoff: baseDelay * 2^attempt
  const exponentialDelay = baseDelay * Math.pow(2, attempt);
  
  // Add jitter (±20%) to prevent thundering herd
  const jitter = exponentialDelay * 0.2 * (Math.random() * 2 - 1);
  
  return Math.min(exponentialDelay + jitter, maxDelay);
};

/**
 * Get cached data if available and not expired
 */
const getCachedData = (cacheKey) => {
  const cached = cacheStore.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_EXPIRY) {
    return cached.data;
  }
  cacheStore.delete(cacheKey);
  return null;
};

/**
 * Store data in cache
 */
const setCachedData = (cacheKey, data) => {
  cacheStore.set(cacheKey, {
    data,
    timestamp: Date.now()
  });
};

/**
 * Main intelligent fetch hook
 */
export const useIntelligentFetch = (url, options = {}) => {
  const {
    method = 'GET',
    body = null,
    headers = {},
    autoFetch = true,
    retryAttempts = 3,
    retryDelay = 1000,
    useCache = true,
    cacheKey = null,
    onSuccess = null,
    onError = null,
    dataFormat = 'auto' // 'auto', 'results', 'trends', 'data'
  } = options;

  // State management
  const [data, setData] = useState(null);
  const [rawData, setRawData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [errorInfo, setErrorInfo] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, loading, success, error, refreshing
  const [retryCount, setRetryCount] = useState(0);
  const [lastFetchTime, setLastFetchTime] = useState(null);
  const [dataSource, setDataSource] = useState(null); // 'api', 'cache', 'fallback'

  // Refs for cleanup
  const abortControllerRef = useRef(null);
  const retryTimeoutRef = useRef(null);
  const mountedRef = useRef(true);

  // Generate cache key from URL
  const getCacheKey = useCallback(() => {
    return cacheKey || `fetch_${method}_${url}`;
  }, [cacheKey, method, url]);

  /**
   * Parse response data with support for multiple formats
   */
  const parseResponseData = useCallback((responseData) => {
    // Handle different response formats
    if (dataFormat === 'results') {
      return responseData.results || [];
    }
    
    if (dataFormat === 'trends') {
      return responseData.trends || [];
    }
    
    if (dataFormat === 'data') {
      return responseData.data || responseData;
    }
    
    // Auto-detect format (default)
    if (Array.isArray(responseData)) {
      return responseData;
    }
    
    // Try common patterns
    return responseData.results || responseData.trends || responseData.data || responseData;
  }, [dataFormat]);

  /**
   * Main fetch function with retry logic
   */
  const fetchData = useCallback(async (isRefresh = false, forceRetry = false) => {
    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Create new abort controller
    abortControllerRef.current = new AbortController();
    
    // Update state
    if (isRefresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setStatus(isRefresh ? 'refreshing' : 'loading');
    setError(null);
    setErrorInfo(null);
    
    // Check cache first (only for non-refresh requests)
    const cacheKey = getCacheKey();
    if (!isRefresh && useCache) {
      const cachedData = getCachedData(cacheKey);
      if (cachedData) {
        setData(parseResponseData(cachedData));
        setRawData(cachedData);
        setDataSource('cache');
        setIsLoading(false);
        setStatus('success');
        return cachedData;
      }
    }

    // Attempt fetch with retries
    let lastError = null;
    const currentRetryCount = 0;
    
    for (let attempt = currentRetryCount; attempt <= retryAttempts; attempt++) {
      try {
        setRetryCount(attempt);
        
        const fetchOptions = {
          method,
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...headers
          },
          signal: abortControllerRef.current.signal
        };

        if (body) {
          fetchOptions.body = JSON.stringify(body);
        }

        const response = await fetch(url, fetchOptions);
        
        // Check if request was aborted
        if (!mountedRef.current) {
          return;
        }

        if (!response.ok) {
          const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
          error.status = response.status;
          
          // Classify error
          const classifiedError = classifyError(error, response);
          setErrorInfo(classifiedError);
          
          // Check if we should retry
          if (classifiedError.recoverable && attempt < retryAttempts) {
            const delay = calculateDelay(attempt, retryDelay, 30000, classifiedError.retryStrategy);
            console.log(`Retry attempt ${attempt + 1}/${retryAttempts} after ${delay}ms...`);
            
            if (mountedRef.current) {
              await new Promise(resolve => {
                retryTimeoutRef.current = setTimeout(resolve, delay);
              });
            }
            continue;
          }
          
          throw error;
        }

        // Parse response
        const responseData = await response.json();
        
        if (!mountedRef.current) {
          return;
        }

        // Cache successful response
        if (useCache && response.ok) {
          setCachedData(cacheKey, responseData);
        }

        // Update state
        const parsedData = parseResponseData(responseData);
        setData(parsedData);
        setRawData(responseData);
        setDataSource('api');
        setLastFetchTime(Date.now());
        setStatus('success');
        setError(null);
        
        if (onSuccess) {
          onSuccess(parsedData, responseData);
        }
        
        return responseData;

      } catch (err) {
        // Check if request was aborted
        if (err.name === 'AbortError') {
          console.log('Request aborted');
          return;
        }

        lastError = err;
        
        // Don't retry further if this was the last attempt
        if (attempt >= retryAttempts) {
          break;
        }
      }
    }

    // All retries exhausted
    if (!mountedRef.current) {
      return;
    }

    // Try to use cached data as fallback
    if (useCache) {
      const cachedData = getCachedData(cacheKey);
      if (cachedData) {
        console.log('Using cached data as fallback');
        const parsedData = parseResponseData(cachedData);
        setData(parsedData);
        setRawData(cachedData);
        setDataSource('fallback');
        setStatus('success');
        
        if (onError) {
          onError(lastError, { usedFallback: true });
        }
        
        return cachedData;
      }
    }

    // Set error state
    const classifiedError = classifyError(lastError, null);
    setErrorInfo(classifiedError);
    setError(lastError);
    setStatus('error');
    
    if (onError) {
      onError(lastError, { usedFallback: false });
    }

    throw lastError;

  }, [url, method, body, headers, retryAttempts, retryDelay, useCache, getCacheKey, parseResponseData, onSuccess, onError]);

  /**
   * Manual refresh function
   */
  const refresh = useCallback(async () => {
    // Clear cache for this key
    const cacheKey = getCacheKey();
    cacheStore.delete(cacheKey);
    
    return fetchData(true, true);
  }, [fetchData, getCacheKey]);

  /**
   * Retry failed request
   */
  const retry = useCallback(() => {
    return fetchData(false, true);
  }, [fetchData]);

  /**
   * Clear cache for this endpoint
   */
  const clearCache = useCallback(() => {
    const cacheKey = getCacheKey();
    cacheStore.delete(cacheKey);
  }, [getCacheKey]);

  // Auto-fetch on mount
  useEffect(() => {
    mountedRef.current = true;
    if (autoFetch) {
      fetchData();
    }
    
    return () => {
      mountedRef.current = false;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, [url]); // eslint-disable-line react-hooks/exhaustive-deps

  // Expose the fetchData function for manual calls
  useEffect(() => {
    // This effect just to establish the dependency
  }, [fetchData]);

  return {
    data,
    rawData,
    isLoading,
    isRefreshing,
    error,
    errorInfo,
    status,
    retryCount,
    lastFetchTime,
    dataSource,
    fetch: fetchData,
    refresh,
    retry,
    clearCache
  };
};

/**
 * Hook for fetching trends with specialized handling
 */
export const useTrendsFetch = (baseUrl, options = {}) => {
  const defaultOptions = {
    method: 'GET',
    useCache: true,
    retryAttempts: 3,
    retryDelay: 1500,
    dataFormat: 'auto',
    ...options
  };

  const buildUrl = useCallback((params = {}) => {
    const url = new URL(`${baseUrl}/api/trends/`);
    if (params.limit) url.searchParams.append('limit', params.limit);
    if (params.region) url.searchParams.append('region', params.region);
    if (params.risk_level) url.searchParams.append('risk_level', params.risk_level);
    if (params.verification_status) url.searchParams.append('verification_status', params.verification_status);
    return url.toString();
  }, [baseUrl]);

  return useIntelligentFetch('', {
    ...defaultOptions,
    // Override url builder
    url: buildUrl(options.params)
  });
};

/**
 * Hook for fetching analytics data
 */
export const useAnalyticsFetch = (baseUrl, options = {}) => {
  return useIntelligentFetch(`${baseUrl}/api/analytics/`, {
    method: 'GET',
    useCache: true,
    retryAttempts: 3,
    retryDelay: 1000,
    dataFormat: 'auto',
    ...options
  });
};

export default useIntelligentFetch;

/**
 * Centralized API utility module
 * Provides robust error handling for fetch requests including:
 * - Content-Type validation before JSON parsing
 * - Proper status code checking
 * - Consistent error response handling
 * - Network error handling
 * - Automatic token refresh
 * - Automatic retry for network failures
 */

import { API_ENDPOINTS } from './api';

// Token storage keys
const ACCESS_TOKEN_KEY = 'authToken';
const REFRESH_TOKEN_KEY = 'refreshToken';

// Retry configuration
const RETRY_CONFIG = {
  maxAttempts: 3,
  delayMs: 1000,
  backoffMultiplier: 2,
  retryableStatuses: [408, 429, 500, 502, 503, 504],
};

// Storage helpers
const getStoredToken = (key) => {
  try {
    return sessionStorage.getItem(key);
  } catch (e) {
    console.error('Error reading from sessionStorage:', e);
    return null;
  }
};

/**
 * Exponential backoff delay
 * @param {number} attempt - Attempt number (0-indexed)
 * @returns {Promise} Resolves after delay
 */
const exponentialBackoff = async (attempt) => {
  const delay = RETRY_CONFIG.delayMs * Math.pow(RETRY_CONFIG.backoffMultiplier, attempt);
  return new Promise(resolve => setTimeout(resolve, delay));
};

/**
 * Parse response safely - checks Content-Type before parsing JSON
 * @param {Response} response - Fetch response object
 * @returns {Object} Parsed JSON data
 */
const parseResponse = async (response) => {
  const contentType = response.headers.get('content-type');
  
  if (!contentType || !contentType.includes('application/json')) {
    // Response is not JSON - might be HTML error page
    const text = await response.text();
    const truncatedText = text.substring(0, 500);
    
    console.error('Non-JSON response received:', truncatedText);
    
    if (!response.ok) {
      // Server returned an error HTML page (404, 500, etc.)
      throw new Error(`Server error: ${response.status} ${response.statusText}`);
    }
    
    throw new Error('Invalid response format from server');
  }
  
  return response.json();
};

/**
 * Try to refresh the access token
 * @returns {boolean} True if refresh was successful
 */
const tryRefreshToken = async () => {
  const refreshToken = getStoredToken(REFRESH_TOKEN_KEY);
  if (!refreshToken) {
    return false;
  }

  try {
    const response = await fetch(API_ENDPOINTS.REFRESH, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      return false;
    }

    const data = await response.json();
    if (data.access) {
      sessionStorage.setItem(ACCESS_TOKEN_KEY, data.access);
      return true;
    }
    return false;
  } catch (e) {
    console.error('Token refresh failed:', e);
    return false;
  }
};

/**
 * Retry wrapper for API calls with exponential backoff
 * @param {Function} fetchFn - Function that returns fetch promise
 * @param {string} context - Context for logging (e.g., 'trending', 'verify')
 * @returns {Promise} Response from fetch
 */
const withRetry = async (fetchFn, context = 'API') => {
  let lastError;
  
  for (let attempt = 0; attempt < RETRY_CONFIG.maxAttempts; attempt++) {
    try {
      const response = await fetchFn();
      
      // Retry on specific status codes
      if (RETRY_CONFIG.retryableStatuses.includes(response.status)) {
        if (attempt < RETRY_CONFIG.maxAttempts - 1) {
          console.warn(`[${context}] Retryable status ${response.status}, retrying... (attempt ${attempt + 1}/${RETRY_CONFIG.maxAttempts})`);
          await exponentialBackoff(attempt);
          continue;
        }
      }
      
      return response;
    } catch (error) {
      lastError = error;
      
      // Retry on network errors
      if (attempt < RETRY_CONFIG.maxAttempts - 1) {
        console.warn(`[${context}] Network error, retrying... (attempt ${attempt + 1}/${RETRY_CONFIG.maxAttempts}):`, error.message);
        await exponentialBackoff(attempt);
        continue;
      }
    }
  }
  
  throw lastError || new Error(`${context} request failed after ${RETRY_CONFIG.maxAttempts} attempts`);
};

/**
 * Make a POST request with proper error handling, token refresh, and retry logic
 * @param {string} url - API endpoint URL
 * @param {Object} data - Request body data
 * @param {Object} options - Additional fetch options
 * @returns {Object} Response data with success status
 */
export const apiPost = async (url, data, options = {}) => {
  // Get current access token
  let accessToken = getStoredToken(ACCESS_TOKEN_KEY);
  
  try {
    const response = await withRetry(() => 
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
          ...options.headers,
        },
        body: JSON.stringify(data),
        ...options,
      }),
      'POST'
    );

    // If unauthorized and we have a refresh token, try to refresh
    if (response.status === 401 && accessToken) {
      const refreshed = await tryRefreshToken();
      if (refreshed) {
        // Retry the request with new token
        accessToken = getStoredToken(ACCESS_TOKEN_KEY);
        const retryResponse = await withRetry(() =>
          fetch(url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${accessToken}`,
              ...options.headers,
            },
            body: JSON.stringify(data),
            ...options,
          }),
          'POST-Retry'
        );
        
        const result = await parseResponse(retryResponse);
        
        if (!retryResponse.ok) {
          throw new Error(result.error || result.message || 'Request failed');
        }
        
        return { success: true, data: result };
      }
    }

    const result = await parseResponse(response);
    
    if (!response.ok) {
      throw new Error(result.error || result.message || 'Request failed');
    }
    
    return { success: true, data: result };
  } catch (error) {
    console.error('API POST request error:', error);
    
    // Handle our custom errors
    if (error.message && (
      error.message.includes('Server error') ||
      error.message.includes('Invalid response') ||
      error.message.includes('Request failed')
    )) {
      return { success: false, error: error.message };
    }
    
    // Handle network errors
    if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
      return { success: false, error: 'Network error. Please check your connection.' };
    }
    
    // Handle JSON parsing errors
    if (error instanceof SyntaxError) {
      return { success: false, error: 'Invalid response from server. Please try again.' };
    }
    
    return { success: false, error: error.message || 'An unexpected error occurred.' };
  }
};

/**
 * Make a GET request with proper error handling, token refresh, and retry logic
 * @param {string} url - API endpoint URL
 * @param {Object} options - Additional fetch options
 * @returns {Object} Response data with success status
 */
export const apiGet = async (url, options = {}) => {
  // Get current access token
  let accessToken = getStoredToken(ACCESS_TOKEN_KEY);
  
  try {
    const response = await withRetry(() =>
      fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
          ...options.headers,
        },
        ...options,
      }),
      'GET'
    );

    // If unauthorized and we have a refresh token, try to refresh
    if (response.status === 401 && accessToken) {
      const refreshed = await tryRefreshToken();
      if (refreshed) {
        // Retry the request with new token
        accessToken = getStoredToken(ACCESS_TOKEN_KEY);
        const retryResponse = await withRetry(() =>
          fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${accessToken}`,
              ...options.headers,
            },
            ...options,
          }),
          'GET-Retry'
        );
        
        const result = await parseResponse(retryResponse);
        
        if (!retryResponse.ok) {
          throw new Error(result.error || result.message || 'Request failed');
        }
        
        return { success: true, data: result };
      }
    }
    
    const result = await parseResponse(response);
    
    if (!response.ok) {
      throw new Error(result.error || result.message || 'Request failed');
    }
    
    return { success: true, data: result };
  } catch (error) {
    console.error('API GET request error:', error);
    
    if (error.message && (
      error.message.includes('Server error') ||
      error.message.includes('Invalid response') ||
      error.message.includes('Request failed')
    )) {
      return { success: false, error: error.message };
    }
    
    if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
      return { success: false, error: 'Network error. Please check your connection.' };
    }
    
    if (error instanceof SyntaxError) {
      return { success: false, error: 'Invalid response from server. Please try again.' };
    }
    
    return { success: false, error: error.message || 'An unexpected error occurred.' };
  }
};

// Export convenience methods for auth endpoints
export const authApi = {
  login: (email, password) => apiPost(API_ENDPOINTS.LOGIN, { email, password }),
  signup: (name, email, password) => apiPost(API_ENDPOINTS.SIGNUP, { name, email, password }),
  forgotPassword: (email) => apiPost(API_ENDPOINTS.FORGOT_PASSWORD, { email }),
  verifyResetToken: (token) => apiPost(API_ENDPOINTS.VERIFY_RESET_TOKEN, { token }),
  resetPassword: (token, newPassword, confirmPassword) => 
    apiPost(API_ENDPOINTS.RESET_PASSWORD, { 
      token, 
      new_password: newPassword, 
      confirm_password: confirmPassword 
    }),
};

export default {
  apiPost,
  apiGet,
  authApi,
};

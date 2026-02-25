/**
 * Centralized API utility module
 * Provides robust error handling for fetch requests including:
 * - Content-Type validation before JSON parsing
 * - Proper status code checking
 * - Consistent error response handling
 * - Network error handling
 */

import { API_ENDPOINTS } from './api';

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
 * Make a POST request with proper error handling
 * @param {string} url - API endpoint URL
 * @param {Object} data - Request body data
 * @param {Object} options - Additional fetch options
 * @returns {Object} Response data with success status
 */
export const apiPost = async (url, data, options = {}) => {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(data),
      ...options,
    });

    const result = await parseResponse(response);
    
    if (!response.ok) {
      throw new Error(result.error || result.message || 'Request failed');
    }
    
    return { success: true, data: result };
  } catch (error) {
    console.error('API request error:', error);
    
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
 * Make a GET request with proper error handling
 * @param {string} url - API endpoint URL
 * @param {Object} options - Additional fetch options
 * @returns {Object} Response data with success status
 */
export const apiGet = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    const result = await parseResponse(response);
    
    if (!response.ok) {
      throw new Error(result.error || result.message || 'Request failed');
    }
    
    return { success: true, data: result };
  } catch (error) {
    console.error('API request error:', error);
    
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

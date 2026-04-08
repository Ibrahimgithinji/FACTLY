// API Configuration
// This file centralizes the API base URL for easy configuration

// Get the API base URL from environment variable or use default
// In production, set REACT_APP_API_URL in your .env file
const getApiBaseUrl = () => {
  // Check for environment variable
  const envUrl = process.env.REACT_APP_API_URL;
  if (envUrl) {
    return envUrl;
  }
  
  // In development with proxy, use relative URLs
  // In production, this should be the full URL
  return '';
};

export const API_BASE_URL = getApiBaseUrl();

// API endpoint helpers - matching Django backend paths under /api/verification/
export const API_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/api/verification/auth/login/`,
  SIGNUP: `${API_BASE_URL}/api/verification/auth/signup/`,
  REFRESH: `${API_BASE_URL}/api/verification/auth/refresh/`,
  FORGOT_PASSWORD: `${API_BASE_URL}/api/verification/auth/forgot-password/`,
  VERIFY_RESET_TOKEN: `${API_BASE_URL}/api/verification/auth/verify-reset-token/`,
  RESET_PASSWORD: `${API_BASE_URL}/api/verification/auth/reset-password/`,
  VERIFY: `${API_BASE_URL}/api/verification/verify/`,
  ENHANCED_VERIFY: `${API_BASE_URL}/api/verification/verify/enhanced/`,
  HISTORY: `${API_BASE_URL}/api/verification/history/`,
  USER: `${API_BASE_URL}/api/verification/user/`,
  TRENDING: `${API_BASE_URL}/api/verification/trending/`,
  TRENDING_LIVE: `${API_BASE_URL}/api/verification/trending/live/`,
  GLOBAL_EVENTS: `${API_BASE_URL}/api/verification/global-events/`,
  REFRESH_DATA: `${API_BASE_URL}/api/verification/refresh/`,
};

// Export for use in fetch requests
export default API_BASE_URL;

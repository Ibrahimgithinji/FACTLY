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
  
  // Default to localhost:8000 for development
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiBaseUrl();

// API endpoint helpers
export const API_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/api/auth/login/`,
  SIGNUP: `${API_BASE_URL}/api/auth/signup/`,
  FORGOT_PASSWORD: `${API_BASE_URL}/api/auth/forgot-password/`,
  VERIFY_RESET_TOKEN: `${API_BASE_URL}/api/auth/verify-reset-token/`,
  RESET_PASSWORD: `${API_BASE_URL}/api/auth/reset-password/`,
  VERIFY: `${API_BASE_URL}/api/verify/`,
  HISTORY: `${API_BASE_URL}/api/history/`,
  USER: `${API_BASE_URL}/api/user/`,
};

// Export for use in fetch requests
export default API_BASE_URL;

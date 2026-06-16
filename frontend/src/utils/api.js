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
  LOGOUT: `${API_BASE_URL}/api/verification/auth/logout/`,
  USER_PROFILE: `${API_BASE_URL}/api/verification/user/`,
  USER: `${API_BASE_URL}/api/verification/user/`,
  TRENDING: `${API_BASE_URL}/api/verification/trending/`,
  TRENDING_LIVE: `${API_BASE_URL}/api/verification/trending/live/`,
  GLOBAL_EVENTS: `${API_BASE_URL}/api/verification/global-events/`,
  REFRESH_DATA: `${API_BASE_URL}/api/verification/refresh/`,
};

// Content/Article API endpoints
export const CONTENT_ENDPOINTS = {
  HOMEPAGE: `${API_BASE_URL}/api/content/homepage/`,
  ARTICLES: `${API_BASE_URL}/api/content/articles/`,
  ARTICLE: (slug) => `${API_BASE_URL}/api/content/articles/${slug}/`,
  RELATED: (slug) => `${API_BASE_URL}/api/content/articles/${slug}/related/`,
  COMMENTS: (id) => `${API_BASE_URL}/api/content/articles/${id}/comments/`,
  CATEGORIES: `${API_BASE_URL}/api/content/categories/`,
  SEARCH: `${API_BASE_URL}/api/content/search/`,
  GUEST_SUBMIT: `${API_BASE_URL}/api/content/guest-submit/`,
  NEWSLETTER: `${API_BASE_URL}/api/content/newsletter/`,
  BOOKMARKS: `${API_BASE_URL}/api/content/bookmarks/`,
  BOOKMARK: (articleId) => `${API_BASE_URL}/api/content/bookmarks/${articleId}/`,
  AUTHOR: (authorId) => `${API_BASE_URL}/api/content/authors/${authorId}/`,
};

// Export for use in fetch requests
export default API_BASE_URL;

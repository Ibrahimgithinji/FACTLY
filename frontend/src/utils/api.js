import { API_BASE_URL } from './constants';

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
  HISTORY_DETAIL: (id) => `${API_BASE_URL}/api/verification/history/${id}/`,
  HISTORY_CLEAR: `${API_BASE_URL}/api/verification/history/clear/`,
  LOGOUT: `${API_BASE_URL}/api/verification/auth/logout/`,
  CSRF: `${API_BASE_URL}/api/verification/auth/csrf/`,
  USER_PROFILE: `${API_BASE_URL}/api/verification/user/`,
  USER_STATS: `${API_BASE_URL}/api/verification/user/stats/`,
  USER: `${API_BASE_URL}/api/verification/user/`,
  TRENDING: `${API_BASE_URL}/api/verification/trending/`,
  TRENDING_LIVE: `${API_BASE_URL}/api/verification/trending/live/`,
  GLOBAL_EVENTS: `${API_BASE_URL}/api/verification/global-events/`,
  REFRESH_DATA: `${API_BASE_URL}/api/verification/refresh/`,
  CLAIMS: `${API_BASE_URL}/api/verification/claims/`,
};

// Content/Article API endpoints
export const CONTENT_ENDPOINTS = {
  HOMEPAGE: `${API_BASE_URL}/api/content/homepage/`,
  DAILY_STORY: `${API_BASE_URL}/api/content/daily-story/`,
  STORY: (slug) => `${API_BASE_URL}/api/content/stories/${slug}/`,
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
  PUSH_VAPID_KEY: `${API_BASE_URL}/api/content/push/vapid-public-key/`,
  PUSH_SUBSCRIBE: `${API_BASE_URL}/api/content/push/subscribe/`,
  ALERTS: `${API_BASE_URL}/api/alerts/`,
};

// Export for use in fetch requests
export default API_BASE_URL;

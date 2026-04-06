/**
 * Application Constants
 * Centralized configuration and constants used throughout the app
 */

// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const API_TIMEOUT_MS = 30000; // 30 seconds
export const API_RETRY_ATTEMPTS = 3;
export const API_RETRY_DELAY_MS = 1000; // Base delay for exponential backoff

// Verification
export const MAX_INPUT_LENGTH = 5000;
export const MIN_INPUT_LENGTH = 10;
export const VERIFICATION_RATE_LIMIT_MESSAGE = 'Too many requests. Please wait a moment before trying again.';

// Polling
export const TRENDING_POLL_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
export const MAX_POLLING_RETRIES = 3;

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

// Confidence Levels
export const CONFIDENCE_THRESHOLDS = {
  HIGH: 0.8,
  MEDIUM: 0.6,
  LOW: 0.4,
};

export const CONFIDENCE_LABELS = {
  HIGH: 'High Confidence',
  MEDIUM: 'Medium Confidence',
  LOW: 'Low Confidence',
};

// Risk Levels
export const RISK_LEVELS = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
};

export const RISK_LEVEL_LABELS = {
  critical: 'Critical',
  high: 'High Risk',
  medium: 'Medium',
  low: 'Low Risk',
};

// Verification Status
export const VERIFICATION_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  VERIFIED: 'verified',
  FALSE: 'false',
  UNVERIFIABLE: 'unverifiable',
};

// Auth
export const TOKEN_EXPIRY_THRESHOLD_MS = 5 * 60 * 1000; // Refresh 5 minutes before expiry
export const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection and try again.',
  TIMEOUT_ERROR: 'Request took too long. Please try again.',
  RATE_LIMITED: 'Too many requests. Please wait before trying again.',
  UNAUTHORIZED: 'Your session has expired. Please log in again.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  SERVER_ERROR: 'Server error. Please try again later.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  VERIFIED: 'Content verified successfully.',
  SAVED: 'Changes saved successfully.',
  DELETED: 'Item deleted successfully.',
  COPIED: 'Copied to clipboard.',
};

// Routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  VERIFY: '/verify',
  RESULTS: '/results',
  HISTORY: '/history',
  ABOUT: '/about',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
};

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'factly_auth_token',
  REFRESH_TOKEN: 'factly_refresh_token',
  USER_PREFERENCES: 'factly_user_preferences',
  RECENT_SEARCHES: 'factly_recent_searches',
  THEME: 'factly_theme',
};

// Theme
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto',
};

export default {
  API_BASE_URL,
  MAX_INPUT_LENGTH,
  CONFIDENCE_THRESHOLDS,
  RISK_LEVELS,
  VERIFICATION_STATUS,
  ERROR_MESSAGES,
  ROUTES,
};

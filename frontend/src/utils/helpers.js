/**
 * Utility functions for API calls with error handling and retry logic
 */

import { ERROR_MESSAGES } from './constants';

/**
 * Handle different API error types and return user-friendly messages
 * @param {Error} error - The error object
 * @returns {string} User-friendly error message
 */
export const getErrorMessage = (error) => {
  if (!error) return ERROR_MESSAGES.UNKNOWN_ERROR;

  // Network errors
  if (error.message === 'Network Error' || error.code === 'ECONNABORTED') {
    return ERROR_MESSAGES.NETWORK_ERROR;
  }

  // Timeout
  if (error.message === 'timeout' || error.code === 'timeout') {
    return ERROR_MESSAGES.TIMEOUT_ERROR;
  }

  // HTTP status codes
  if (error.status) {
    switch (error.status) {
      case 429:
        return ERROR_MESSAGES.RATE_LIMITED;
      case 401:
        return ERROR_MESSAGES.UNAUTHORIZED;
      case 403:
        return ERROR_MESSAGES.FORBIDDEN;
      case 404:
        return ERROR_MESSAGES.NOT_FOUND;
      case 422:
      case 400:
        return ERROR_MESSAGES.VALIDATION_ERROR;
      case 500:
      case 502:
      case 503:
        return ERROR_MESSAGES.SERVER_ERROR;
      default:
        return error.message || ERROR_MESSAGES.UNKNOWN_ERROR;
    }
  }

  return error.message || ERROR_MESSAGES.UNKNOWN_ERROR;
};

/**
 * Format date for display
 * @param {string|Date} date - Date to format
 * @param {boolean} includeTime - Include time in format
 * @returns {string} Formatted date string
 */
export const formatDate = (date, includeTime = false) => {
  if (!date) return 'N/A';

  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;

    if (isNaN(dateObj.getTime())) return 'Invalid date';

    const options = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      ...(includeTime && {
        hour: '2-digit',
        minute: '2-digit',
      }),
    };

    return dateObj.toLocaleDateString('en-US', options);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid date';
  }
};

/**
 * Format relative time (e.g., "2 hours ago")
 * @param {string|Date} date - Date to format
 * @returns {string} Relative time string
 */
export const formatRelativeTime = (date) => {
  if (!date) return 'Unknown';

  try {
    const targetDate = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const diff = now - targetDate;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return formatDate(targetDate);
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return 'Unknown';
  }
};

/**
 * Get confidence level label from score
 * @param {number} confidence - Confidence score (0-1)
 * @returns {object} {level, label, color}
 */
export const getConfidenceLevel = (confidence) => {
  if (confidence >= 0.8) {
    return {
      level: 'HIGH',
      label: 'High Confidence',
      color: '#16a34a',
      backgroundColor: '#dcfce7',
    };
  } else if (confidence >= 0.6) {
    return {
      level: 'MEDIUM',
      label: 'Medium Confidence',
      color: '#ca8a04',
      backgroundColor: '#fef3c7',
    };
  } else {
    return {
      level: 'LOW',
      label: 'Low Confidence',
      color: '#dc2626',
      backgroundColor: '#fee2e2',
    };
  }
};

/**
 * Get risk level styling
 * @param {string} riskLevel - Risk level (critical, high, medium, low)
 * @returns {object} {color, backgroundColor, label}
 */
export const getRiskLevelStyle = (riskLevel) => {
  const styles = {
    critical: {
      color: '#dc2626',
      backgroundColor: '#fee2e2',
      label: 'Critical',
      icon: '🔴',
    },
    high: {
      color: '#ea580c',
      backgroundColor: '#fed7aa',
      label: 'High Risk',
      icon: '🟠',
    },
    medium: {
      color: '#ca8a04',
      backgroundColor: '#fef3c7',
      label: 'Medium',
      icon: '🟡',
    },
    low: {
      color: '#16a34a',
      backgroundColor: '#dcfce7',
      label: 'Low Risk',
      icon: '🟢',
    },
  };

  return styles[riskLevel.toLowerCase()] || styles.low;
};

/**
 * Sanitize user input to prevent XSS
 * @param {string} input - User input
 * @returns {string} Sanitized input
 */
export const sanitizeInput = (input) => {
  if (!input) return '';

  try {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
  } catch (error) {
    console.error('Error sanitizing input:', error);
    return input;
  }
};

/**
 * Validate URL format
 * @param {string} url - URL to validate
 * @returns {boolean} True if valid URL
 */
export const isValidUrl = (url) => {
  try {
    new URL(url);
    return true;
  } catch (error) {
    return false;
  }
};

/**
 * Debounce function for search and resize operations
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttle function for scroll and resize operations
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in ms
 * @returns {Function} Throttled function
 */
export const throttle = (func, limit) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} True if successful
 */
export const copyToClipboard = async (text) => {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return true;
    }
  } catch (error) {
    console.error('Error copying to clipboard:', error);
    return false;
  }
};

/**
 * Truncate text with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
};

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
export const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

export default {
  getErrorMessage,
  formatDate,
  formatRelativeTime,
  getConfidenceLevel,
  getRiskLevelStyle,
  sanitizeInput,
  isValidUrl,
  debounce,
  throttle,
  copyToClipboard,
  truncateText,
  generateId,
};

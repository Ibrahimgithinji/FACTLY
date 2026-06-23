import { API_ENDPOINTS } from './api';

const RETRY_CONFIG = {
  maxAttempts: 2,
  delayMs: 1000,
  backoffMultiplier: 2,
  retryableStatuses: [408, 429],
};

const exponentialBackoff = async (attempt) => {
  const delay = RETRY_CONFIG.delayMs * Math.pow(RETRY_CONFIG.backoffMultiplier, attempt);
  return new Promise(resolve => setTimeout(resolve, delay));
};

const baseFetchOptions = {
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
};

const withRetry = async (fetchFn, context = 'API') => {
  let lastError;

  for (let attempt = 0; attempt < RETRY_CONFIG.maxAttempts; attempt++) {
    try {
      const response = await fetchFn();

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

      if (attempt < RETRY_CONFIG.maxAttempts - 1) {
        console.warn(`[${context}] Network error, retrying... (attempt ${attempt + 1}/${RETRY_CONFIG.maxAttempts}):`, error.message);
        await exponentialBackoff(attempt);
        continue;
      }
    }
  }

  throw lastError || new Error(`${context} request failed after ${RETRY_CONFIG.maxAttempts} attempts`);
};

const apiRequest = async (url, method, data = null, options = {}) => {
  try {
    const fetchParams = {
      ...baseFetchOptions,
      method,
      ...options,
    };

    if (data) {
      fetchParams.body = JSON.stringify(data);
    }

    let response = await withRetry(() => fetch(url, fetchParams), method);

    if (response.status === 401) {
      const refreshResponse = await fetch(API_ENDPOINTS.REFRESH, {
        ...baseFetchOptions,
        method: 'POST',
      });
      if (refreshResponse.ok) {
        response = await withRetry(() => fetch(url, fetchParams), method);
      } else {
        return { success: false, error: 'Session expired. Please log in again.', authError: true };
      }
    }

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || result.message || 'Request failed');
    }

    return { success: true, data: result };
  } catch (error) {
    if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
      return { success: false, error: 'Network error. Please check your connection.' };
    }

    if (error instanceof SyntaxError) {
      return { success: false, error: 'Invalid response from server. Please try again.' };
    }

    return { success: false, error: error.message || 'An unexpected error occurred.' };
  }
};

export const apiPost = async (url, data, options = {}) => {
  return apiRequest(url, 'POST', data, options);
};

export const apiGet = async (url, options = {}) => {
  return apiRequest(url, 'GET', null, options);
};

export const apiPut = async (url, data, options = {}) => {
  return apiRequest(url, 'PUT', data, options);
};

export const authApi = {
  login: (email, password) => apiPost(API_ENDPOINTS.LOGIN, { email, password }),
  signup: (name, email, password) => apiPost(API_ENDPOINTS.SIGNUP, { name, email, password }),
  forgotPassword: (email) => apiPost(API_ENDPOINTS.FORGOT_PASSWORD, { email }),
  verifyResetToken: (token) => apiPost(API_ENDPOINTS.VERIFY_RESET_TOKEN, { token }),
  resetPassword: (token, newPassword, confirmPassword) =>
    apiPost(API_ENDPOINTS.RESET_PASSWORD, {
      token,
      new_password: newPassword,
      confirm_password: confirmPassword,
    }),
};

const apiClient = {
  apiPost,
  apiGet,
  apiPut,
  authApi,
};

export default apiClient;

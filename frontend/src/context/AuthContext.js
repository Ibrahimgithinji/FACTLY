import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { API_ENDPOINTS } from '../utils/api';

const AuthContext = createContext(null);

// Token storage keys
const ACCESS_TOKEN_KEY = 'authToken';
const REFRESH_TOKEN_KEY = 'refreshToken';
const USER_KEY = 'user';

// Token refresh threshold - refresh if token expires in less than this many minutes
const TOKEN_REFRESH_THRESHOLD_MINUTES = 5;

// Helper to get token expiration time from JWT (without verification)
const getTokenExpiration = (token) => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp ? new Date(payload.exp * 1000) : null;
  } catch (e) {
    return null;
  }
};

// Check if token is expired or about to expire
const isTokenExpiringSoon = (token) => {
  if (!token) return true;
  const expiration = getTokenExpiration(token);
  if (!expiration) return false; // Can't determine, assume valid
  
  const now = new Date();
  const threshold = new Date(now.getTime() + TOKEN_REFRESH_THRESHOLD_MINUTES * 60 * 1000);
  return expiration < threshold;
};

// Storage helpers (using sessionStorage for XSS protection)
const getStoredToken = (key) => {
  try {
    return sessionStorage.getItem(key);
  } catch (e) {
    console.error('Error reading from sessionStorage:', e);
    return null;
  }
};

const setStoredToken = (key, value) => {
  try {
    if (value) {
      sessionStorage.setItem(key, value);
    } else {
      sessionStorage.removeItem(key);
    }
  } catch (e) {
    console.error('Error writing to sessionStorage:', e);
  }
};

const getStoredUser = () => {
  try {
    const userStr = sessionStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  } catch (e) {
    console.error('Error reading user from sessionStorage:', e);
    return null;
  }
};

const setStoredUser = (user) => {
  try {
    if (user) {
      sessionStorage.setItem(USER_KEY, JSON.stringify(user));
    } else {
      sessionStorage.removeItem(USER_KEY);
    }
  } catch (e) {
    console.error('Error writing user to sessionStorage:', e);
  }
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing tokens on mount - use sessionStorage for XSS protection
    const accessToken = getStoredToken(ACCESS_TOKEN_KEY);
    const refreshToken = getStoredToken(REFRESH_TOKEN_KEY);
    const storedUser = getStoredUser();
    
    if (accessToken && storedUser) {
      setUser(storedUser);
      setIsAuthenticated(true);
    } else if (refreshToken && storedUser) {
      // If we have refresh token but no access token, try to refresh
      // This handles cases where access token expired but refresh token is still valid
      refreshAccessToken(refreshToken, storedUser);
    }
    setIsLoading(false);
  }, []);

  // Function to refresh access token using refresh token
  const refreshAccessToken = useCallback(async (refreshToken, userData) => {
    try {
      const response = await fetch(API_ENDPOINTS.REFRESH, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        console.error('Token refresh failed: Non-JSON response');
        // Clear tokens and log out
        setStoredToken(ACCESS_TOKEN_KEY, null);
        setStoredToken(REFRESH_TOKEN_KEY, null);
        setStoredUser(null);
        setUser(null);
        setIsAuthenticated(false);
        return false;
      }

      if (!response.ok) {
        console.error('Token refresh failed with status:', response.status);
        // Clear tokens and log out
        setStoredToken(ACCESS_TOKEN_KEY, null);
        setStoredToken(REFRESH_TOKEN_KEY, null);
        setStoredUser(null);
        setUser(null);
        setIsAuthenticated(false);
        return false;
      }

      const data = await response.json();
      
      if (data.access) {
        // Store new access token
        setStoredToken(ACCESS_TOKEN_KEY, data.access);
        setUser(userData);
        setIsAuthenticated(true);
        return true;
      }
      
      return false;
    } catch (err) {
      console.error('Token refresh error:', err);
      // Clear tokens and log out on error
      setStoredToken(ACCESS_TOKEN_KEY, null);
      setStoredToken(REFRESH_TOKEN_KEY, null);
      setStoredUser(null);
      setUser(null);
      setIsAuthenticated(false);
      return false;
    }
  }, []);

  // Function to get valid access token (refreshes if needed)
  const getValidAccessToken = useCallback(async () => {
    const accessToken = getStoredToken(ACCESS_TOKEN_KEY);
    const refreshToken = getStoredToken(REFRESH_TOKEN_KEY);
    
    if (!accessToken) {
      // No access token, try to refresh
      if (refreshToken) {
        const success = await refreshAccessToken(refreshToken, getStoredUser());
        if (success) {
          return getStoredToken(ACCESS_TOKEN_KEY);
        }
      }
      return null;
    }
    
    // Check if token is expiring soon
    if (isTokenExpiringSoon(accessToken) && refreshToken) {
      await refreshAccessToken(refreshToken, getStoredUser());
      return getStoredToken(ACCESS_TOKEN_KEY);
    }
    
    return accessToken;
  }, [refreshAccessToken]);

  // Set up periodic token refresh check
  useEffect(() => {
    if (!isAuthenticated) return;

    // Check token validity every minute
    const checkInterval = setInterval(() => {
      const accessToken = getStoredToken(ACCESS_TOKEN_KEY);
      const refreshToken = getStoredToken(REFRESH_TOKEN_KEY);
      
      if (accessToken && isTokenExpiringSoon(accessToken) && refreshToken) {
        refreshAccessToken(refreshToken, getStoredUser());
      }
    }, 60000); // Check every minute

    return () => clearInterval(checkInterval);
  }, [isAuthenticated, refreshAccessToken]);

  const login = async (email, password) => {
    try {
      const normalizedEmail = email?.trim();
      const response = await fetch(API_ENDPOINTS.LOGIN, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: normalizedEmail, password }),
      });

      // Check if response is JSON before parsing
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Login error: Non-JSON response received:', text.substring(0, 500));
        
        if (!response.ok) {
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        
        throw new Error('Invalid response from server. Please try again.');
      }

      if (!response.ok) {
        let errorMessage = 'Login failed';
        try {
          const error = await response.json();
          errorMessage = error.error || error.message || 'Login failed';
        } catch (e) {
          // If response is not JSON, use default message
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      // Store both access and refresh tokens using localStorage for persistence
      setStoredToken(ACCESS_TOKEN_KEY, data.access);
      setStoredToken(REFRESH_TOKEN_KEY, data.refresh);
      setStoredUser(data.user);
      
      setUser(data.user);
      setIsAuthenticated(true);
      return { success: true };
    } catch (err) {
      console.error('Login error:', err);
      
      if (err.message && (
        err.message.includes('Server error') || 
        err.message.includes('Invalid response')
      )) {
        return { success: false, error: err.message };
      }
      
      return { success: false, error: err.message || 'Login failed. Please try again.' };
    }
  };

  const signup = async (name, email, password) => {
    try {
      const response = await fetch(API_ENDPOINTS.SIGNUP, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      // Check if response is JSON before parsing
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Signup error: Non-JSON response received:', text.substring(0, 500));
        
        if (!response.ok) {
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        
        throw new Error('Invalid response from server. Please try again.');
      }

      if (!response.ok) {
        let errorMessage = 'Signup failed';
        try {
          const error = await response.json();
          errorMessage = error.error || error.message || 'Signup failed';
        } catch (e) {
          // If response is not JSON, use default message
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      
      // Store both access and refresh tokens using localStorage for persistence
      setStoredToken(ACCESS_TOKEN_KEY, data.access);
      setStoredToken(REFRESH_TOKEN_KEY, data.refresh);
      setStoredUser(data.user);
      
      setUser(data.user);
      setIsAuthenticated(true);
      return { success: true };
    } catch (err) {
      console.error('Signup error:', err);
      
      if (err.message && (
        err.message.includes('Server error') || 
        err.message.includes('Invalid response')
      )) {
        return { success: false, error: err.message };
      }
      
      return { success: false, error: err.message || 'Signup failed. Please try again.' };
    }
  };

  const logout = () => {
    // Clear tokens from sessionStorage
    setStoredToken(ACCESS_TOKEN_KEY, null);
    setStoredToken(REFRESH_TOKEN_KEY, null);
    setStoredUser(null);
    
    setUser(null);
    setIsAuthenticated(false);
  };

  const forgotPassword = async (email) => {
    try {
      const response = await fetch(API_ENDPOINTS.FORGOT_PASSWORD, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      // Check if response is JSON before parsing
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        // Response is not JSON - handle HTML or other error pages
        const text = await response.text();
        console.error('Forgot password error: Non-JSON response received:', text.substring(0, 500));
        
        // Try to extract useful error information from HTML response
        let extractedError = null;
        
        // Look for Django error page patterns
        if (response.status === 500) {
          // Extract exception value or error message from Django error page
          const exceptionMatch = text.match(/<pre class="exception_value">(.*?)<\/pre>/s);
          if (exceptionMatch && exceptionMatch[1]) {
            extractedError = exceptionMatch[1].replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
          }
          
          // Also check for specific error messages in the page
          if (!extractedError) {
            const errorSectionMatch = text.match(/<h1[^>]*>(.*?)<\/h1>/s);
            if (errorSectionMatch && errorSectionMatch[1]) {
              extractedError = errorSectionMatch[1].trim();
            }
          }
          
          // Provide helpful message based on common Django 500 errors
          if (extractedError) {
            if (extractedError.includes('DisallowedHost')) {
              throw new Error('Server configuration error. Please contact support or try again later.');
            }
            if (extractedError.includes('Invalid HTTP_HOST')) {
              throw new Error('Server configuration error. Please contact support or try again later.');
            }
            throw new Error(`Server error: ${extractedError.substring(0, 200)}`);
          }
        }
        
        if (!response.ok) {
          // Server returned an error HTML page (404, 500, etc.)
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        
        throw new Error('Invalid response from server. Please try again.');
      }

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to send reset email');
      }

      return { 
        success: true, 
        message: data.message
      };
    } catch (err) {
      console.error('Forgot password error:', err);
      
      // Re-throw if it's already our error
      if (err.message && (
        err.message.includes('Server error') || 
        err.message.includes('Invalid response') ||
        err.message.includes('Failed to send reset email')
      )) {
        return { success: false, error: err.message };
      }
      
      // Handle network errors or JSON parsing errors
      return { 
        success: false, 
        error: err.message || 'Network error. Please check your connection and try again.' 
      };
    }
  };

  const verifyResetToken = async (token) => {
    try {
      const response = await fetch(API_ENDPOINTS.VERIFY_RESET_TOKEN, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      // Check if response is JSON before parsing
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Verify reset token error: Non-JSON response received:', text.substring(0, 500));
        
        if (!response.ok) {
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        
        throw new Error('Invalid response from server. Please try again.');
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || error.message || 'Invalid reset token');
      }

      const data = await response.json();
      return { success: true, email: data.email };
    } catch (err) {
      console.error('Verify reset token error:', err);
      
      if (err.message && (
        err.message.includes('Server error') || 
        err.message.includes('Invalid response') ||
        err.message.includes('Invalid reset token')
      )) {
        return { success: false, error: err.message };
      }
      
      return { success: false, error: err.message || 'Invalid or expired reset link' };
    }
  };

  const resetPassword = async (token, newPassword, confirmPassword) => {
    try {
      const response = await fetch(API_ENDPOINTS.RESET_PASSWORD, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, new_password: newPassword, confirm_password: confirmPassword }),
      });

      // Check if response is JSON before parsing
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('Reset password error: Non-JSON response received:', text.substring(0, 500));
        
        if (!response.ok) {
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }
        
        throw new Error('Invalid response from server. Please try again.');
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || error.message || 'Failed to reset password');
      }

      const data = await response.json();
      return { success: true, message: data.message };
    } catch (err) {
      console.error('Reset password error:', err);
      
      if (err.message && (
        err.message.includes('Server error') || 
        err.message.includes('Invalid response') ||
        err.message.includes('Failed to reset password')
      )) {
        return { success: false, error: err.message };
      }
      
      return { success: false, error: err.message || 'Failed to reset password. Please try again.' };
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    signup,
    logout,
    forgotPassword,
    verifyResetToken,
    resetPassword,
    getValidAccessToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
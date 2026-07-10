import React, { createContext, useState, useContext, useEffect, useCallback, useRef } from 'react';
import { API_ENDPOINTS } from '../utils/api';

const AuthContext = createContext(null);

const fetchOptions = {
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
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
  const abortControllerRef = useRef(null);
  const authPendingRef = useRef(false);

  const fetchUser = useCallback(async () => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    const ac = new AbortController();
    abortControllerRef.current = ac;

    try {
      let response = await fetch(API_ENDPOINTS.USER_PROFILE, {
        ...fetchOptions,
        method: 'GET',
        signal: ac.signal,
      });

      if (response.status === 401) {
        const refreshResponse = await fetch(API_ENDPOINTS.REFRESH, {
          ...fetchOptions,
          method: 'POST',
          signal: ac.signal,
        });

        if (refreshResponse.ok) {
          response = await fetch(API_ENDPOINTS.USER_PROFILE, {
            ...fetchOptions,
            method: 'GET',
            signal: ac.signal,
          });
        } else {
          setUser(null);
          setIsAuthenticated(false);
          return false;
        }
      }

      if (response.ok) {
        const data = await response.json();
        setUser(data);
        setIsAuthenticated(true);
        return true;
      }

      setUser(null);
      setIsAuthenticated(false);
      return false;
    } catch (e) {
      if (e.name === 'AbortError') return false;
      console.warn('fetchUser error:', e);
      return false;
    }
  }, []);

  useEffect(() => {
    fetchUser().finally(() => setIsLoading(false));
  }, [fetchUser]);

  const login = async (email, password) => {
    if (authPendingRef.current) return { success: false, error: 'Already processing authentication.' };
    authPendingRef.current = true;
    try {
      const response = await fetch(API_ENDPOINTS.LOGIN, {
        ...fetchOptions,
        method: 'POST',
        body: JSON.stringify({ email: email?.trim(), password }),
      });

      if (!response.ok) {
        let errorMessage = 'Login failed';
        try {
          const error = await response.json();
          errorMessage = error.error || error.message || 'Login failed';
        } catch (e) {
        }
        throw new Error(errorMessage);
      }

      await fetchUser();
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || 'Login failed. Please try again.' };
    } finally {
      authPendingRef.current = false;
    }
  };

  const signup = async (name, email, password) => {
    if (authPendingRef.current) return { success: false, error: 'Already processing authentication.' };
    authPendingRef.current = true;
    try {
      const response = await fetch(API_ENDPOINTS.SIGNUP, {
        ...fetchOptions,
        method: 'POST',
        body: JSON.stringify({ name, email, password }),
      });

      if (!response.ok) {
        let errorMessage = 'Signup failed';
        try {
          const error = await response.json();
          errorMessage = error.error || error.message || 'Signup failed';
        } catch (e) {
        }
        throw new Error(errorMessage);
      }

      await fetchUser();
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || 'Signup failed. Please try again.' };
    } finally {
      authPendingRef.current = false;
    }
  };

  const logout = async () => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    const ac = new AbortController();
    abortControllerRef.current = ac;
    try {
      await fetch(API_ENDPOINTS.LOGOUT, { ...fetchOptions, method: 'POST', signal: ac.signal });
    } catch (e) {
      if (e.name === 'AbortError') return;
    }
    localStorage.removeItem('factCheckHistory');
    localStorage.removeItem('reverifyClaim');
    sessionStorage.removeItem('factCheckResult');
    sessionStorage.removeItem('factCheckQuery');
    setUser(null);
    setIsAuthenticated(false);
  };

  const forgotPassword = async (email) => {
    try {
      const response = await fetch(API_ENDPOINTS.FORGOT_PASSWORD, {
        ...fetchOptions,
        method: 'POST',
        body: JSON.stringify({ email: email?.trim().toLowerCase() }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to send reset email');
      }

      return { success: true, message: data.message };
    } catch (err) {
      return { success: false, error: err.message || 'Network error. Please check your connection and try again.' };
    }
  };

  const verifyResetToken = async (token) => {
    try {
      const response = await fetch(API_ENDPOINTS.VERIFY_RESET_TOKEN, {
        ...fetchOptions,
        method: 'POST',
        body: JSON.stringify({ token }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || error.message || 'Invalid reset token');
      }

      const data = await response.json();
      return { success: true, email: data.email };
    } catch (err) {
      return { success: false, error: err.message || 'Invalid or expired reset link' };
    }
  };

  const resetPassword = async (token, newPassword, confirmPassword) => {
    try {
      const response = await fetch(API_ENDPOINTS.RESET_PASSWORD, {
        ...fetchOptions,
        method: 'POST',
        body: JSON.stringify({ token, new_password: newPassword, confirm_password: confirmPassword }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || error.message || 'Failed to reset password');
      }

      const data = await response.json();
      return { success: true, message: data.message };
    } catch (err) {
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
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;

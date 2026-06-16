import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
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

  const fetchUser = useCallback(async () => {
    try {
      let response = await fetch(API_ENDPOINTS.USER_PROFILE, {
        ...fetchOptions,
        method: 'GET',
      });

      if (response.status === 401) {
        await fetch(API_ENDPOINTS.REFRESH, {
          ...fetchOptions,
          method: 'POST',
        });
        response = await fetch(API_ENDPOINTS.USER_PROFILE, {
          ...fetchOptions,
          method: 'GET',
        });
      }

      if (response.ok) {
        const data = await response.json();
        setUser(data);
        setIsAuthenticated(true);
        return true;
      }
    } catch (e) {
    }
    setUser(null);
    setIsAuthenticated(false);
    return false;
  }, []);

  const login = async (email, password) => {
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
    }
  };

  const signup = async (name, email, password) => {
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
    }
  };

  const logout = async () => {
    try {
      await fetch(API_ENDPOINTS.LOGOUT, { ...fetchOptions, method: 'POST' });
    } catch (e) {
    }
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

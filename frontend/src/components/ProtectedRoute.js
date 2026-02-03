import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute Component
 * 
 * Wraps routes that require authentication.
 * Redirects unauthenticated users to the login page
 * while preserving the intended destination.
 * 
 * Features:
 * - Loading state with accessible spinner
 * - Preserves redirect location for post-login navigation
 * - Smooth transitions
 */

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div 
        className="loading-container" 
        role="status" 
        aria-live="polite"
        aria-label="Loading authentication status"
      >
        <div 
          className="loading-spinner" 
          aria-hidden="true"
        ></div>
        <p className="loading-text">Checking authentication...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to login page, but save the location they were trying to access
    return (
      <Navigate 
        to="/login" 
        state={{ from: location }} 
        replace 
      />
    );
  }

  return children;
};

export default ProtectedRoute;

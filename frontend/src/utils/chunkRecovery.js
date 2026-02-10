/**
 * Utility to handle and recover from chunk loading errors in React/Webpack
 * applications with lazy loading and Hot Module Replacement (HMR).
 */

import React, { Suspense } from 'react';
import ErrorBoundary from '../components/ErrorBoundary';

/**
 * Reloads the page to recover from chunk loading errors.
 * This is a common fix for HMR-related chunk loading errors.
 */
export const reloadPage = () => {
  // Clear any cached chunks from localStorage or sessionStorage
  try {
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith('webpack')) {
        localStorage.removeItem(key);
      }
    });
  } catch (e) {
    console.warn('Could not clear localStorage:', e);
  }

  // Reload the page
  if (window.location.reload) {
    window.location.reload();
  }
};

/**
 * Attempts to recover from a chunk loading error by reloading the page.
 * Returns true if recovery was attempted, false otherwise.
 */
export const recoverFromChunkError = () => {
  // Check if this is a chunk loading error
  const error = window.__CHUNK_ERROR__;
  if (error) {
    console.warn('Chunk loading error detected, recovering...');
    reloadPage();
    return true;
  }
  return false;
};

/**
 * Sets up a global error listener to catch chunk loading errors.
 * Should be called once at the application entry point.
 */
export const setupChunkErrorRecovery = () => {
  // Listen for unhandled promise rejections which can indicate chunk loading errors
  window.addEventListener('unhandledrejection', (event) => {
    const error = event.reason;
    
    // Check if this is a chunk loading error
    if (error?.name === 'ChunkLoadError' ||
        error?.message?.includes('Loading chunk') ||
        error?.message?.includes('Failed to fetch') ||
        error?.message?.includes('chunk')) {
      
      console.warn('Chunk loading error detected:', error.message);
      event.preventDefault(); // Prevent the default error handling
      
      // Attempt to recover by reloading the page
      setTimeout(() => {
        console.log('Attempting to recover from chunk loading error...');
        reloadPage();
      }, 1000);
    }
  });

  // Also set up a handler for chunk loading errors that might occur during navigation
  window.addEventListener('error', (event) => {
    if (event.message?.includes('Loading chunk') ||
        event.message?.includes('chunk')) {
      console.warn('Chunk loading error caught via window error event:', event.message);
      
      // Attempt to recover
      setTimeout(() => {
        reloadPage();
      }, 1000);
    }
  });
};

/**
 * Higher-order function to wrap a lazy-loaded component with error recovery.
 * The component will attempt to recover from chunk loading errors.
 */
export const withChunkErrorRecovery = (LazyComponent, fallback) => {
  return (props) => (
    <Suspense fallback={fallback || <div>Loading...</div>}>
      <ErrorBoundary>
        <LazyComponent {...props} />
      </ErrorBoundary>
    </Suspense>
  );
};

// eslint-disable-next-line import/no-anonymous-default-export
export default {
  reloadPage,
  recoverFromChunkError,
  setupChunkErrorRecovery,
  withChunkErrorRecovery
};

import React, { Component } from 'react';

/**
 * ErrorBoundary component to catch JavaScript errors anywhere in the child
 * component tree and display a fallback UI instead of crashing the app.
 * Particularly useful for catching lazy-loaded chunk loading errors.
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to the console for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ errorInfo });

    // Check if this is a chunk loading error
    if (error.name === 'ChunkLoadError' || 
        error.message?.includes('Loading chunk') ||
        error.message?.includes('chunk')) {
      console.warn('Chunk loading error detected. Attempting recovery...');
      
      // Attempt to recover by reloading the page
      // This is a common fix for HMR-related chunk loading errors
      setTimeout(() => {
        if (window.location.reload) {
          console.log('Reloading page to recover from chunk loading error...');
          window.location.reload();
        }
      }, 1000);
    }
  }

  handleRetry = () => {
    // Attempt to reload the chunk by forcing a page reload
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI for chunk loading errors
      const isChunkError = this.state.error?.name === 'ChunkLoadError' ||
                           this.state.error?.message?.includes('Loading chunk');

      return (
        <div 
          className="error-boundary-fallback" 
          role="alert"
          style={{
            padding: '2rem',
            textAlign: 'center',
            backgroundColor: '#fff5f5',
            border: '1px solid #feb2b2',
            borderRadius: '8px',
            margin: '1rem'
          }}
        >
          <h2 style={{ color: '#c53030', marginBottom: '1rem' }}>
            {isChunkError ? 'Component Loading Error' : 'Something went wrong'}
          </h2>
          
          <p style={{ color: '#742a2a', marginBottom: '1rem' }}>
            {isChunkError 
              ? 'The requested component failed to load. This may be due to a network issue or a build problem.'
              : 'An unexpected error occurred while loading this component.'
            }
          </p>
          
          {this.state.error?.message && (
            <p style={{ color: '#9b2c2c', fontSize: '0.875rem', marginBottom: '1rem' }}>
              Error: {this.state.error.message}
            </p>
          )}
          
          <button
            onClick={this.handleRetry}
            style={{
              backgroundColor: '#c53030',
              color: 'white',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
            aria-label="Retry loading the component"
          >
            Retry / Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

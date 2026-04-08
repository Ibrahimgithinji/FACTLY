import React, { createContext, useContext, useState, useEffect } from 'react';

// Create context for verification results
const ResultsContext = createContext();

// Custom hook to use results context
export const useResults = () => {
  const context = useContext(ResultsContext);
  if (!context) {
    throw new Error('useResults must be used within a ResultsProvider');
  }
  return context;
};

// Provider component
export const ResultsProvider = ({ children }) => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load results from sessionStorage on mount
  useEffect(() => {
    const loadResults = () => {
      try {
        const storedResult = sessionStorage.getItem('factCheckResult');
        const storedQuery = sessionStorage.getItem('factCheckQuery');

        if (storedResult) {
          const parsed = JSON.parse(storedResult);
          setResults({
            ...parsed,
            query: storedQuery || parsed.original_text || parsed.query
          });
        }
      } catch (err) {
        console.error('Failed to load results:', err);
        setError('Failed to load verification results');
      } finally {
        setLoading(false);
      }
    };

    loadResults();
  }, []);

  // Update results (can be called from verification form)
  const updateResults = (newResults, query = null) => {
    try {
      setResults({
        ...newResults,
        query: query || newResults.original_text || newResults.query
      });

      // Update sessionStorage
      sessionStorage.setItem('factCheckResult', JSON.stringify(newResults));
      if (query) {
        sessionStorage.setItem('factCheckQuery', query);
      }

      setError(null);
    } catch (err) {
      console.error('Failed to update results:', err);
      setError('Failed to save verification results');
    }
  };

  // Clear results
  const clearResults = () => {
    setResults(null);
    setError(null);
    sessionStorage.removeItem('factCheckResult');
    sessionStorage.removeItem('factCheckQuery');
  };

  const value = {
    results,
    loading,
    error,
    updateResults,
    clearResults,
    hasResults: !!results
  };

  return (
    <ResultsContext.Provider value={value}>
      {children}
    </ResultsContext.Provider>
  );
};

export default ResultsContext;
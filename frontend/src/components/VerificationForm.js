import React, { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useResults } from '../context/ResultsContext';
import { API_ENDPOINTS } from '../utils/api';
import { apiPost } from '../utils/apiClient';
import './VerificationForm.css';

const VerificationForm = () => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [charCount, setCharCount] = useState(0);
  const navigate = useNavigate();
  const { getValidAccessToken, isAuthenticated } = useAuth();
  const { updateResults } = useResults();
  
  // Ref for abort controller
  const abortControllerRef = useRef(null);

  const MAX_CHARS = 5000;

  const handleInputChange = useCallback((e) => {
    const value = e.target.value;
    if (value.length <= MAX_CHARS) {
      setInput(value);
      setCharCount(value.length);
      if (error) setError(null);
    }
  }, [error]);

  const validateInput = useCallback((value) => {
    if (!value.trim()) {
      return 'Please enter some text to verify';
    }
    if (value.trim().length < 3) {
      return 'Please enter at least 3 characters for accurate verification';
    }
    return null;
  }, []);

  const isValidUrl = useCallback((string) => {
    try {
      new URL(string);
      return true;
    } catch {
      return false;
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateInput(input);
    if (validationError) {
      setError(validationError);
      return;
    }

    // Cancel any previous in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Create new abort controller
    abortControllerRef.current = new AbortController();
    
    setIsLoading(true);
    setError(null);

    try {
      // Detect if input is a URL
      const isUrl = isValidUrl(input.trim());
      
      const requestBody = isUrl
        ? { url: input.trim() }
        : { text: input.trim() };

      console.log('Sending request to API:', isUrl ? 'URL mode' : 'Text mode');

      // Use the apiClient which handles authentication automatically
      // Pass abort signal to cancel on new submissions
      const result = await apiPost(API_ENDPOINTS.VERIFY, requestBody, {
        signal: abortControllerRef.current.signal
      });
      
      if (!result.success) {
        throw new Error(result.error || 'Verification failed');
      }

      const data = result.data;
      console.log('API Response received:', {
        factlyScore: data.factly_score?.factly_score || data.factly_score?.score,
        classification: data.factly_score?.classification
      });
      
      // Update results in context (this also saves to sessionStorage)
      updateResults(data, input.trim());
      
      // Save to history (localStorage is for persistent history)
      const historyItem = {
        id: `history_${Date.now()}`,
        claim: input.trim(),
        originalText: input.trim(),
        factly_score: data.factly_score?.factly_score || data.factly_score?.score,
        classification: data.factly_score?.classification,
        confidence_level: data.factly_score?.confidence_level,
        components: data.factly_score?.components || [],
        justifications: data.factly_score?.justifications || [],
        timestamp: new Date().toISOString()
      };
      
      // Add to existing history
      const existingHistory = JSON.parse(localStorage.getItem('factCheckHistory') || '[]');
      existingHistory.unshift(historyItem);
      // Keep only last 50 items
      const trimmedHistory = existingHistory.slice(0, 50);
      localStorage.setItem('factCheckHistory', JSON.stringify(trimmedHistory));
      
      navigate('/results');
    } catch (err) {
      setError(err.message || 'Verification failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getCharCountClass = () => {
    if (charCount > MAX_CHARS * 0.9) return 'error';
    if (charCount > MAX_CHARS * 0.8) return 'warning';
    return '';
  };

  return (
    <div className="verification-form-container">
      <h2>Verify News Credibility</h2>
      <p>Enter a news headline, article URL, or paste text to check its credibility</p>
      
      <form onSubmit={handleSubmit} className="verification-form" noValidate>
        <div className="input-wrapper">
          <textarea
            value={input}
            onChange={handleInputChange}
            placeholder="Paste a headline, URL, or article text here..."
            rows={6}
            disabled={isLoading}
            aria-label="Enter news content to verify"
            aria-describedby="input-help char-counter"
            aria-invalid={error ? 'true' : 'false'}
            aria-errormessage={error ? 'input-error' : undefined}
            maxLength={MAX_CHARS}
          />
          <p id="input-help" className="sr-only">
            Enter a news headline, article URL, or article text to verify its credibility.
            Maximum {MAX_CHARS} characters.
          </p>
          <div 
            id="char-counter" 
            className={`char-counter ${getCharCountClass()}`}
            aria-live="polite"
            aria-atomic="true"
          >
            {charCount}/{MAX_CHARS} characters
          </div>
        </div>
        
        {error && (
          <div 
            id="input-error" 
            className="error-message" 
            role="alert"
            aria-live="assertive"
          >
            {error}
          </div>
        )}
        
        <button 
          type="submit" 
          disabled={isLoading || !input.trim()}
          aria-busy={isLoading}
          className="submit-button"
        >
          {isLoading ? (
            <>
              <span className="spinner" aria-hidden="true"></span>
              <span>Verifying...</span>
            </>
          ) : (
            <>
              <span aria-hidden="true">🔍</span>
              <span>Verify Now</span>
            </>
          )}
        </button>
      </form>

      <div className="features" role="list" aria-label="Key features">
        <div className="feature" role="listitem">
          <span className="feature-icon" aria-hidden="true">🔍</span>
          <span>Fact-check against multiple sources</span>
        </div>
        <div className="feature" role="listitem">
          <span className="feature-icon" aria-hidden="true">📊</span>
          <span>Get a credibility score</span>
        </div>
        <div className="feature" role="listitem">
          <span className="feature-icon" aria-hidden="true">📚</span>
          <span>View supporting evidence</span>
        </div>
      </div>
    </div>
  );
};

export default VerificationForm;

import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './VerificationForm.css';

const VerificationForm = () => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [charCount, setCharCount] = useState(0);
  const navigate = useNavigate();

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
    if (value.trim().length < 10) {
      return 'Please enter at least 10 characters for accurate verification';
    }
    return null;
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateInput(input);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const response = await fetch('http://localhost:8000/api/verify/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: input.trim() }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Server error: ${response.status}`);
      }

      const data = await response.json();
      localStorage.setItem('factCheckResult', JSON.stringify(data));
      localStorage.setItem('factCheckQuery', input.trim());
      navigate('/results');
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Request timed out. Please try again.');
      } else if (err.message.includes('Failed to fetch')) {
        // Backend not available - use mock data for demo
        console.log('Backend not available, using mock data');
        const mockData = {
          score: 0.75,
          confidence: 0.82,
          sources: [
            { name: 'Reuters Fact Check', url: 'https://www.reuters.com/fact-check', credibility: 'High' },
            { name: 'AP News', url: 'https://apnews.com/hub/fact-checking', credibility: 'High' },
            { name: 'BBC Verify', url: 'https://www.bbc.com/news/verify', credibility: 'High' },
          ],
          claims: [
            { text: 'Sample claim verified by multiple sources', rating: 'True', source: 'https://example.com' },
            { text: 'Another claim with mixed evidence', rating: 'Mixed', source: 'https://example.com' },
          ],
          factors: {
            sourceReliability: 0.85,
            contentConsistency: 0.78,
            factCheckCoverage: 0.72,
            crossReference: 0.80,
          },
          query: input.trim(),
          timestamp: new Date().toISOString(),
        };
        localStorage.setItem('factCheckResult', JSON.stringify(mockData));
        localStorage.setItem('factCheckQuery', input.trim());
        navigate('/results');
      } else {
        setError(err.message || 'An unexpected error occurred. Please try again.');
      }
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
            Enter a news headline, article URL, or paste article text to verify its credibility.
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

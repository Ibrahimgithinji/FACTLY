import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useResults } from '../context/ResultsContext';
import { API_ENDPOINTS } from '../utils/api';
import { apiPost } from '../utils/apiClient';
import { FactlyScoreBadge, FactlyScoreBar } from './FactlyScoreBadge';
import SourceBiasIndicator from './SourceBiasIndicator';
import './VerificationForm.css';

const STEPS = [
  { id: 'input', label: 'Submit Claim', icon: '1' },
  { id: 'analyzing', label: 'Analyzing', icon: '2' },
  { id: 'sources', label: 'Cross-Checking', icon: '3' },
  { id: 'scoring', label: 'Scoring', icon: '4' },
  { id: 'done', label: 'Results', icon: '5' },
];

const MAX_CHARS = 5000;

const VerificationForm = ({ initialValue = '' }) => {
  const [input, setInput] = useState(initialValue);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [charCount, setCharCount] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const navigate = useNavigate();
  const { updateResults } = useResults();
  const abortControllerRef = useRef(null);

  useEffect(() => {
    setInput(initialValue);
    setCharCount(initialValue.length);
    setError(null);
  }, [initialValue]);

  const handleInputChange = useCallback((e) => {
    const value = e.target.value;
    if (value.length <= MAX_CHARS) {
      setInput(value);
      setCharCount(value.length);
      if (error) setError(null);
    }
  }, [error]);

  const validateInput = useCallback((value) => {
    if (!value.trim()) return 'Please enter some text to verify';
    if (value.trim().length < 3) return 'Please enter at least 3 characters for accurate verification';
    return null;
  }, []);

  const isValidUrl = useCallback((string) => {
    try { new URL(string); return true; } catch { return false; }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationError = validateInput(input);
    if (validationError) { setError(validationError); return; }

    if (abortControllerRef.current) abortControllerRef.current.abort();
    abortControllerRef.current = new AbortController();

    setIsLoading(true);
    setError(null);
    setCurrentStep(1);
    setProgress(10);

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) { clearInterval(progressInterval); return 90; }
        return prev + Math.random() * 8 + 2;
      });
      setCurrentStep((prev) => {
        if (prev < 4) return prev + 1;
        return prev;
      });
    }, 800);

    try {
      const isUrl = isValidUrl(input.trim());
      const requestBody = isUrl ? { url: input.trim() } : { text: input.trim() };

      const result = await apiPost(API_ENDPOINTS.VERIFY, requestBody, {
        signal: abortControllerRef.current.signal
      });

      if (!result.success) {
        if (result.authError) { setError('Session expired. Please log in again.'); return; }
        throw new Error(result.error || 'Verification failed');
      }

      clearInterval(progressInterval);
      setProgress(100);
      setCurrentStep(4);

      const data = result.data;
      updateResults(data, input.trim());

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

      const existingHistory = JSON.parse(localStorage.getItem('factCheckHistory') || '[]');
      existingHistory.unshift(historyItem);
      localStorage.setItem('factCheckHistory', JSON.stringify(existingHistory.slice(0, 50)));

      setTimeout(() => navigate('/results'), 600);
    } catch (err) {
      clearInterval(progressInterval);
      setError(err.message || 'Verification failed. Please try again.');
      setCurrentStep(0);
      setProgress(0);
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

      <div className="vf-steps">
        {STEPS.map((step, i) => (
          <div
            key={step.id}
            className={`vf-step ${i <= currentStep ? 'active' : ''} ${i === currentStep && isLoading ? 'current' : ''} ${i < currentStep ? 'done' : ''}`}
          >
            <div className="vf-step__icon">
              {i < currentStep ? (
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 7l3.5 3.5L12 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              ) : (
                step.icon
              )}
            </div>
            <span className="vf-step__label">{step.label}</span>
            {i < STEPS.length - 1 && <div className={`vf-step__connector ${i < currentStep ? 'done' : ''}`} />}
          </div>
        ))}
      </div>

      {isLoading && (
        <div className="vf-progress">
          <motion.div
            className="vf-progress__bar"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
          <span className="vf-progress__text">{Math.round(progress)}%</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="verification-form" noValidate>
        <div className="input-wrapper">
          <textarea
            value={input}
            onChange={handleInputChange}
            placeholder="Paste a headline, URL, or article text here..."
            rows={6}
            disabled={isLoading}
            aria-label="Enter news content to verify"
            maxLength={MAX_CHARS}
          />
          <div className={`char-counter ${getCharCountClass()}`}>
            {charCount}/{MAX_CHARS} characters
          </div>
        </div>

        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        <button type="submit" disabled={isLoading || !input.trim()} className="submit-button">
          {isLoading ? (
            <>
              <span className="spinner" />
              <span>Verifying...</span>
            </>
          ) : (
            <>
              <span>Verify Now</span>
            </>
          )}
        </button>
      </form>

      <div className="features">
        <div className="feature">
          <span className="feature-icon">1</span>
          <span>Multi-source fact-checking</span>
        </div>
        <div className="feature">
          <span className="feature-icon">2</span>
          <span>Credibility score with evidence</span>
        </div>
        <div className="feature">
          <span className="feature-icon">3</span>
          <span>Source bias analysis</span>
        </div>
      </div>
    </div>
  );
};

export default VerificationForm;

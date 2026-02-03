import React, { useEffect, useState, useRef } from 'react';
import './ScoreDisplay.css';

const ScoreDisplay = () => {
  const [result, setResult] = useState(null);
  const [animatedScore, setAnimatedScore] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    // Use sessionStorage instead of localStorage to reduce persistent exposure
    const storedResult = sessionStorage.getItem('factCheckResult');
    if (storedResult) {
      try {
        const parsed = JSON.parse(storedResult);
        setResult(parsed);
      } catch (err) {
        // If parsing fails, remove corrupted entry
        sessionStorage.removeItem('factCheckResult');
      }
    }
  }, []);

  // Intersection Observer for animation trigger
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.2 }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  // Animate score counting
  useEffect(() => {
    if (!result || !isVisible) return;

    const targetScore = Math.round(result.score * 100);
    const duration = 1500;
    const steps = 60;
    const increment = targetScore / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= targetScore) {
        setAnimatedScore(targetScore);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.round(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [result, isVisible]);

  if (!result) {
    return (
      <div className="score-display loading" role="status" aria-live="polite">
        <div className="loading-spinner-large" aria-hidden="true"></div>
        <p className="loading-text">Loading your results...</p>
      </div>
    );
  }

  const { score, confidence, factors = {} } = result;
  const scorePercentage = Math.round(score * 100);

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
  };

  const getScoreLabel = (score) => {
    if (score >= 0.8) return 'Highly Credible';
    if (score >= 0.6) return 'Moderately Credible';
    if (score >= 0.4) return 'Low Credibility';
    return 'Not Credible';
  };

  const scoreClass = getScoreColor(score);
  const scoreLabel = getScoreLabel(score);

  return (
    <div 
      ref={containerRef}
      className="score-display"
      role="region"
      aria-label="Credibility Score"
    >
      <h2>FACTLY Score™</h2>
      
      <div 
        className={`score-circle ${scoreClass}`}
        role="img"
        aria-label={`Credibility score: ${scorePercentage}%, ${scoreLabel}`}
      >
        <div className="score-number" aria-hidden="true">
          {animatedScore}%
        </div>
        <div className="score-label">{scoreLabel}</div>
      </div>

      <div className="confidence-section">
        <div className="confidence-label">
          <span>Confidence Level</span>
          <span className="confidence-value">{Math.round(confidence * 100)}%</span>
        </div>
        <div className="confidence-bar" role="progressbar" aria-valuenow={Math.round(confidence * 100)} aria-valuemin="0" aria-valuemax="100">
          <div 
            className="confidence-fill" 
            style={{ width: isVisible ? `${confidence * 100}%` : '0%' }}
            aria-hidden="true"
          ></div>
        </div>
      </div>

      {factors && Object.keys(factors).length > 0 && (
        <div className="score-breakdown">
          <h3>Score Breakdown</h3>
          {Object.entries(factors).map(([key, value]) => (
            <div key={key} className="breakdown-item">
              <span className="breakdown-label">
                {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
              </span>
              <span className="breakdown-value">{Math.round(value * 100)}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ScoreDisplay;

import React, { useEffect, useState, useRef } from 'react';
import './CredibilityChart.css';

const CredibilityChart = () => {
  const [result, setResult] = useState(null);
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const storedResult = localStorage.getItem('factCheckResult');
    if (storedResult) {
      setResult(JSON.parse(storedResult));
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

  if (!result) {
    return (
      <div className="credibility-chart" role="region" aria-label="Credibility Analysis">
        <h3>Credibility Breakdown</h3>
        <div className="chart-placeholder">
          <div className="chart-placeholder-icon" aria-hidden="true">📊</div>
          <div className="placeholder-bar" style={{ width: '0%' }}></div>
          <p>Submit a query to see credibility analysis.</p>
        </div>
      </div>
    );
  }

  const { score, confidence, factors = {}, components = [] } = result;

  // Map backend component data to chart display
  const componentMap = {};
  components.forEach(comp => {
    componentMap[comp.name.toLowerCase().replace(/\s+/g, '')] = comp;
  });

  const chartData = [
    { 
      label: 'Source Reliability', 
      value: componentMap['sourcecredibility'] ? componentMap['sourcecredibility'].score : (factors.sourceReliability || score * 0.9), 
      className: 'source-reliability',
      icon: '📚'
    },
    { 
      label: 'Content Consistency', 
      value: componentMap['contentanalysis'] ? componentMap['contentanalysis'].score : (factors.contentConsistency || score * 0.85), 
      className: 'content-consistency',
      icon: '✓'
    },
    { 
      label: 'Fact-Check Coverage', 
      value: componentMap['factcheckconsensus'] ? componentMap['factcheckconsensus'].score : (factors.factCheckCoverage || confidence), 
      className: 'fact-check-coverage',
      icon: '🔍'
    },
    { 
      label: 'Evidence Quality', 
      value: componentMap['evidencequality'] ? componentMap['evidencequality'].score : (factors.evidenceQuality || score * 0.8), 
      className: 'evidence-quality',
      icon: '📋'
    },
  ];

  return (
    <div 
      ref={containerRef}
      className="credibility-chart"
      role="region"
      aria-label="Credibility Analysis"
    >
      <h3>Credibility Breakdown</h3>
      
      <div className="chart-container">
        {chartData.map((item, index) => (
          <div key={index} className="chart-item">
            <div className="chart-label">
              <span className="chart-label-text">
                <span className="chart-label-icon" aria-hidden="true">{item.icon}</span>
                {item.label}
              </span>
            </div>
            <div className="chart-bar-container">
              <div className="chart-bar-wrapper">
                <div 
                  className={`chart-bar ${item.className}`}
                  style={{ 
                    width: isVisible ? `${Math.round(item.value * 100)}%` : '0%'
                  }}
                  role="progressbar"
                  aria-valuenow={Math.round(item.value * 100)}
                  aria-valuemin="0"
                  aria-valuemax="100"
                  aria-label={`${item.label}: ${Math.round(item.value * 100)}%`}
                ></div>
              </div>
              <span className="chart-value" aria-hidden="true">
                {Math.round(item.value * 100)}%
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="chart-summary">
        <div className="summary-item score">
          <span className="summary-label">Overall Score</span>
          <span className="summary-value">{Math.round(score * 100)}%</span>
        </div>
        <div className="summary-item confidence">
          <span className="summary-label">Confidence</span>
          <span className="summary-value">{Math.round(confidence * 100)}%</span>
        </div>
      </div>

      {factors && Object.keys(factors).length > 0 && (
        <div className="factor-details">
          <h4>Detailed Factors</h4>
          {Object.entries(factors).map(([key, value]) => (
            <div key={key} className="factor-item">
              <span className="factor-name">
                {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
              </span>
              <span className="factor-score">{Math.round(value * 100)}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CredibilityChart;

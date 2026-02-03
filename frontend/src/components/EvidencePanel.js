import React, { useEffect, useState } from 'react';
import './EvidencePanel.css';

const EvidencePanel = () => {
  const [result, setResult] = useState(null);
  const [expandedClaims, setExpandedClaims] = useState({});

  useEffect(() => {
    const storedResult = localStorage.getItem('factCheckResult');
    if (storedResult) {
      setResult(JSON.parse(storedResult));
    }
  }, []);

  const toggleClaim = (index) => {
    setExpandedClaims(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  const getRatingClass = (rating) => {
    if (!rating) return 'unverified';
    const normalized = rating.toLowerCase().replace(/\s+/g, '-');
    if (['true', 'correct', 'verified'].includes(normalized)) return 'true';
    if (['false', 'incorrect', 'fake'].includes(normalized)) return 'false';
    if (['mixed', 'partially-true', 'misleading'].includes(normalized)) return 'mixed';
    return 'unverified';
  };

  const getRatingIcon = (rating) => {
    const ratingClass = getRatingClass(rating);
    switch (ratingClass) {
      case 'true': return '✓';
      case 'false': return '✕';
      case 'mixed': return '~';
      default: return '?';
    }
  };

  if (!result) {
    return (
      <div className="evidence-panel" role="region" aria-label="Evidence and Sources">
        <h3>Evidence & Sources</h3>
        <div className="placeholder-state">
          <div className="placeholder-icon" aria-hidden="true">📚</div>
          <p>Submit a query to see evidence and sources.</p>
        </div>
      </div>
    );
  }

  const { sources = [], claims = [], query } = result;

  return (
    <div className="evidence-panel" role="region" aria-label="Evidence and Sources">
      <h3>Evidence & Sources</h3>
      
      {query && (
        <div className="query-preview" role="note">
          <strong>Query:</strong> {query.length > 100 ? `${query.substring(0, 100)}...` : query}
        </div>
      )}
      
      {claims.length > 0 && (
        <div className="claims-section">
          <h4>Fact-Check Claims</h4>
          {claims.map((claim, index) => (
            <div 
              key={index} 
              className="claim-item"
              role="article"
              aria-label={`Claim ${index + 1}: ${claim.rating || 'Unverified'}`}
            >
              <p className="claim-text">{claim.text}</p>
              <div className="claim-meta">
                <span 
                  className={`claim-rating ${getRatingClass(claim.rating)}`}
                  aria-label={`Rating: ${claim.rating || 'Unverified'}`}
                >
                  <span aria-hidden="true">{getRatingIcon(claim.rating)}</span>
                  {claim.rating || 'Unverified'}
                </span>
                {claim.source && (
                  <a 
                    href={claim.source} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="claim-source"
                    aria-label={`View source for claim ${index + 1} (opens in new tab)`}
                  >
                    View Source
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {sources.length > 0 && (
        <div className="sources-section">
          <h4>Sources</h4>
          <ul className="sources-list" role="list">
            {sources.map((source, index) => (
              <li 
                key={index} 
                className="source-item"
                role="listitem"
              >
                <a 
                  href={source.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  aria-label={`${source.name || 'Source'} (opens in new tab)`}
                >
                  {source.name || source.url}
                </a>
                {source.credibility && (
                  <span 
                    className={`source-credibility ${source.credibility.toLowerCase()}`}
                    aria-label={`Credibility: ${source.credibility}`}
                  >
                    {source.credibility}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {claims.length === 0 && sources.length === 0 && (
        <p className="no-evidence" role="status">
          No specific evidence found for this query.
        </p>
      )}
    </div>
  );
};

export default EvidencePanel;

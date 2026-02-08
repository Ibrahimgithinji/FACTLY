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
    if (['true', 'correct', 'verified', 'mostly-true'].includes(normalized)) return 'true';
    if (['false', 'incorrect', 'fake', 'mostly-false'].includes(normalized)) return 'false';
    if (['mixed', 'partially-true', 'misleading', 'half-true'].includes(normalized)) return 'mixed';
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

  const formatExactDate = (dateStr) => {
    if (!dateStr) return 'Date not available';
    try {
      const date = new Date(dateStr);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZoneName: 'short'
      });
    } catch {
      return dateStr;
    }
  };

  const formatConfidence = (score) => {
    if (score === undefined || score === null) return 'N/A';
    return `${(score * 100).toFixed(1)}%`;
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

  // Use new evidence structure if available, fallback to legacy structure
  const evidence = result.evidence || [];
  const sources = result.sources || result.sources || [];
  const legacyClaims = result.claims || [];
  const legacySources = result.sources || [];
  
  // Combine legacy and new structures
  const displayClaims = evidence.length > 0 
    ? evidence.filter(e => e.type === 'fact_check' || e.rating)
    : legacyClaims;
  const displaySources = evidence.length > 0 
    ? evidence.filter(e => e.type === 'news')
    : legacySources;

  return (
    <div className="evidence-panel" role="region" aria-label="Evidence and Sources">
      <h3>Evidence & Sources</h3>
      
      {result.query && (
        <div className="query-preview" role="note">
          <strong>Query:</strong> {result.query}
        </div>
      )}
      
      {displayClaims.length > 0 && (
        <div className="claims-section">
          <h4>Fact-Check Evidence</h4>
          {displayClaims.map((claim, index) => (
            <div 
              key={index} 
              className="claim-item"
              role="article"
              aria-label={`Evidence ${index + 1}: ${claim.rating || claim.verdict || 'Unverified'}`}
            >
              <div className="claim-header" onClick={() => toggleClaim(index)}>
                <span 
                  className={`claim-rating ${getRatingClass(claim.rating || claim.verdict)}`}
                  aria-label={`Rating: ${claim.rating || claim.verdict || 'Unverified'}`}
                >
                  <span aria-hidden="true">{getRatingIcon(claim.rating || claim.verdict)}</span>
                  {claim.rating || claim.verdict || 'Unverified'}
                </span>
                <span className="expand-icon" aria-hidden="true">
                  {expandedClaims[index] ? '▼' : '▶'}
                </span>
              </div>
              
              {(expandedClaims[index] || claim.full_text) && (
                <div className="claim-content">
                  <p className="claim-text">
                    <strong>Claim:</strong> {claim.full_text || claim.text || claim.claim}
                  </p>
                  
                  {/* Exact Confidence Score */}
                  <div className="exact-metadata">
                    <span className="metadata-label">Confidence Score:</span>
                    <span className="metadata-value exact-score">
                      {formatConfidence(claim.confidence_score)}
                    </span>
                  </div>
                  
                  {/* Exact Source Citation */}
                  {claim.source && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Source:</span>
                      <span className="metadata-value">{claim.source}</span>
                    </div>
                  )}
                  
                  {/* Exact Source Credibility */}
                  {claim.source_credibility !== undefined && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Source Credibility:</span>
                      <span className="metadata-value exact-score">
                        {formatConfidence(claim.source_credibility)}
                      </span>
                    </div>
                  )}
                  
                  {/* Exact Publication Date */}
                  {claim.exact_date && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Publication Date:</span>
                      <span className="metadata-value">{formatExactDate(claim.exact_date)}</span>
                    </div>
                  )}
                  
                  {/* Exact URL */}
                  {claim.url && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Source URL:</span>
                      <a 
                        href={claim.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="claim-source"
                        aria-label={`View source (opens in new tab)`}
                      >
                        {claim.url}
                      </a>
                    </div>
                  )}
                  
                  {/* Full Text Toggle */}
                  {claim.full_text && claim.text !== claim.full_text && (
                    <button 
                      className="view-full-text"
                      onClick={() => toggleClaim(index)}
                    >
                      {expandedClaims[index] ? 'Show Less' : 'View Full Text'}
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {displaySources.length > 0 && (
        <div className="sources-section">
          <h4>Related News Sources</h4>
          <ul className="sources-list">
            {displaySources.map((source, index) => (
              <li 
                key={index} 
                className="source-item"
              >
                <div className="source-header">
                  <a 
                    href={source.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    aria-label={`${source.name || 'Source'} (opens in new tab)`}
                  >
                    {source.name || source.source || 'Unknown Source'}
                  </a>
                  <span className="source-type-badge">{source.type || 'news'}</span>
                </div>
                
                <div className="source-details">
                  {/* Exact Relevance Score */}
                  {source.confidence_score !== undefined && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Relevance Score:</span>
                      <span className="metadata-value exact-score">
                        {formatConfidence(source.confidence_score)}
                      </span>
                    </div>
                  )}
                  
                  {/* Exact Source Credibility */}
                  {source.source_credibility !== undefined && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Source Credibility:</span>
                      <span className="metadata-value exact-score">
                        {formatConfidence(source.source_credibility)}
                      </span>
                    </div>
                  )}
                  
                  {/* Exact Publication Date */}
                  {source.exact_date && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Published:</span>
                      <span className="metadata-value">{formatExactDate(source.exact_date)}</span>
                    </div>
                  )}
                  
                  {/* Sentiment */}
                  {source.rating && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Sentiment:</span>
                      <span className={`sentiment-badge ${source.rating}`}>
                        {source.rating}
                      </span>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Sources List (from new structure) */}
      {sources.length > 0 && (
        <div className="sources-section">
          <h4>Source Credibility Assessment</h4>
          <ul className="sources-list">
            {sources.map((source, index) => (
              <li 
                key={index} 
                className="source-item credibility-item"
              >
                <div className="source-header">
                  <a 
                    href={source.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    aria-label={`${source.name} (opens in new tab)`}
                  >
                    {source.name}
                  </a>
                </div>
                
                <div className="source-details">
                  {/* Exact Credibility Score */}
                  {source.exact_credibility_score !== undefined && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Credibility Score:</span>
                      <span className="metadata-value exact-score">
                        {formatConfidence(source.exact_credibility_score)}
                      </span>
                    </div>
                  )}
                  
                  {/* Review Count */}
                  {source.review_count !== undefined && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Review Count:</span>
                      <span className="metadata-value">{source.review_count}</span>
                    </div>
                  )}
                  
                  {/* Categories */}
                  {source.categories && source.categories.length > 0 && (
                    <div className="exact-metadata">
                      <span className="metadata-label">Categories:</span>
                      <span className="metadata-value">
                        {source.categories.join(', ')}
                      </span>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {displayClaims.length === 0 && displaySources.length === 0 && sources.length === 0 && (
        <p className="no-evidence" role="status">
          No specific evidence found for this query.
        </p>
      )}
      
      {/* Enhanced Verification Results */}
      {result.verification_summary && (
        <div className="enhanced-verification-section">
          <h4>Enhanced Verification Summary</h4>
          
          {/* Overall Assessment */}
          {result.verification_summary.overall_assessment && (
            <div className="verification-assessment">
              <p>{result.verification_summary.overall_assessment}</p>
            </div>
          )}
          
          {/* Verified Data Points */}
          {result.verification_summary.verified_data_points && result.verification_summary.verified_data_points.length > 0 && (
            <div className="data-points-section verified">
              <h5>✓ Verified Data Points</h5>
              <ul>
                {result.verification_summary.verified_data_points.map((point, idx) => (
                  <li key={idx}>{point}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Unverified Data Points */}
          {result.verification_summary.unverified_data_points && result.verification_summary.unverified_data_points.length > 0 && (
            <div className="data-points-section unverified">
              <h5>⚠ Unverified Data Points</h5>
              <ul>
                {result.verification_summary.unverified_data_points.map((point, idx) => (
                  <li key={idx}>{point}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Discrepancies */}
          {result.verification_summary.discrepancies_and_caveats && result.verification_summary.discrepancies_and_caveats.length > 0 && (
            <div className="discrepancies-section">
              <h5>⚠ Discrepancies & Caveats</h5>
              <ul>
                {result.verification_summary.discrepancies_and_caveats.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Source Diversity Assessment */}
          {result.verification_summary.source_diversity_assessment && (
            <div className="source-diversity-section">
              <h5>📊 Source Diversity</h5>
              <p>{result.verification_summary.source_diversity_assessment}</p>
            </div>
          )}
          
          {/* Recommendations */}
          {result.verification_summary.recommendations && result.verification_summary.recommendations.length > 0 && (
            <div className="recommendations-section">
              <h5>💡 Recommendations</h5>
              <ul>
                {result.verification_summary.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Verification Limitations */}
          {result.verification_summary.verification_limitations && result.verification_summary.verification_limitations.length > 0 && (
            <div className="limitations-section">
              <h5>⚠ Verification Limitations</h5>
              <ul>
                {result.verification_summary.verification_limitations.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      {/* Verification Trace */}
      {result.verification_trace && (
        <div className="verification-trace-section">
          <h4>Verification Process Trace</h4>
          
          {/* Confidence Level */}
          {result.verification_trace.confidence_level && (
            <div className="trace-meta">
              <span className="meta-label">Confidence Level:</span>
              <span className={`confidence-badge ${result.verification_trace.confidence_level.toLowerCase()}`}>
                {result.verification_trace.confidence_level}
              </span>
            </div>
          )}
          
          {/* Recommended Verdict */}
          {result.verification_trace.recommended_verdict && (
            <div className="trace-meta">
              <span className="meta-label">Recommended Verdict:</span>
              <span className="verdict-badge">{result.verification_trace.recommended_verdict}</span>
            </div>
          )}
          
          {/* Verification Steps */}
          {result.verification_trace.verification_steps && result.verification_trace.verification_steps.length > 0 && (
            <div className="trace-steps">
              <h5>Verification Steps</h5>
              <ol>
                {result.verification_trace.verification_steps.map((step, idx) => (
                  <li key={idx} className={`step-item ${step.status}`}>
                    <span className="step-name">{step.step_name}</span>
                    <span className="step-status">{step.status}</span>
                    {step.duration_ms > 0 && (
                      <span className="step-duration">{step.duration_ms.toFixed(0)}ms</span>
                    )}
                  </li>
                ))}
              </ol>
            </div>
          )}
          
          {/* Processing Time */}
          {result.verification_trace.processing_time_ms > 0 && (
            <div className="trace-meta">
              <span className="meta-label">Processing Time:</span>
              <span className="processing-time">{result.verification_trace.processing_time_ms.toFixed(0)}ms</span>
            </div>
          )}
        </div>
      )}
      
      {/* Direct Verification Details */}
      {result.direct_verification && (
        <div className="direct-verification-section">
          <h4>Direct Source Verification</h4>
          
          <div className="verification-stats">
            <div className="stat-item">
              <span className="stat-value">{result.direct_verification.sources_consulted}</span>
              <span className="stat-label">Sources Consulted</span>
            </div>
            <div className="stat-item primary">
              <span className="stat-value">{result.direct_verification.primary_sources_found}</span>
              <span className="stat-label">Primary Sources</span>
            </div>
            <div className="stat-item secondary">
              <span className="stat-value">{result.direct_verification.secondary_sources_found}</span>
              <span className="stat-label">Secondary Sources</span>
            </div>
            <div className="stat-item score">
              <span className="stat-value">{(result.direct_verification.overall_verification_score * 100).toFixed(0)}%</span>
              <span className="stat-label">Verification Score</span>
            </div>
          </div>
          
          {/* Sources Consulted Details */}
          {result.verification_summary?.sources_consulted && result.verification_summary.sources_consulted.length > 0 && (
            <div className="sources-detail">
              <h5>Authoritative Sources</h5>
              <ul>
                {result.verification_summary.sources_consulted.map((source, idx) => (
                  <li key={idx} className="source-detail-item">
                    <span className="source-name">{source.name}</span>
                    <span className="source-type">{source.type}</span>
                    <span className="source-credibility">Credibility: {source.credibility}</span>
                    <span className="source-verified">{source.verified}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      {/* Cross-Source Analysis */}
      {result.cross_source_analysis && (
        <div className="cross-source-section">
          <h4>Cross-Source Analysis</h4>
          
          <div className="analysis-metrics">
            {result.cross_source_analysis.consensus_level && (
              <div className="metric-item">
                <span className="metric-label">Consensus:</span>
                <span className={`metric-value ${result.cross_source_analysis.consensus_level}`}>
                  {result.cross_source_analysis.consensus_level.replace(/_/g, ' ')}
                </span>
              </div>
            )}
            
            {result.cross_source_analysis.evidence_strength && (
              <div className="metric-item">
                <span className="metric-label">Evidence Strength:</span>
                <span className={`metric-value ${result.cross_source_analysis.evidence_strength}`}>
                  {result.cross_source_analysis.evidence_strength.replace(/_/g, ' ')}
                </span>
              </div>
            )}
            
            {result.cross_source_analysis.agreement_score > 0 && (
              <div className="metric-item">
                <span className="metric-label">Agreement Score:</span>
                <span className="metric-value">{(result.cross_source_analysis.agreement_score * 100).toFixed(0)}%</span>
              </div>
            )}
            
            {result.cross_source_analysis.confidence_score > 0 && (
              <div className="metric-item">
                <span className="metric-label">Confidence Score:</span>
                <span className="metric-value">{(result.cross_source_analysis.confidence_score * 100).toFixed(0)}%</span>
              </div>
            )}
          </div>
          
          {/* Key Findings */}
          {result.cross_source_analysis.key_findings && result.cross_source_analysis.key_findings.length > 0 && (
            <div className="key-findings">
              <h5>Key Findings</h5>
              <ul>
                {result.cross_source_analysis.key_findings.map((finding, idx) => (
                  <li key={idx}>{finding}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Contradictions */}
          {result.cross_source_analysis.contradictions && result.cross_source_analysis.contradictions.length > 0 && (
            <div className="contradictions">
              <h5>⚠ Contradictions Found</h5>
              <ul>
                {result.cross_source_analysis.contradictions.map((contradiction, idx) => (
                  <li key={idx}>
                    {contradiction.source1} vs {contradiction.source2}: {contradiction.details}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Uncertainty Factors */}
          {result.cross_source_analysis.uncertainty_factors && result.cross_source_analysis.uncertainty_factors.length > 0 && (
            <div className="uncertainty-factors">
              <h5>⚠ Uncertainty Factors</h5>
              <ul>
                {result.cross_source_analysis.uncertainty_factors.map((factor, idx) => (
                  <li key={idx}>{factor}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EvidencePanel;

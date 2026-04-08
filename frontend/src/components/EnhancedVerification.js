import React, { useMemo } from 'react';
import { useResults } from '../context/ResultsContext';
import './EnhancedVerification.css';

const EnhancedVerification = () => {
  const { results, loading } = useResults();

  const analysis = useMemo(() => {
    if (!results || !results.enhanced_analysis) return null;
    return results.enhanced_analysis;
  }, [results]);

  if (loading || !results || !analysis) {
    return (
      <div className="enhanced-verification">
        <h3>Verification Analysis</h3>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Analyzing evidence...</p>
        </div>
      </div>
    );
  }

  const getVerdictColor = (verdict) => {
    if (['true', 'correct', 'verified', 'mostly-true'].includes(verdict)) return 'positive';
    if (['false', 'incorrect', 'fake', 'mostly-false'].includes(verdict)) return 'negative';
    if (['mixed', 'partially-true', 'misleading', 'half-true'].includes(verdict)) return 'mixed';
    return 'unknown';
  };

  const formatAge = (hours) => {
    if (hours === Infinity || !isFinite(hours)) return 'Date not available';
    if (hours < 1) return 'Less than 1 hour';
    if (hours < 24) return `${Math.round(hours)} hours`;
    if (hours < 168) return `${Math.round(hours / 24)} days`;
    return `${Math.round(hours / 168)} weeks`;
  };

  return (
    <div className="enhanced-verification">
      <h3>Advanced Verification Analysis</h3>

      <div className="analysis-grid">
        {/* Evidence Summary */}
        <div className="analysis-card summary">
          <h4>Evidence Summary</h4>
          <div className="metrics">
            <div className="metric">
              <span className="value">{analysis.evidence_summary.total_sources}</span>
              <span className="label">Total Sources</span>
            </div>
            <div className="metric">
              <span className="value">{analysis.evidence_summary.fact_checks}</span>
              <span className="label">Fact Checks</span>
            </div>
            <div className="metric">
              <span className="value">{analysis.evidence_summary.news_sources}</span>
              <span className="label">News Sources</span>
            </div>
          </div>
        </div>

        {/* Verdict Consensus */}
        <div className="analysis-card consensus">
          <h4>Verdict Consensus</h4>
          <div className={`consensus-result ${getVerdictColor(analysis.verdict_consensus.consensus_verdict)}`}>
            <div className="verdict-main">
              <span className="verdict-label">
                {analysis.verdict_consensus.consensus_verdict.toUpperCase()}
              </span>
              <span className="verdict-percentage">
                {analysis.verdict_consensus.consensus_percentage}% consensus
              </span>
            </div>
            {analysis.verdict_consensus.has_conflicts && (
              <div className="conflict-warning">
                ⚠️ Conflicting evidence detected
              </div>
            )}
          </div>
        </div>

        {/* Source Credibility */}
        <div className="analysis-card credibility">
          <h4>Source Credibility</h4>
          <div className="credibility-score">
            <div className="credibility-gauge">
              <div
                className="credibility-fill"
                style={{ width: `${analysis.source_credibility.average_score * 100}%` }}
              ></div>
            </div>
            <div className="credibility-info">
              <span className="credibility-value">
                {analysis.source_credibility.credibility_level}
              </span>
              <span className="credibility-percent">
                {(analysis.source_credibility.average_score * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>

        {/* Data Freshness */}
        <div className="analysis-card freshness">
          <h4>Data Freshness</h4>
          <div className={`freshness-indicator ${analysis.evidence_freshness.is_fresh ? 'fresh' : analysis.evidence_freshness.is_stale ? 'stale' : 'moderate'}`}>
            <div className="freshness-icon">
              {analysis.evidence_freshness.is_fresh ? '🟢' : analysis.evidence_freshness.is_stale ? '🔴' : '🟡'}
            </div>
            <div className="freshness-info">
              <span className="freshness-age">
                Avg: {formatAge(analysis.evidence_freshness.average_age_hours)}
              </span>
              <span className="freshness-status">
                {analysis.evidence_freshness.freshness_level}
              </span>
            </div>
          </div>
        </div>

        {/* Cross-Verification */}
        <div className="analysis-card cross-verification">
          <h4>Cross-Verification</h4>
          <div className="cross-verification-score">
            <div className="verification-gauge">
              <div
                className="verification-fill"
                style={{ width: `${analysis.cross_verification.cross_verification_score * 100}%` }}
              ></div>
            </div>
            <div className="verification-info">
              <span className="verification-sources">
                {analysis.cross_verification.unique_sources} unique sources
              </span>
              <span className="verification-strength">
                {analysis.cross_verification.verification_strength}
              </span>
            </div>
          </div>
        </div>

        {/* Methodology Note */}
        <div className="analysis-card methodology">
          <h4>Verification Methodology</h4>
          <div className="methodology-content">
            <p>
              This analysis combines multiple fact-checking sources, evaluates source credibility,
              assesses data freshness, and checks for cross-verification consistency.
            </p>
            <div className="methodology-factors">
              <span className="factor">✓ Multi-source verification</span>
              <span className="factor">✓ Source credibility assessment</span>
              <span className="factor">✓ Evidence freshness analysis</span>
              <span className="factor">✓ Consensus evaluation</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedVerification;
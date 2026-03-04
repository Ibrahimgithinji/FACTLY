/**
 * Real-Time Verification Display Component
 * 
 * Displays verification results with:
 * - Real-time global consensus
 * - Information freshness indicators
 * - Global source attribution
 * - Trending analysis
 * - Verification timeline
 */

import React, { useState, useCallback } from 'react';
import './RealTimeVerification.css';

const RealTimeVerification = ({ verificationData }) => {
  const [expandedSources, setExpandedSources] = useState(false);
  const [expandedTimeline, setExpandedTimeline] = useState(false);

  if (!verificationData) {
    return <div className="realtime-verification">No verification data available</div>;
  }

  const {
    verified,
    confidence_score,
    freshness,
    global_consensus,
    trending_score,
    sources_found,
    primary_sources,
    conflicting_information,
    supporting_information,
    verification_timeline
  } = verificationData;

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return '#10b981';  // Green
    if (score >= 0.5) return '#f59e0b';  // Amber
    return '#ef4444';                     // Red
  };

  const getFreshnessLabel = () => {
    const labels = {
      'breaking': '🔴 Breaking',
      'recent': '🟠 Recent',
      'current': '🟡 Current',
      'established': '🟢 Established'
    };
    return labels[freshness] || freshness;
  };

  const getConsensusIcon = () => {
    const icons = {
      'verified': '✅ Verified',
      'disputed': '⚠️ Disputed',
      'unverified': '❓ Unverified',
      'evolving': '🔄 Evolving'
    };
    return icons[global_consensus] || global_consensus;
  };

  return (
    <div className="realtime-verification">
      {/* Header with consensus badge */}
      <div className="verification-header">
        <div className="consensus-badge">
          <span className="consensus-text">{getConsensusIcon()}</span>
          <span className="consensus-label">{global_consensus.toUpperCase()}</span>
        </div>

        <div className="confidence-meter">
          <div className="confidence-label">Confidence Score</div>
          <div className="confidence-bar-container">
            <div
              className="confidence-bar-fill"
              style={{
                width: `${confidence_score * 100}%`,
                backgroundColor: getConfidenceColor(confidence_score)
              }}
            />
          </div>
          <span className="confidence-value">{(confidence_score * 100).toFixed(0)}%</span>
        </div>

        <div className="freshness-badge">
          <span className="freshness-label">{getFreshnessLabel()}</span>
        </div>
      </div>

      {/* Key Stats */}
      <div className="verification-stats">
        <div className="stat-item">
          <div className="stat-icon">🌍</div>
          <div className="stat-content">
            <div className="stat-label">Global Sources</div>
            <div className="stat-value">{sources_found} sources</div>
          </div>
        </div>

        <div className="stat-item">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-label">Trending Score</div>
            <div className="stat-value">{(trending_score * 100).toFixed(0)}%</div>
          </div>
        </div>

        <div className="stat-item">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">Supporting</div>
            <div className="stat-value">{supporting_information.length} sources</div>
          </div>
        </div>

        <div className="stat-item">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <div className="stat-label">Conflicting</div>
            <div className="stat-value">{conflicting_information.length} sources</div>
          </div>
        </div>
      </div>

      {/* Primary Sources */}
      <div className="sources-section">
        <div
          className="section-header"
          onClick={() => setExpandedSources(!expandedSources)}
        >
          <span className="header-title">📰 Primary Sources ({primary_sources.length})</span>
          <span className="expand-icon">
            {expandedSources ? '▼' : '▶'}
          </span>
        </div>

        {expandedSources && (
          <div className="sources-list">
            {primary_sources.map((source, idx) => (
              <div key={idx} className="source-item primary">
                <div className="source-header">
                  <span className="source-name">{source.source}</span>
                  <span className="source-credibility">
                    Credibility: {(source.credibility * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="source-info">
                  {new Date(source.timestamp).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Supporting Information */}
      {supporting_information.length > 0 && (
        <div className="info-section supporting">
          <div className="section-label">✅ Supporting Information</div>
          <div className="info-list">
            {supporting_information.map((item, idx) => (
              <div key={idx} className="info-item">
                <span className="info-source">{item.source}</span>
                <p className="info-text">{item.info?.substring(0, 150)}...</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conflicting Information */}
      {conflicting_information.length > 0 && (
        <div className="info-section conflicting">
          <div className="section-label">⚠️ Conflicting Information</div>
          <div className="info-list">
            {conflicting_information.map((item, idx) => (
              <div key={idx} className="info-item conflicting-item">
                <span className="info-source">{item.source}</span>
                <p className="info-text">{item.info?.substring(0, 150)}...</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Verification Timeline */}
      {verification_timeline && verification_timeline.length > 0 && (
        <div className="timeline-section">
          <div
            className="section-header"
            onClick={() => setExpandedTimeline(!expandedTimeline)}
          >
            <span className="header-title">📅 Verification Timeline</span>
            <span className="expand-icon">
              {expandedTimeline ? '▼' : '▶'}
            </span>
          </div>

          {expandedTimeline && (
            <div className="timeline">
              {verification_timeline.map((event, idx) => (
                <div key={idx} className="timeline-item">
                  <div className="timeline-time">
                    {new Date(event.timestamp).toLocaleString()}
                  </div>
                  <div className="timeline-sources">
                    {event.sources.map((source, sidx) => (
                      <span key={sidx} className={`timeline-source ${source.status}`}>
                        {source.source}: {source.status}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Methodology Note */}
      <div className="methodology-note">
        <span className="info-icon">ℹ️</span>
        <span className="note-text">
          This verification uses real-time global data from 30+ authoritative sources
          including Reuters, AP, BBC, academic databases (PubMed, arXiv), and
          official organizations (UN, WHO, World Bank).
        </span>
      </div>
    </div>
  );
};

export default RealTimeVerification;

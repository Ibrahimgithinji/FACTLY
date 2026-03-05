/**
 * TrendingTopics Component
 * 
 * Enhanced dashboard for AI-Powered Trend Discovery and Misinformation Detection
 * Displays trending topics with virality scores, risk levels, and verification status
 * 
 * Features:
 * - Topic name, source platforms, virality score with visual indicators
 * - Misinformation risk level with color-coded badges
 * - Fact-check status
 * - Timestamp and predicted spread timeline
 * - Filtering by region, risk level, and verification status
 */

// ============================================================================
// TypeScript Interfaces (documented for reference)
// ============================================================================

/**
 * @typedef {Object} Trend
 * @property {number} id - Unique identifier
 * @property {string} topic - Topic/claim text
 * @property {string[]} keywords - Extracted keywords
 * @property {string[]} source_platforms - Source platforms
 * @property {number} engagement_score - Virality score (0-100)
 * @property {number} engagement_velocity - Engagement per hour
 * @property {string} risk_level - Risk level (low, medium, high, critical)
 * @property {number} misinformation_risk_score - Risk score (0-100)
 * @property {string} verification_status - Verification status
 * @property {number} factly_score - FACTLY verification score
 * @property {string} primary_region - Primary region
 * @property {number} predicted_trend_score - Predicted trend score
 * @property {string} first_detected - First detection timestamp
 * @property {string} last_updated - Last update timestamp
 */

/**
 * @typedef {Object} RiskBadgeConfig
 * @property {string} label - Display label
 * @property {string} color - Background color
 * @property {string} textColor - Text color
 */

// ============================================================================
// Component Implementation
// ============================================================================

import React, { useState, useEffect, useCallback } from 'react';
import './TrendingTopics.css';

// SVG Icons
const TrendingIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
    <polyline points="17 6 23 6 23 12"></polyline>
  </svg>
);

const RefreshIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 4 23 10 17 10"></polyline>
    <polyline points="1 20 1 14 7 14"></polyline>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
  </svg>
);

const GlobeIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="2" y1="12" x2="22" y2="12"></line>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
  </svg>
);

const AlertIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
    <line x1="12" y1="9" x2="12" y2="13"></line>
    <line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>
);

const CheckIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
);

const WarningIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="12" y1="8" x2="12" y2="12"></line>
    <line x1="12" y1="16" x2="12.01" y2="16"></line>
  </svg>
);

// Risk badge configuration
const RISK_BADGES = {
  critical: { label: 'Critical', color: '#dc2626', textColor: '#fff' },
  high: { label: 'High Risk', color: '#ea580c', textColor: '#fff' },
  medium: { label: 'Medium', color: '#ca8a04', textColor: '#fff' },
  low: { label: 'Low Risk', color: '#16a34a', textColor: '#fff' },
};

// Verification status badges
const VERIFICATION_BADGES = {
  pending: { label: 'Pending', color: '#6b7280' },
  processing: { label: 'Processing', color: '#2563eb' },
  verified: { label: 'Verified True', color: '#16a34a' },
  false: { label: 'False Claim', color: '#dc2626' },
  true: { label: 'True', color: '#16a34a' },
  unverifiable: { label: 'Unverifiable', color: '#ca8a04' },
};

// Get API URL from environment
const getApiUrl = () => {
  const envUrl = process.env.REACT_APP_API_URL;
  const defaultUrls = ['http://localhost:8000', 'http://127.0.0.1:8000'];
  return envUrl || defaultUrls[0];
};

// Format relative time
const formatRelativeTime = (dateString) => {
  if (!dateString) return 'Unknown';
  
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
};

// Get engagement bar color
const getEngagementColor = (score) => {
  if (score >= 80) return '#16a34a'; // green
  if (score >= 60) return '#ca8a04'; // yellow
  if (score >= 40) return '#ea580c'; // orange
  return '#dc2626'; // red
};

// Region display names
const REGION_NAMES = {
  global: 'Global',
  africa: 'Africa',
  india: 'India',
  us: 'United States',
  europe: 'Europe',
  asia: 'Asia',
  latin_america: 'Latin America',
};

const TrendingTopics = ({ onTopicClick }) => {
  // State
  const [trends, setTrends] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [apiUrl] = useState(() => getApiUrl());
  
  // Filters
  const [regionFilter, setRegionFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Analytics
  const [analytics, setAnalytics] = useState(null);

  // Fetch trends from API
  const fetchTrends = useCallback(async (showRefreshing = false) => {
    if (showRefreshing) setIsRefreshing(true);
    else setIsLoading(true);
    setError(null);

    try {
      // Build query params
      const params = new URLSearchParams();
      if (regionFilter) params.append('region', regionFilter);
      if (riskFilter) params.append('risk_level', riskFilter);
      if (statusFilter) params.append('verification_status', statusFilter);
      params.append('limit', '50');

      const url = `${apiUrl}/api/trends/?${params.toString()}`;
      console.log('Fetching trends from:', url);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setTrends(data.results || []);
      
    } catch (err) {
      console.error('Error fetching trends:', err);
      setError(err.message || 'Failed to load trending topics');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [apiUrl, regionFilter, riskFilter, statusFilter]);

  // Fetch analytics
  const fetchAnalytics = useCallback(async () => {
    try {
      const response = await fetch(`${apiUrl}/api/analytics/`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (err) {
      console.error('Error fetching analytics:', err);
    }
  }, [apiUrl]);

  // Initial fetch
  useEffect(() => {
    fetchTrends();
    fetchAnalytics();
    
    // Auto-refresh every 30 seconds
    const intervalId = setInterval(() => {
      fetchTrends();
      fetchAnalytics();
    }, 30000);
    
    return () => clearInterval(intervalId);
  }, [fetchTrends, fetchAnalytics]);

  // Handle manual refresh
  const handleRefresh = () => {
    fetchTrends(true);
    fetchAnalytics();
    
    // Trigger backend collection
    fetch(`${apiUrl}/api/trends/collect/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ regions: ['global', 'africa', 'us', 'europe', 'india'] }),
    }).catch(err => console.log('Collection trigger:', err.message));
  };

  // Handle filter change
  const handleFilterChange = (filterType, value) => {
    switch (filterType) {
      case 'region':
        setRegionFilter(value);
        break;
      case 'risk':
        setRiskFilter(value);
        break;
      case 'status':
        setStatusFilter(value);
        break;
    }
  };

  // Handle topic click
  const handleTopicClick = (topic) => {
    if (onTopicClick) {
      onTopicClick(topic);
    }
  };

  // Render loading state
  if (isLoading && trends.length === 0) {
    return (
      <div className="trending-topics-container">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading trending topics...</p>
        </div>
      </div>
    );
  }

  // Render error state with demo data
  if (error && trends.length === 0) {
    return (
      <div className="trending-topics-container">
        <div className="trending-header">
          <h3 className="trending-title">
            <TrendingIcon />
            AI Trend Discovery
          </h3>
          <button 
            className="refresh-button" 
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshIcon />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
        
        <div className="error-state">
          <AlertIcon />
          <p>Unable to connect to trend detection service</p>
          <p className="error-detail">{error}</p>
          <p className="help-text">Make sure the backend server is running</p>
          <button className="retry-button" onClick={() => fetchTrends()}>
            Try Again
          </button>
        </div>
        
        {/* Demo data */}
        <div className="demo-notice">
          <p>Demo Trends (Backend not connected):</p>
          {DEMO_TRENDS.map((trend, idx) => (
            <TrendCard 
              key={idx} 
              trend={trend} 
              onClick={handleTopicClick}
              isDemo={true}
            />
          ))}
        </div>
      </div>
    );
  }

  // Render main dashboard
  return (
    <div className="trending-topics-container dashboard">
      {/* Header */}
      <div className="trending-header">
        <h3 className="trending-title">
          <TrendingIcon />
          AI Trend Discovery
        </h3>
        <button 
          className="refresh-button" 
          onClick={handleRefresh}
          disabled={isRefreshing}
        >
          <RefreshIcon />
          {isRefreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Analytics Summary */}
      {analytics && (
        <div className="analytics-summary">
          <div className="analytics-stat">
            <span className="stat-value">{analytics.total_trends}</span>
            <span className="stat-label">Total Trends</span>
          </div>
          <div className="analytics-stat warning">
            <span className="stat-value">{analytics.high_risk_trends}</span>
            <span className="stat-label">High Risk</span>
          </div>
          <div className="analytics-stat">
            <span className="stat-value">{analytics.pending_verification}</span>
            <span className="stat-label">Need Verification</span>
          </div>
          <div className="analytics-stat success">
            <span className="stat-value">{analytics.verified_claims}</span>
            <span className="stat-label">Verified</span>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="filters-bar">
        <select 
          value={regionFilter} 
          onChange={(e) => handleFilterChange('region', e.target.value)}
          className="filter-select"
        >
          <option value="">All Regions</option>
          <option value="global">Global</option>
          <option value="africa">Africa</option>
          <option value="us">United States</option>
          <option value="europe">Europe</option>
          <option value="india">India</option>
          <option value="asia">Asia</option>
        </select>
        
        <select 
          value={riskFilter} 
          onChange={(e) => handleFilterChange('risk', e.target.value)}
          className="filter-select"
        >
          <option value="">All Risk Levels</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        
        <select 
          value={statusFilter} 
          onChange={(e) => handleFilterChange('status', e.target.value)}
          className="filter-select"
        >
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="verified">Verified</option>
          <option value="false">False Claim</option>
          <option value="true">True</option>
        </select>
      </div>

      {/* Trend Cards */}
      <div className="trends-list">
        {trends.length > 0 ? (
          trends.slice(0, 20).map((trend) => (
            <TrendCard 
              key={trend.id} 
              trend={trend} 
              onClick={handleTopicClick}
            />
          ))
        ) : (
          <div className="empty-state">
            <GlobeIcon />
            <p>No trends found</p>
            <p className="help-text">Try adjusting your filters or refresh to collect new data</p>
          </div>
        )}
      </div>

      {/* Last updated */}
      <div className="last-updated">
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

// Trend Card Component
const TrendCard = ({ trend, onClick, isDemo = false }) => {
  const riskBadge = RISK_BADGES[trend.risk_level] || RISK_BADGES.low;
  const verificationBadge = VERIFICATION_BADGES[trend.verification_status] || VERIFICATION_BADGES.pending;
  
  return (
    <div 
      className={`trend-card ${trend.risk_level === 'critical' || trend.risk_level === 'high' ? 'high-risk' : ''}`}
      onClick={() => onClick(trend.topic)}
    >
      {/* Header */}
      <div className="trend-header">
        <h4 className="trend-topic">{trend.topic}</h4>
        <span 
          className="risk-badge"
          style={{ backgroundColor: riskBadge.color, color: riskBadge.textColor }}
        >
          {riskBadge.label}
        </span>
      </div>
      
      {/* Metrics Row */}
      <div className="trend-metrics">
        {/* Virality Score */}
        <div className="metric">
          <span className="metric-label">Virality</span>
          <div className="engagement-bar-container">
            <div 
              className="engagement-bar"
              style={{ 
                width: `${trend.engagement_score || 0}%`,
                backgroundColor: getEngagementColor(trend.engagement_score || 0)
              }}
            ></div>
          </div>
          <span className="metric-value">{Math.round(trend.engagement_score || 0)}%</span>
        </div>
        
        {/* Risk Score */}
        <div className="metric">
          <span className="metric-label">Risk</span>
          <div className="risk-score-container">
            <span 
              className="risk-score"
              style={{ color: riskBadge.color }}
            >
              {Math.round(trend.misinformation_risk_score || 0)}
            </span>
          </div>
        </div>
        
        {/* Priority Score */}
        <div className="metric">
          <span className="metric-label">Priority</span>
          <span className="metric-value priority">
            {(trend.priority_score || 0).toFixed(2)}
          </span>
        </div>
      </div>
      
      {/* Footer */}
      <div className="trend-footer">
        {/* Source Platforms */}
        <div className="source-platforms">
          {(trend.source_platforms || []).slice(0, 4).map((platform, idx) => (
            <span key={idx} className="platform-tag">{platform}</span>
          ))}
        </div>
        
        {/* Region */}
        <span className="region-tag">
          <GlobeIcon />
          {REGION_NAMES[trend.primary_region] || trend.primary_region}
        </span>
        
        {/* Verification Status */}
        <span 
          className="verification-badge"
          style={{ backgroundColor: verificationBadge.color }}
        >
          {verificationBadge.label}
        </span>
        
        {/* Timestamp */}
        <span className="timestamp">
          {formatRelativeTime(trend.last_updated)}
        </span>
      </div>
      
      {/* Prediction indicator */}
      {trend.predicted_trend_score > 0 && (
        <div className="trend-prediction">
          <span className="prediction-label">Predicted Trend Score:</span>
          <span className="prediction-value">{Math.round(trend.predicted_trend_score)}</span>
        </div>
      )}
    </div>
  );
};

// Demo data for offline mode
const DEMO_TRENDS = [
  {
    id: 1,
    topic: "New vaccine causes infertility - Health misinformation spreading rapidly",
    engagement_score: 85,
    misinformation_risk_score: 92,
    risk_level: "critical",
    verification_status: "pending",
    primary_region: "global",
    source_platforms: ["twitter", "facebook", "reddit"],
    priority_score: 78.2,
    predicted_trend_score: 95,
    last_updated: new Date().toISOString(),
  },
  {
    id: 2,
    topic: "Climate change summit reaches historic agreement",
    engagement_score: 72,
    misinformation_risk_score: 25,
    risk_level: "low",
    verification_status: "verified",
    primary_region: "europe",
    source_platforms: ["news_api", "rss"],
    priority_score: 18.0,
    predicted_trend_score: 65,
    last_updated: new Date().toISOString(),
  },
  {
    id: 3,
    topic: "Election fraud claims spread across social media",
    engagement_score: 90,
    misinformation_risk_score: 88,
    risk_level: "critical",
    verification_status: "pending",
    primary_region: "us",
    source_platforms: ["twitter", "reddit"],
    priority_score: 79.2,
    predicted_trend_score: 98,
    last_updated: new Date().toISOString(),
  },
];

export default TrendingTopics;

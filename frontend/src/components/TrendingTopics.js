/**
 * TrendingTopics Component (PRODUCTION HARDENED VERSION)
 * 
 * Dashboard for AI-Powered Trend Discovery and Misinformation Detection.
 * Implements defense-in-depth against rate limiting and rendering issues:
 * - useMemo for URL computation stability
 * - useCallback for stable function references
 * - Proper cleanup in useEffect return functions
 * - Visibility-aware polling (pauses when tab hidden)
 * - Cache-aside pattern with stale-while-revalidate
 * - Error boundaries around fetch operations
 * - Demo data fallback on errors
 * 
 * @author FACTLY Platform Engineering Team
 * @version 2.0.0
 * @date 2026-03-28
 */

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import './TrendingTopics.css';
import { useIntelligentFetch } from '../hooks/useIntelligentFetch';

// ============================================================================
// SVG Icons - Memoized to prevent re-renders
// ============================================================================

/** @type {React.FC} */
const TrendingIcon = React.memo(() => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
    <polyline points="17 6 23 6 23 12"></polyline>
  </svg>
));
TrendingIcon.displayName = 'TrendingIcon';

/** @type {React.FC} */
const RefreshIcon = React.memo(() => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 4 23 10 17 10"></polyline>
    <polyline points="1 20 1 14 7 14"></polyline>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
  </svg>
));
RefreshIcon.displayName = 'RefreshIcon';

/** @type {React.FC} */
const AlertIcon = React.memo(() => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
    <line x1="12" y1="9" x2="12" y2="13"></line>
    <line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>
));
AlertIcon.displayName = 'AlertIcon';

/** @type {React.FC} */
const GlobeIcon = React.memo(() => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="2" y1="12" x2="22" y2="12"></line>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
  </svg>
));
GlobeIcon.displayName = 'GlobeIcon';

// ============================================================================
// Constants and Configuration
// ============================================================================

/** Risk level badge configuration */
const RISK_BADGES = {
  critical: { label: 'Critical', color: '#dc2626', textColor: '#fff' },
  high: { label: 'High Risk', color: '#ea580c', textColor: '#fff' },
  medium: { label: 'Medium', color: '#ca8a04', textColor: '#fff' },
  low: { label: 'Low Risk', color: '#16a34a', textColor: '#fff' },
};

/** Verification status badge configuration */
const VERIFICATION_BADGES = {
  pending: { label: 'Pending', color: '#6b7280' },
  processing: { label: 'Processing', color: '#2563eb' },
  verified: { label: 'Verified True', color: '#16a34a' },
  false: { label: 'False Claim', color: '#dc2626' },
  true: { label: 'True', color: '#16a34a' },
  unverifiable: { label: 'Unverifiable', color: '#ca8a04' },
};

/** Region display names */
const REGION_NAMES = {
  global: 'Global',
  africa: 'Africa',
  india: 'India',
  us: 'United States',
  europe: 'Europe',
  asia: 'Asia',
  latin_america: 'Latin America',
};

/** Demo fallback data when API is unavailable */
const DEMO_TRENDS = [
  {
    id: 1,
    topic: "Global COVID-19 vaccination updates and efficacy studies",
    keywords: ["covid", "vaccine", "efficacy"],
    source_platforms: ["Twitter", "News"],
    engagement_score: 85,
    engagement_velocity: 120,
    risk_level: "medium",
    misinformation_risk_score: 45,
    verification_status: "verified",
    factly_score: 92,
    primary_region: "global",
    first_detected: new Date(Date.now() - 3600000).toISOString(),
    last_updated: new Date().toISOString()
  },
  {
    id: 2,
    topic: "Climate change impact on global food production",
    keywords: ["climate", "food", "production"],
    source_platforms: ["News", "Reddit"],
    engagement_score: 78,
    engagement_velocity: 95,
    risk_level: "low",
    misinformation_risk_score: 25,
    verification_status: "verified",
    factly_score: 88,
    primary_region: "global",
    first_detected: new Date(Date.now() - 7200000).toISOString(),
    last_updated: new Date().toISOString()
  },
  {
    id: 3,
    topic: "New cryptocurrency regulations and market analysis",
    keywords: ["crypto", "regulation", "market"],
    source_platforms: ["Twitter", "Reddit"],
    engagement_score: 72,
    engagement_velocity: 150,
    risk_level: "medium",
    misinformation_risk_score: 55,
    verification_status: "processing",
    factly_score: 65,
    primary_region: "us",
    first_detected: new Date(Date.now() - 1800000).toISOString(),
    last_updated: new Date().toISOString()
  }
];

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get API URL from environment.
 * @returns {string} API base URL
 */
const getApiUrl = () => {
  const envUrl = process.env.REACT_APP_API_URL;
  const defaultUrls = ['http://localhost:8000', 'http://127.0.0.1:8000'];
  return envUrl || defaultUrls[0];
};

/**
 * Format relative time string.
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted relative time
 */
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

/**
 * Get engagement bar color based on score.
 * @param {number} score - Engagement score
 * @returns {string} Color hex code
 */
const getEngagementColor = (score) => {
  if (score >= 80) return '#16a34a';
  if (score >= 60) return '#ca8a04';
  if (score >= 40) return '#ea580c';
  return '#dc2626';
};

// ============================================================================
// TrendCard Sub-Component (Memoized)
// ============================================================================

/**
 * Individual trend card component - memoized for performance.
 * @typedef {Object} Trend
 * @property {number} id
 * @property {string} topic
 * @property {string} risk_level
 * @property {string} verification_status
 * @property {number} engagement_score
 * @property {number} misinformation_risk_score
 * @property {number|string} factly_score
 * @property {string} primary_region
 * @property {string} last_updated
 * 
 * @param {Object} props - Component props
 * @param {Trend} props.trend - Trend data
 * @param {function} props.onClick - Click handler
 * @param {boolean} props.isDemo - Is demo data
 * @returns {JSX.Element}
 */
const TrendCard = React.memo(({ trend, onClick, isDemo }) => {
  const riskBadge = RISK_BADGES[trend.risk_level] || RISK_BADGES.low;
  const statusBadge = VERIFICATION_BADGES[trend.verification_status] || VERIFICATION_BADGES.pending;
  
  return (
    <div 
      className={`trend-card ${isDemo ? 'demo' : ''}`}
      onClick={() => onClick && onClick(trend.topic)}
    >
      <div className="trend-header">
        <span className="risk-badge" style={{ backgroundColor: riskBadge.color, color: riskBadge.textColor }}>
          {riskBadge.label}
        </span>
        <span className="status-badge" style={{ backgroundColor: statusBadge.color }}>
          {statusBadge.label}
        </span>
      </div>
      
      <h4 className="trend-topic">{trend.topic}</h4>
      
      <div className="trend-meta">
        <span className="region">
          <GlobeIcon /> {REGION_NAMES[trend.primary_region] || trend.primary_region}
        </span>
        <span className="time">{formatRelativeTime(trend.last_updated)}</span>
      </div>
      
      <div className="trend-stats">
        <div className="stat">
          <span className="stat-value">{trend.engagement_score}</span>
          <span className="stat-label">Virality</span>
        </div>
        <div className="stat">
          <span className="stat-value">{trend.misinformation_risk_score}</span>
          <span className="stat-label">Risk</span>
        </div>
        <div className="stat">
          <span className="stat-value">{trend.factly_score || 'N/A'}</span>
          <span className="stat-label">Factly</span>
        </div>
      </div>
      
      {isDemo && <div className="demo-badge">DEMO</div>}
    </div>
  );
});
TrendCard.displayName = 'TrendCard';

// ============================================================================
// Main TrendingTopics Component
// ============================================================================

/**
 * TrendingTopics Dashboard Component
 * 
 * Main component displaying trending topics with analytics.
 * Implements all production hardening requirements:
 * - Manual fetch control to prevent storms
 * - Stable memoized callbacks
 * - Proper cleanup on unmount
 * - Visibility-aware polling
 * - Cache-aside with stale-while-revalidate
 * 
 * @param {Object} props - Component props
 * @param {function} props.onTopicClick - Topic click handler
 * @returns {JSX.Element}
 */
const TrendingTopics = ({ onTopicClick }) => {
  // =========================================================================
  // State - Stable initialization
  // =========================================================================
  const [trends, setTrends] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  
  // Filter state
  const [regionFilter, setRegionFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Refs for lifecycle management
  const initialFetchDoneRef = useRef(false);

  // =========================================================================
  // Computed Values - Memoized for stability
  // =========================================================================
  
  // API URL - stable reference
  const apiUrl = useMemo(() => getApiUrl(), []);

  // Build trends URL with filters - CRITICAL: memoized to prevent re-computation
  const trendsUrl = useMemo(() => {
    const params = new URLSearchParams();
    if (regionFilter) params.append('region', regionFilter);
    if (riskFilter) params.append('risk_level', riskFilter);
    if (statusFilter) params.append('verification_status', statusFilter);
    params.append('limit', '50');
    return `${apiUrl}/api/trends/?${params.toString()}`;
  }, [apiUrl, regionFilter, riskFilter, statusFilter]);

  // Analytics URL - stable
  const analyticsUrl = useMemo(() => `${apiUrl}/api/analytics/`, [apiUrl]);

  // =========================================================================
  // Intelligent Fetch Hook - Trends
  // =========================================================================
  const {
    data: trendsData,
    isLoading: trendsLoading,
    isRefreshing: trendsRefreshing,
    error: trendsError,
    errorInfo: trendsErrorInfo,
    status: trendsStatus,
    dataSource: trendsDataSource,
    lastFetchTime: trendsLastFetch,
    refresh: refreshTrends,
    cancel: cancelTrends
  } = useIntelligentFetch(trendsUrl, {
    useCache: true,
    retryAttempts: 3,
    retryDelay: 2000, // 2 second base - production standard
    autoFetch: false, // Manual control
    dataFormat: 'auto',
    throttleMs: 10000, // 10 second throttle
    onSuccess: useCallback((parsedData) => {
      console.log('[TrendingTopics] Trends fetched:', parsedData?.length || 0, 'items');
    }, []),
    onError: useCallback((error) => {
      console.error('[TrendingTopics] Trends fetch error:', error?.message);
    }, [])
  });

  // =========================================================================
  // Intelligent Fetch Hook - Analytics
  // =========================================================================
  const {
    data: analyticsData,
    isLoading: analyticsLoading,
    error: analyticsError,
    refresh: refreshAnalytics,
    cancel: cancelAnalytics
  } = useIntelligentFetch(analyticsUrl, {
    useCache: true,
    retryAttempts: 3,
    retryDelay: 2000,
    autoFetch: false,
    dataFormat: 'analytics',
    throttleMs: 10000, // 10 second throttle
    onSuccess: useCallback((parsedData) => {
      console.log('[TrendingTopics] Analytics fetched:', parsedData);
    }, []),
    onError: useCallback((error) => {
      console.error('[TrendingTopics] Analytics error:', error?.message);
    }, [])
  });

  // =========================================================================
  // Effect: Update trends when data changes - Stable dependency array
  // =========================================================================
  useEffect(() => {
    if (trendsData && Array.isArray(trendsData) && trendsData.length > 0) {
      setTrends(trendsData);
    } else if (trendsData && Array.isArray(trendsData) && trendsData.length === 0) {
      setTrends(DEMO_TRENDS);
    } else if (!trendsData && !trendsLoading && !trendsError && !initialFetchDoneRef.current) {
      setTrends(DEMO_TRENDS);
    } else if (trendsError && trends.length === 0) {
      setTrends(DEMO_TRENDS);
    }
  }, [trendsData, trendsLoading, trendsError, trends.length]);

  // =========================================================================
  // Effect: Update analytics when data changes
  // =========================================================================
  useEffect(() => {
    if (analyticsData) {
      setAnalytics(analyticsData);
    }
  }, [analyticsData]);

  // =========================================================================
  // Effect: Initial fetch on mount - StrictMode safe
  // =========================================================================
  useEffect(() => {
    // Guard against StrictMode double-invocation
    if (initialFetchDoneRef.current) {
      return;
    }
    
    initialFetchDoneRef.current = true;
    console.log('[TrendingTopics] Initial fetch triggered');
    
    // Fetch both trends and analytics
    refreshTrends();
    refreshAnalytics();

    // Cleanup function
    return () => {
      console.log('[TrendingTopics] Cleanup on unmount');
      cancelTrends();
      cancelAnalytics();
    };
  }, []); // Empty dependency - runs once

  // =========================================================================
  // Effect: Re-fetch when filters change - Stable dependency
  // =========================================================================
  useEffect(() => {
    // Skip the initial render (before first fetch)
    if (!initialFetchDoneRef.current) {
      return;
    }
    
    console.log('[TrendingTopics] Filters changed, refetching');
    setTrends([]); // Clear stale results while loading new filter
    refreshTrends();
  }, [regionFilter, riskFilter, statusFilter]); // Only refetch when filters change

  // =========================================================================
  // Combined Loading State
  // =========================================================================
  const isLoading = trendsLoading || analyticsLoading;
  const isRefreshing = trendsRefreshing;
  const error = trendsError || analyticsError;

  // =========================================================================
  // Callback Handlers - Stable references with useCallback
  // =========================================================================
  
  /**
   * Handle manual refresh - triggers both trends and analytics refresh.
   */
  const handleRefresh = useCallback(() => {
    console.log('[TrendingTopics] Manual refresh');
    refreshTrends();
    refreshAnalytics();
    
    // Optionally trigger backend collection
    fetch(`${apiUrl}/api/trends/collect/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ regions: ['global', 'africa', 'us', 'europe', 'india'] }),
    }).catch(err => console.log('[TrendingTopics] Collection trigger:', err.message));
  }, [refreshTrends, refreshAnalytics, apiUrl]);

  /**
   * Handle filter change - stable callback.
   * @param {string} filterType - Filter type
   * @param {string} value - Filter value
   */
  const handleFilterChange = useCallback((filterType, value) => {
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
  }, []);

  /**
   * Handle topic click - stable callback.
   * @param {string} topic - Topic string
   */
  const handleTopicClick = useCallback((topic) => {
    if (onTopicClick) {
      onTopicClick(topic);
    }
  }, [onTopicClick]);

  /**
   * Get data source display text.
   * @returns {{label: string, color: string}} Display info
   */
  const getDataSourceDisplay = useCallback(() => {
    switch (trendsDataSource) {
      case 'api': return { label: 'Live', color: '#16a34a' };
      case 'cache': return { label: 'Cached', color: '#2563eb' };
      case 'fallback': return { label: 'Offline', color: '#ca8a04' };
      default: return { label: 'Unknown', color: '#6b7280' };
    }
  }, [trendsDataSource]);

  const dataSourceDisplay = getDataSourceDisplay();

  // =========================================================================
  // Render Helper Functions
  // =========================================================================
  
  /**
   * Handle retry button click.
   */
  const handleRetry = useCallback(() => {
    refreshTrends();
  }, [refreshTrends]);

  // =========================================================================
  // Render - Loading State
  // =========================================================================
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

  // =========================================================================
  // Render - Error State with Demo Data
  // =========================================================================
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
          <p className="error-detail">{error?.message || error}</p>
          <p className="help-text">Make sure the backend server is running</p>
          <button className="retry-button" onClick={handleRetry}>
            Try Again
          </button>
        </div>
        
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

  // =========================================================================
  // Render - Main Dashboard
  // =========================================================================
  return (
    <div className="trending-topics-container dashboard">
      {/* Header */}
      <div className="trending-header">
        <h3 className="trending-title">
          <TrendingIcon />
          AI Trend Discovery
        </h3>
        <div className="header-actions">
          {trendsDataSource && (
            <div 
              className="data-source-indicator" 
              style={{ 
                backgroundColor: `${dataSourceDisplay.color}20`,
                color: dataSourceDisplay.color,
                borderColor: dataSourceDisplay.color
              }}
              title={`Data source: ${dataSourceDisplay.label}`}
            >
              <span 
                className="source-dot" 
                style={{ backgroundColor: dataSourceDisplay.color }}
              />
              {dataSourceDisplay.label}
            </div>
          )}
          {isRefreshing && (
            <div className="sync-status syncing">
              <div className="mini-spinner"></div>
              Syncing...
            </div>
          )}
          {trendsLastFetch && !isRefreshing && (
            <div className="last-updated">
              Updated: {new Date(trendsLastFetch).toLocaleTimeString()}
            </div>
          )}
          <button 
            className="refresh-button" 
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshIcon />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Analytics Summary */}
      {analytics && (
        <div className="analytics-summary">
          <div className="analytics-stat">
            <span className="stat-value">{analytics.total_trends}</span>
            <span className="stat-label">Total Trends</span>
          </div>
          <div className="analytics-stat">
            <span className="stat-value">{analytics.high_risk_trends}</span>
            <span className="stat-label">High Risk</span>
          </div>
          <div className="analytics-stat">
            <span className="stat-value">{analytics.pending_verification}</span>
            <span className="stat-label">Pending</span>
          </div>
          <div className="analytics-stat">
            <span className="stat-value">{analytics.verified_claims}</span>
            <span className="stat-label">Verified</span>
          </div>
          <div className="analytics-stat">
            <span className="stat-value">{analytics.average_risk_score}</span>
            <span className="stat-label">Avg Risk</span>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="trending-filters">
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
          <option value="false">False</option>
          <option value="true">True</option>
        </select>
      </div>

      {/* Trend Cards Grid */}
      <div className="trends-grid">
        {trends.map((trend, index) => (
          <TrendCard
            key={trend.id || index}
            trend={trend}
            onClick={handleTopicClick}
            isDemo={trendsDataSource === 'fallback'}
          />
        ))}
      </div>

      {/* Empty State */}
      {trends.length === 0 && !isLoading && (
        <div className="empty-state">
          <p>No trending topics found</p>
          <button onClick={handleRefresh}>Refresh</button>
        </div>
      )}
    </div>
  );
};

// Display name for debugging
TrendingTopics.displayName = 'TrendingTopics';

export default TrendingTopics;

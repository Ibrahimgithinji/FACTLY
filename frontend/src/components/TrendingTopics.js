/**
 * TrendingTopics Component - Complete Rewrite
 * 
 * Fetches from GET /api/verification/trending/ and POST /api/verification/refresh/
 * Implements proper polling with abort handling and error states.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import './TrendingTopics.css';

// ============================================================================
// Constants
// ============================================================================

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const POLL_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes

const RISK_BADGES = {
  critical: { label: 'Critical', color: '#dc2626', textColor: '#fff' },
  high: { label: 'High Risk', color: '#ea580c', textColor: '#fff' },
  medium: { label: 'Medium', color: '#ca8a04', textColor: '#fff' },
  low: { label: 'Low Risk', color: '#16a34a', textColor: '#fff' },
};

const VERIFICATION_BADGES = {
  pending: { label: 'Pending', color: '#6b7280' },
  processing: { label: 'Processing', color: '#2563eb' },
  verified: { label: 'Verified', color: '#16a34a' },
  false: { label: 'False', color: '#dc2626' },
  true: { label: 'True', color: '#16a34a' },
  unverifiable: { label: 'Unverifiable', color: '#ca8a04' },
};

// ============================================================================
// Helper Functions
// ============================================================================

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

const getFreshnessDot = (lastUpdated) => {
  if (!lastUpdated) return 'gray';
  const date = new Date(lastUpdated);
  const diff = Date.now() - date.getTime();
  const minutes = diff / 60000;
  if (minutes < 30) return 'green';
  if (minutes < 60) return 'yellow';
  return 'red';
};

// ============================================================================
// SVG Icons
// ============================================================================

const TrendingIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
    <polyline points="17 6 23 6 23 12"></polyline>
  </svg>
);

const RefreshIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="23 4 23 10 17 10"></polyline>
    <polyline points="1 20 1 14 7 14"></polyline>
    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
  </svg>
);

const AlertIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
    <line x1="12" y1="9" x2="12" y2="13"></line>
    <line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>
);

// ============================================================================
// Demo Data
// ============================================================================

const DEMO_TOPICS = [
  {
    id: 1,
    topic: "Global COVID-19 vaccination updates and efficacy studies",
    mention_count: 1250,
    trending_score: 85,
    freshness: 0.92,
    risk_level: "medium",
    verification_status: "verified",
    last_updated: new Date(Date.now() - 1800000).toISOString()
  },
  {
    id: 2,
    topic: "Climate change impact on global food production",
    mention_count: 890,
    trending_score: 78,
    freshness: 0.88,
    risk_level: "low",
    verification_status: "verified",
    last_updated: new Date(Date.now() - 3600000).toISOString()
  },
  {
    id: 3,
    topic: "New cryptocurrency regulations and market analysis",
    mention_count: 720,
    trending_score: 72,
    freshness: 0.65,
    risk_level: "medium",
    verification_status: "processing",
    last_updated: new Date(Date.now() - 900000).toISOString()
  }
];

// ============================================================================
// Main Component
// ============================================================================

const TrendingTopics = ({ onTopicClick }) => {
  // State variables
  const [topics, setTopics] = useState([]);
  const [globalEvents, setGlobalEvents] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [cacheStats, setCacheStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchFailed, setFetchFailed] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState(null);
  const [dataSource, setDataSource] = useState(null);

  // Refs for lifecycle management
  const abortControllerRef = useRef(null);
  const pollIntervalRef = useRef(null);
  const isFetchingRef = useRef(false);
  const fetchTopicsRef = useRef(null);

  // =========================================================================
  // Fetch Function - Handles both GET and POST refresh
  // =========================================================================

  const fetchTopics = useCallback(async (isManualRefresh = false) => {
    // Prevent concurrent requests
    if (isFetchingRef.current) {
      return;
    }

    // Create new abort controller
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    isFetchingRef.current = true;

    try {
      // If manual refresh, POST to trigger backend refresh first
      if (isManualRefresh) {
        try {
          const refreshResponse = await fetch(
            `${API_BASE_URL}/api/verification/refresh/`,
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ task: 'all', force: true }),
              signal: abortControllerRef.current.signal
            }
          );

          // Check Content-Type before parsing JSON
          const contentType = refreshResponse.headers.get('content-type');
          if (!contentType || !contentType.includes('application/json')) {
            const text = await refreshResponse.text();
            console.warn('[TrendingTopics] POST returned non-JSON:', text.substring(0, 200));
          } else if (refreshResponse.ok) {
            // Wait for backend to start processing
            await new Promise(resolve => setTimeout(resolve, 800));
          }
        } catch (postErr) {
          if (postErr.name !== 'AbortError') {
            console.warn('[TrendingTopics] POST refresh failed, continuing to GET:', postErr.message);
          }
          setRefreshError('Refresh trigger failed, fetching latest data');
        }
      }

      // Now GET the trending topics
      const response = await fetch(
        `${API_BASE_URL}/api/verification/trending/`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
          signal: abortControllerRef.current.signal
        }
      );

      // Validate Content-Type header
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        throw new Error(`Invalid Content-Type for ${response.url}: ${response.status} - ${text.substring(0, 200)}`);
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Handle the API response structure
      if (data.trending_topics) {
        setTopics(data.trending_topics);
      } else if (Array.isArray(data)) {
        setTopics(data);
      } else {
        setTopics([]);
      }

      // Set additional data if available
      if (data.global_events) {
        setGlobalEvents(data.global_events);
      }
      if (data.last_updated) {
        setLastUpdated(data.last_updated);
      }
      if (data.cache_stats) {
        setCacheStats(data.cache_stats);
      }
      // ENHANCEMENT 2: Surface data_source field
      if (data.data_source) {
        setDataSource(data.data_source);
      }

      // Clear error states on success
      setFetchFailed(false);
      setRefreshError(null);
      setLoading(false);

    } catch (err) {
      if (err.name === 'AbortError') {
        console.log('[TrendingTopics] Fetch aborted');
        return;
      }

      console.error('[TrendingTopics] Fetch error:', err.message);
      setFetchFailed(true);
      setLoading(false);
    } finally {
      isFetchingRef.current = false;
    }
  }, []);

  // =========================================================================
  // Polling Effect - Poll every 5 minutes
  // =========================================================================

  useEffect(() => {
    // Create ref for fetchTopics to use in interval
    fetchTopicsRef.current = fetchTopics;
  }, [fetchTopics]);

  // Polling Effect - Poll every 5 minutes
  useEffect(() => {
    // Initial fetch
    fetchTopicsRef.current(false);

    // Set up polling interval
    pollIntervalRef.current = setInterval(() => {
      fetchTopicsRef.current(false);
    }, POLL_INTERVAL_MS);

    // Cleanup on unmount
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // =========================================================================
  // Handle Manual Refresh
  // =========================================================================

  const handleManualRefresh = useCallback(() => {
    setIsRefreshing(true);
    fetchTopics(true).finally(() => {
      setIsRefreshing(false);
    });
  }, [fetchTopics]);

  // =========================================================================
  // Handle Topic Click
  // =========================================================================

  const handleTopicClick = useCallback((topic) => {
    if (onTopicClick && typeof onTopicClick === 'function') {
      onTopicClick(topic.topic || topic);
    }
  }, [onTopicClick]);

  // =========================================================================
  // Render: Skeleton Loading State
  // =========================================================================

  if (loading && topics.length === 0) {
    return (
      <div className="trending-topics-container">
        <div className="trending-header">
          <h3 className="trending-title">
            <TrendingIcon />
            Trending Topics
          </h3>
        </div>
        <div className="skeleton-list">
          {[1, 2, 3].map(i => (
            <div key={i} className="skeleton-card">
              <div className="skeleton-title"></div>
              <div className="skeleton-meta"></div>
              <div className="skeleton-stats"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // =========================================================================
  // ENHANCEMENT 1: Render Error State with DEMO Fallback
  // Instead of showing an error, fall back to demo topics with a banner
  // =========================================================================

  if (fetchFailed && topics.length === 0) {
    return (
      <div className="trending-topics-container">
        <div className="trending-header">
          <h3 className="trending-title">
            <TrendingIcon />
            Trending Topics
          </h3>
          <button 
            className="refresh-button" 
            onClick={handleManualRefresh}
            disabled={isRefreshing}
          >
            <RefreshIcon />
            {isRefreshing ? 'Refreshing...' : 'Try Again'}
          </button>
        </div>
        
        {/* ENHANCEMENT 1: Show demo data instead of error */}
        <div className="warning-banner">
          <AlertIcon />
          Demo data — backend unavailable
        </div>
        
        {/* Render DEMO_TOPICS as fallback */}
        <div className="topics-list">
          {DEMO_TOPICS.map((topic) => {
            const riskBadge = RISK_BADGES[topic.risk_level] || RISK_BADGES.low;
            const statusBadge = VERIFICATION_BADGES[topic.verification_status] || VERIFICATION_BADGES.pending;
            const freshnessColor = getFreshnessDot(topic.last_updated);

            return (
              <div
                key={topic.id || topic.topic}
                className="topic-card"
                onClick={() => handleTopicClick(topic)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleTopicClick(topic);
                  }
                }}
              >
                <div className="topic-header">
                  <span
                    className="risk-badge"
                    style={{ backgroundColor: riskBadge.color, color: riskBadge.textColor }}
                  >
                    {riskBadge.label}
                  </span>
                  <span
                    className="status-badge"
                    style={{ backgroundColor: statusBadge.color }}
                  >
                    {statusBadge.label}
                  </span>
                </div>

                <h4 className="topic-title">{topic.topic}</h4>

                <div className="topic-meta">
                  <span className="freshness">
                    <span
                      className="freshness-dot"
                      style={{ backgroundColor: freshnessColor }}
                    />
                    Freshness: {Math.round((topic.freshness || 0) * 100)}%
                  </span>
                  {topic.last_updated && (
                    <span className="timestamp">
                      {formatRelativeTime(topic.last_updated)}
                    </span>
                  )}
                </div>

                <div className="topic-stats">
                  <div className="stat">
                    <span className="stat-value">{topic.mention_count || 0}</span>
                    <span className="stat-label">Mentions</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">{Math.round(topic.trending_score || 0)}</span>
                    <span className="stat-label">Trend Score</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // =========================================================================
  // Render: Full UI with Topics
  // =========================================================================

  return (
    <div className="trending-topics-container">
      {/* Header */}
      <div className="trending-header">
        <h3 className="trending-title">
          <TrendingIcon />
          Trending Topics
        </h3>
        <div className="header-actions">
          {lastUpdated && (
            <span className="last-updated">
              Updated: {formatRelativeTime(lastUpdated)}
            </span>
          )}
          {/* ENHANCEMENT 2: Show data_source badge */}
          {dataSource && (
            <span className="data-source-badge">
              Source: {dataSource}
            </span>
          )}
          <button 
            className="refresh-button" 
            onClick={handleManualRefresh}
            disabled={isRefreshing}
          >
            <RefreshIcon />
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Error Message (if refresh failed but we have cached data) */}
      {refreshError && (
        <div className="warning-banner">
          {refreshError}
        </div>
      )}

      {/* Global Events */}
      {globalEvents.length > 0 && (
        <div className="global-events">
          <h4>Global Events</h4>
          <div className="events-list">
            {globalEvents.map((event, idx) => (
              <span key={idx} className="event-tag">
                {event.title || event.topic || JSON.stringify(event).substring(0, 50)}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Topics List */}
      <div className="topics-list">
        {topics.map((topic) => {
          const riskBadge = RISK_BADGES[topic.risk_level] || RISK_BADGES.low;
          const statusBadge = VERIFICATION_BADGES[topic.verification_status] || VERIFICATION_BADGES.pending;
          const freshnessColor = getFreshnessDot(topic.last_updated);

          return (
            <div
              key={topic.id || topic.topic}
              className="topic-card"
              onClick={() => handleTopicClick(topic)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  handleTopicClick(topic);
                }
              }}
            >
              <div className="topic-header">
                <span
                  className="risk-badge"
                  style={{ backgroundColor: riskBadge.color, color: riskBadge.textColor }}
                >
                  {riskBadge.label}
                </span>
                <span
                  className="status-badge"
                  style={{ backgroundColor: statusBadge.color }}
                >
                  {statusBadge.label}
                </span>
              </div>

              <h4 className="topic-title">{topic.topic}</h4>

              <div className="topic-meta">
                <span className="freshness">
                  <span
                    className="freshness-dot"
                    style={{ backgroundColor: freshnessColor }}
                  />
                  Freshness: {Math.round((topic.freshness || 0) * 100)}%
                </span>
                {topic.last_updated && (
                  <span className="timestamp">
                    {formatRelativeTime(topic.last_updated)}
                  </span>
                )}
              </div>

              <div className="topic-stats">
                <div className="stat">
                  <span className="stat-value">{topic.mention_count || 0}</span>
                  <span className="stat-label">Mentions</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{Math.round(topic.trending_score || 0)}</span>
                  <span className="stat-label">Trend Score</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Cache Stats */}
      {cacheStats && (
        <div className="cache-stats">
          <span>Cache hit rate: {Math.round((cacheStats.hit_rate || 0) * 100)}%</span>
        </div>
      )}
    </div>
  );
};

export default TrendingTopics;

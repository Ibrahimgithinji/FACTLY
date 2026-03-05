/**
 * Trending Topics Component
 * 
 * Displays real-time trending topics and global events
 * to keep users informed about current worldwide developments.
 */

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

const TrendingTopics = ({ onTopicClick }) => {
  const [trendingTopics, setTrendingTopics] = useState([]);
  const [globalEvents, setGlobalEvents] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const fetchTrendingData = useCallback(async (showRefreshing = false) => {
    if (showRefreshing) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/verification/trending/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch trending topics: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.trending_topics) {
        setTrendingTopics(data.trending_topics);
      }
      
      if (data.global_events) {
        setGlobalEvents(data.global_events);
      }
      
      if (data.last_updated) {
        setLastUpdated(new Date(data.last_updated));
      }

    } catch (err) {
      console.error('Error fetching trending topics:', err);
      setError(err.message || 'Failed to load trending topics');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [API_BASE_URL]);

  // Initial fetch
  useEffect(() => {
    fetchTrendingData();
    
    // Auto-refresh every 5 minutes
    const intervalId = setInterval(() => {
      fetchTrendingData();
    }, 5 * 60 * 1000);
    
    return () => clearInterval(intervalId);
  }, [fetchTrendingData]);

  // Handle manual refresh
  const handleRefresh = () => {
    fetchTrendingData(true);
    
    // Also trigger backend refresh
    fetch(`${API_BASE_URL}/api/verification/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task: 'all' }),
    }).catch(err => console.error('Failed to trigger refresh:', err));
  };

  // Handle topic click
  const handleTopicClick = (topic) => {
    if (onTopicClick) {
      onTopicClick(topic);
    }
  };

  // Format relative time
  const formatRelativeTime = (date) => {
    if (!date) return 'Never';
    
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  if (isLoading && trendingTopics.length === 0) {
    return (
      <div className="trending-topics-container">
        <div className="loading-state">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error && trendingTopics.length === 0) {
    return (
      <div className="trending-topics-container">
        <div className="error-state">
          <p>Unable to load trending topics</p>
          <p>{error}</p>
          <button className="retry-button" onClick={() => fetchTrendingData()}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="trending-topics-container">
      <div className="trending-header">
        <h3 className="trending-title">
          <TrendingIcon />
          Trending Topics
        </h3>
        <button 
          className="refresh-button" 
          onClick={handleRefresh}
          disabled={isRefreshing}
          title="Refresh trending topics"
        >
          <RefreshIcon />
          {isRefreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {lastUpdated && (
        <p className="last-updated">
          Last updated: {formatRelativeTime(lastUpdated)}
        </p>
      )}

      {/* Trending Topics */}
      {trendingTopics.length > 0 ? (
        <div className="topics-list">
          {trendingTopics.slice(0, 10).map((topic, index) => (
            <button
              key={index}
              className="topic-item"
              onClick={() => handleTopicClick(topic.topic)}
            >
              <span>{topic.topic}</span>
              <span className="topic-score">
                {Math.round(topic.trending_score * 100)}%
              </span>
            </button>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <p>No trending topics available at the moment</p>
        </div>
      )}

      {/* Global Events Section */}
      {globalEvents.length > 0 && (
        <div className="global-events-section">
          <h4 className="section-title">
            <GlobeIcon /> Global Events
          </h4>
          <div className="events-grid">
            {globalEvents.map((event, index) => (
              <div key={index} className="event-card">
                <div className="event-region">{event.region_name}</div>
                <ul className="event-headlines">
                  {event.headlines && event.headlines.slice(0, 3).map((headline, hIndex) => (
                    <li key={hIndex} className="event-headline">
                      <a 
                        href={headline.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        title={headline.title}
                      >
                        {headline.title.length > 80 
                          ? headline.title.substring(0, 80) + '...' 
                          : headline.title}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrendingTopics;

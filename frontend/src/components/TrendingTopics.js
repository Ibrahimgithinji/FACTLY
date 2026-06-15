import React, { useState, useEffect, useCallback, useRef } from 'react';
import { API_ENDPOINTS } from '../utils/api';
import './TrendingTopics.css';

const POLL_INTERVAL_MS = 3 * 60 * 1000;
const FETCH_TIMEOUT_MS = 10000;

const formatRelativeTime = (dateString) => {
  if (!dateString) return null;
  const diff = Date.now() - new Date(dateString).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return new Date(dateString).toLocaleDateString();
};

const TrendingTopics = ({ onTopicClick }) => {
  const [topics, setTopics] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);
  const pollRef = useRef(null);
  const mountedRef = useRef(false);

  const fetchTopics = useCallback(async () => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(API_ENDPOINTS.TRENDING, {
        signal: controller.signal,
        headers: { 'Accept': 'application/json' },
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      if (!mountedRef.current) return;

      const topicsList = data.trending_topics || [];
      setTopics(topicsList);
      setLastUpdated(data.last_updated || null);
      setError(null);
    } catch (err) {
      if (err.name === 'AbortError') return;
      if (!mountedRef.current) return;
      setError(err.message);
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    fetchTopics();

    pollRef.current = setInterval(fetchTopics, POLL_INTERVAL_MS);

    const handleVisibility = () => {
      if (document.visibilityState === 'visible') fetchTopics();
    };
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      mountedRef.current = false;
      clearInterval(pollRef.current);
      document.removeEventListener('visibilitychange', handleVisibility);
      if (abortRef.current) abortRef.current.abort();
    };
  }, [fetchTopics]);

  const handleTopicClick = (topic) => {
    if (onTopicClick) onTopicClick(topic.topic || topic);
  };

  if (loading) {
    return (
      <div className="trending-topics-container">
        <div className="trending-header">
          <span className="trending-title">Loading topics…</span>
        </div>
        <div className="skeleton-list">
          <div className="skeleton-card" />
          <div className="skeleton-card" />
          <div className="skeleton-card" />
        </div>
      </div>
    );
  }

  if (error && topics.length === 0) {
    return (
      <div className="trending-topics-container">
        <div className="trending-header">
          <span className="trending-title">Trending topics</span>
          <button className="refresh-button" onClick={fetchTopics}>Try again</button>
        </div>
        <div className="empty-state">Could not load trending data right now.</div>
      </div>
    );
  }

  if (topics.length === 0) {
    return (
      <div className="trending-topics-container">
        <div className="trending-header">
          <span className="trending-title">Trending topics</span>
        </div>
        <div className="empty-state">No trending topics at the moment.</div>
      </div>
    );
  }

  return (
    <div className="trending-topics-container">
      <div className="trending-header">
        <span className="trending-title">Trending topics</span>
        <div className="header-actions">
          {lastUpdated && (
            <span className="last-updated">
              Updated {formatRelativeTime(lastUpdated)}
            </span>
          )}
          <button className="refresh-button" onClick={fetchTopics}>
            Refresh
          </button>
        </div>
      </div>

      {error && <div className="warning-banner">Refresh failed — showing cached data</div>}

      <div className="topics-list">
        {topics.map((topic) => (
          <div
            key={topic.id || topic.topic}
            className="topic-card"
            onClick={() => handleTopicClick(topic)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') handleTopicClick(topic);
            }}
          >
            {topic.topic}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrendingTopics;

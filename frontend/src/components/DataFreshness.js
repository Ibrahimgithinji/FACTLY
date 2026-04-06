import React from 'react';
import './DataFreshness.css';

/**
 * Data Freshness Badge Component
 * Shows whether data is real-time, cached, or demo
 *
 * Props:
 * - source: 'cache' | 'memory' | 'demo_fallback' | 'realtime'
 * - lastUpdated: ISO timestamp
 * - isWarning: boolean (show warning state)
 */
const DataFreshness = ({ source = 'demo_fallback', lastUpdated, isWarning = false }) => {
  const getFreshnessIndicator = () => {
    if (!lastUpdated) return { dot: 'gray', label: 'Unknown' };

    const date = new Date(lastUpdated);
    const now = new Date();
    const minutesAgo = Math.floor((now - date) / 60000);
    const hoursAgo = Math.floor(minutesAgo / 60);
    const daysAgo = Math.floor(hoursAgo / 24);

    if (minutesAgo < 5) return { dot: 'green', label: 'Just now' };
    if (minutesAgo < 30) return { dot: 'green', label: `${minutesAgo}m ago` };
    if (hoursAgo < 1) return { dot: 'green', label: '< 1h ago' };
    if (hoursAgo < 6) return { dot: 'yellow', label: `${hoursAgo}h ago` };
    if (daysAgo < 1) return { dot: 'orange', label: 'Earlier today' };
    return { dot: 'red', label: `${daysAgo}d ago` };
  };

  const getSourceInfo = () => {
    const sources = {
      cache: {
        icon: '💾',
        label: 'Cached Data',
        description: 'Data from recent cache (< 10 min old)',
        color: 'blue',
      },
      memory: {
        icon: '⚡',
        label: 'Memory Cache',
        description: 'Data from current session cache',
        color: 'blue',
      },
      realtime: {
        icon: '🔴',
        label: 'Real-Time',
        description: 'Live data from API (< 1 min old)',
        color: 'green',
      },
      demo_fallback: {
        icon: '📚',
        label: 'Demo Data',
        description: 'Example data (APIs unavailable)',
        color: 'orange',
      },
    };

    return sources[source] || sources.demo_fallback;
  };

  const freshness = getFreshnessIndicator();
  const sourceInfo = getSourceInfo();

  return (
    <div
      className={`data-freshness ${sourceInfo.color} ${isWarning ? 'warning' : ''}`}
      title={sourceInfo.description}
    >
      <span className={`freshness-dot freshness-${freshness.dot}`} />
      <span className="freshness-badge">
        {sourceInfo.icon} {sourceInfo.label} · {freshness.label}
      </span>
    </div>
  );
};

/**
 * Data Quality Warning Component
 * Warns when using demo data or stale data
 */
export const DataQualityWarning = ({ source, show = true }) => {
  if (!show || source !== 'demo_fallback') return null;

  return (
    <div className="data-quality-warning">
      <div className="warning-icon">⚠️</div>
      <div className="warning-content">
        <h4>Using Example Data</h4>
        <p>
          The verification APIs are currently unavailable. Showing example data for demonstration.
          For real fact-checking, please configure API keys in production.
        </p>
        <button className="learn-more-btn">Learn How to Enable Real Data</button>
      </div>
    </div>
  );
};

/**
 * Real-Time Status Indicator
 * Shows if system is pulling from real internet data
 */
export const RealTimeIndicator = ({
  isRealTime = false,
  dataSource = '',
  onRefresh = null,
}) => {
  return (
    <div className={`realtime-indicator ${isRealTime ? 'active' : 'inactive'}`}>
      <div className="indicator-dot">
        <span className="pulse" />
      </div>
      <div className="indicator-text">
        <span className="status">
          {isRealTime ? '🔴 Real-Time Data' : '📦 Cached Data'}
        </span>
        {dataSource && <span className="source">{dataSource}</span>}
      </div>
      {onRefresh && (
        <button className="refresh-btn" onClick={onRefresh} title="Manually refresh data">
          🔄 Refresh
        </button>
      )}
    </div>
  );
};

/**
 * Data Source Details Component
 * Shows detailed info about where the data came from
 */
export const DataSourceDetails = ({ verification }) => {
  if (!verification || !verification.data_freshness) {
    return null;
  }

  const { data_freshness, api_sources_used = [] } = verification;

  return (
    <div className="data-source-details">
      <h4>Data Source Information</h4>

      <div className="detail-item">
        <label>Freshness:</label>
        <span className={`freshness-value ${data_freshness.cache_status}`}>
          {data_freshness.cache_status === 'fresh' ? '✅ Fresh' : '⚠️ Stale'}
        </span>
      </div>

      {data_freshness.most_recent_evidence_age_hours && (
        <div className="detail-item">
          <label>Most Recent Evidence:</label>
          <span>
            {data_freshness.most_recent_evidence_age_hours < 1
              ? '< 1 hour ago'
              : `${Math.floor(data_freshness.most_recent_evidence_age_hours)} hours ago`}
          </span>
        </div>
      )}

      {api_sources_used && api_sources_used.length > 0 && (
        <div className="detail-item">
          <label>Data Sources:</label>
          <div className="sources-list">
            {api_sources_used.map((source, idx) => (
              <span key={idx} className="source-badge">
                {source === 'google_fact_check' && '✓ Google Fact Check'}
                {source === 'newsapi' && '📰 NewsAPI'}
                {source === 'newsdata' && '🌍 NewsData.io'}
                {source === 'rss' && '📡 RSS Feeds'}
                {source === 'twitter' && '🐦 Twitter'}
                {source === 'reddit' && '📱 Reddit'}
              </span>
            ))}
          </div>
        </div>
      )}

      {data_freshness.data_age_warning && (
        <div className="detail-item warning">
          <span>{data_freshness.data_age_warning}</span>
        </div>
      )}
    </div>
  );
};

/**
 * Trending Topics Data Quality Indicator
 * Shows quality of trending data
 */
export const TrendingDataQuality = ({ topics = [], dataSource = '' }) => {
  if (!topics || topics.length === 0) {
    return (
      <div className="trending-data-quality poor">
        <span>No data available</span>
      </div>
    );
  }

  const isDemo = dataSource === 'demo_fallback';
  const recentTopics = topics.filter(t => {
    if (!t.last_updated) return false;
    const age = Date.now() - new Date(t.last_updated).getTime();
    return age < 60 * 60 * 1000; // Less than 1 hour old
  });

  const quality = isDemo ? 'demo' : recentTopics.length === topics.length ? 'excellent' : 'good';

  return (
    <div className={`trending-data-quality ${quality}`}>
      {quality === 'excellent' && (
        <>
          <span className="quality-icon">✨</span>
          <span className="quality-text">All data fresh (live internet)</span>
        </>
      )}
      {quality === 'good' && (
        <>
          <span className="quality-icon">✓</span>
          <span className="quality-text">
            {recentTopics.length}/{topics.length} topics fresh
          </span>
        </>
      )}
      {quality === 'demo' && (
        <>
          <span className="quality-icon">ℹ️</span>
          <span className="quality-text">Example data (for demonstration)</span>
        </>
      )}
    </div>
  );
};

export default DataFreshness;

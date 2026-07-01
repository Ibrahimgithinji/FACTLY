import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FactlyScoreBadge, FactlyScoreInline, FactlyScoreBar } from '../components/FactlyScoreBadge';
import { RevealOnScroll, StaggerContainer, StaggerItem } from '../components/Animations';
import { API_BASE_URL } from '../utils/constants';
import './TrendingPage.css';

const TRENDING_API = `${API_BASE_URL}/api/verification/trends/`;
const LIVE_API = `${API_BASE_URL}/api/verification/trending/live/`;

const RISK_COLORS = {
  critical: '#dc2626',
  high: '#ef4444',
  medium: '#eab308',
  low: '#22c55e',
};

export default function TrendingPage() {
  const [trends, setTrends] = useState([]);
  const [liveStories, setLiveStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [view, setView] = useState('trends');

  useEffect(() => {
    Promise.all([
      fetch(`${TRENDING_API}?limit=30`).then((r) => r.json()),
      fetch(LIVE_API).then((r) => r.json()).catch(() => ({ trending_stories: [] })),
    ])
      .then(([trendData, liveData]) => {
        setTrends(trendData.results || trendData.trending_topics || []);
        setLiveStories(liveData.trending_stories || []);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  const filteredTrends = filter === 'all'
    ? trends
    : trends.filter((t) => (t.risk_level || '').toLowerCase() === filter);

  if (loading) {
    return (
      <div className="trending-page">
        <div className="trending-skeleton">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="trending-skeleton-card" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="trending-page">
      <header className="trending-page-header">
        <div>
          <span className="section-label">Trending Now</span>
          <h1 className="trending-page-title">Misinformation Tracker</h1>
          <p className="trending-page-subtitle">
            Real-time monitoring of trending claims, risk levels, and verification status
          </p>
        </div>
      </header>

      <div className="trending-view-toggle">
        <button
          className={`view-btn ${view === 'trends' ? 'view-btn--active' : ''}`}
          onClick={() => setView('trends')}
        >
          Risk Analysis
        </button>
        <button
          className={`view-btn ${view === 'live' ? 'view-btn--active' : ''}`}
          onClick={() => setView('live')}
        >
          Live Stories
        </button>
      </div>

      {view === 'trends' && (
        <>
          <div className="trending-filters">
            {['all', 'critical', 'high', 'medium', 'low'].map((level) => (
              <button
                key={level}
                className={`filter-btn ${filter === level ? 'filter-btn--active' : ''}`}
                onClick={() => setFilter(level)}
                style={filter === level && level !== 'all' ? { '--filter-color': RISK_COLORS[level] } : {}}
              >
                {level === 'all' ? 'All' : level.charAt(0).toUpperCase() + level.slice(1)}
                {level !== 'all' && (
                  <span className="filter-count">
                    {trends.filter((t) => (t.risk_level || '').toLowerCase() === level).length}
                  </span>
                )}
              </button>
            ))}
          </div>

          {filteredTrends.length === 0 ? (
            <div className="trending-empty">
              <p>No trends match the selected filter.</p>
            </div>
          ) : (
            <StaggerContainer className="trending-grid" staggerDelay={0.06}>
              {filteredTrends.map((trend) => (
                <StaggerItem key={trend.id || trend.topic}>
                  <motion.div
                    className="trend-card"
                    whileHover={{ y: -4, boxShadow: '0 12px 32px rgba(0,0,0,0.08)' }}
                  >
                    <div className="trend-card__header">
                      <span
                        className="trend-risk-badge"
                        style={{ background: RISK_COLORS[trend.risk_level] || '#6b7280' }}
                      >
                        {(trend.risk_level || 'unknown').toUpperCase()}
                      </span>
                      {trend.factly_score !== undefined && (
                        <FactlyScoreInline score={trend.factly_score} verdict={trend.verification_status} />
                      )}
                    </div>
                    <h3 className="trend-card__title">{trend.topic}</h3>
                    {trend.keywords && trend.keywords.length > 0 && (
                      <div className="trend-card__keywords">
                        {trend.keywords.slice(0, 4).map((kw, i) => (
                          <span key={i} className="trend-keyword">{kw}</span>
                        ))}
                      </div>
                    )}
                    <div className="trend-card__stats">
                      {trend.engagement_score !== undefined && (
                        <div className="trend-stat">
                          <span className="trend-stat__label">Engagement</span>
                          <span className="trend-stat__value">{trend.engagement_score}</span>
                        </div>
                      )}
                      {trend.misinformation_risk_score !== undefined && (
                        <div className="trend-stat">
                          <span className="trend-stat__label">Risk Score</span>
                          <span className="trend-stat__value" style={{ color: RISK_COLORS[trend.risk_level] || '#6b7280' }}>
                            {trend.misinformation_risk_score}
                          </span>
                        </div>
                      )}
                      {trend.verification_status && (
                        <div className="trend-stat">
                          <span className="trend-stat__label">Status</span>
                          <span className="trend-stat__value">{trend.verification_status}</span>
                        </div>
                      )}
                    </div>
                    {trend.primary_region && (
                      <div className="trend-card__region">{trend.primary_region}</div>
                    )}
                  </motion.div>
                </StaggerItem>
              ))}
            </StaggerContainer>
          )}
        </>
      )}

      {view === 'live' && (
        <div className="live-stories-grid">
          {liveStories.length === 0 ? (
            <div className="trending-empty">
              <p>No live stories available right now. Check back soon.</p>
            </div>
          ) : (
            liveStories.map((story, i) => (
              <RevealOnScroll key={i} delay={i * 0.05}>
                <motion.a
                  href={story.url}
                  target="_blank"
                  rel="noreferrer"
                  className="live-story-card"
                  whileHover={{ y: -4 }}
                >
                  <div className="live-story-card__source">{story.source || story.api_source || 'Unknown'}</div>
                  <h3 className="live-story-card__title">{story.title}</h3>
                  {story.description && (
                    <p className="live-story-card__desc">{story.description.substring(0, 140)}...</p>
                  )}
                  {story.publishedAt && (
                    <span className="live-story-card__date">
                      {new Date(story.publishedAt).toLocaleString()}
                    </span>
                  )}
                </motion.a>
              </RevealOnScroll>
            ))
          )}
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FactlyScoreBadge, FactlyScoreInline, FactlyScoreBar } from '../components/FactlyScoreBadge';
import { RevealOnScroll, CountUp } from '../components/Animations';
import { API_BASE_URL } from '../utils/constants';
import './DailyBriefingPage.css';

const AGENT_API = `${API_BASE_URL}/api/agent`;

function scoreColor(score) {
  if (score >= 70) return '#22c55e';
  if (score >= 40) return '#eab308';
  return '#ef4444';
}

export default function DailyBriefingPage() {
  const [digest, setDigest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hours, setHours] = useState(24);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`${AGENT_API}/digest/?hours=${hours}`)
      .then((r) => {
        if (!r.ok) throw new Error('Failed to fetch digest');
        return r.json();
      })
      .then((d) => {
        setDigest(d);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [hours]);

  if (loading) {
    return (
      <div className="briefing-page">
        <div className="briefing-skeleton">
          <div className="skeleton-pulse" style={{ height: 40, width: '60%', marginBottom: 8 }} />
          <div className="skeleton-pulse" style={{ height: 20, width: '40%', marginBottom: 32 }} />
          <div className="briefing-summary">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="skeleton-pulse" style={{ height: 80, borderRadius: 12 }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="briefing-page">
        <div className="briefing-error">
          <h2>Could not load briefing</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="briefing-page">
      <header className="briefing-header">
        <div className="briefing-header__left">
          <span className="section-label">Daily Briefing</span>
          <h1 className="briefing-title">Verified News Digest</h1>
          <p className="briefing-subtitle">
            {digest?.date || new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <div className="briefing-time-toggle">
          {[{ label: '24h', value: 24 }, { label: '48h', value: 48 }, { label: '7 days', value: 168 }].map(
            ({ label, value }) => (
              <button
                key={value}
                className={`time-btn ${hours === value ? 'time-btn--active' : ''}`}
                onClick={() => setHours(value)}
              >
                {label}
              </button>
            )
          )}
        </div>
      </header>

      {digest?.verification_summary && (
        <RevealOnScroll>
          <div className="briefing-summary">
            <motion.div className="summary-card" whileHover={{ y: -4 }}>
              <span className="summary-num"><CountUp target={digest.verification_summary.total_stories || 0} /></span>
              <span className="summary-label">Stories Analyzed</span>
            </motion.div>
            <motion.div className="summary-card summary-card--green" whileHover={{ y: -4 }}>
              <span className="summary-num" style={{ color: '#22c55e' }}>
                <CountUp target={digest.verification_summary.verified_true || 0} />
              </span>
              <span className="summary-label">Verified True</span>
            </motion.div>
            <motion.div className="summary-card summary-card--red" whileHover={{ y: -4 }}>
              <span className="summary-num" style={{ color: '#ef4444' }}>
                <CountUp target={digest.verification_summary.suspicious || 0} />
              </span>
              <span className="summary-label">Suspicious</span>
            </motion.div>
            <motion.div className="summary-card summary-card--blue" whileHover={{ y: -4 }}>
              <span className="summary-num">
                <CountUp target={digest.verification_summary.trust_score || 0} suffix="%" />
              </span>
              <span className="summary-label">Trust Score</span>
            </motion.div>
          </div>
        </RevealOnScroll>
      )}

      {digest?.headline && (
        <RevealOnScroll delay={0.1}>
          <section className="briefing-headline">
            <div className="briefing-headline__badge">Top Story</div>
            <h2 className="briefing-headline__title">{digest.headline.title}</h2>
            <div className="briefing-headline__meta">
              <span className="headline-source">{digest.headline.source_name || digest.headline.source || 'Unknown'}</span>
              <FactlyScoreInline
                score={digest.headline.credibility_score}
                verdict={digest.headline.verdict}
              />
            </div>
            <FactlyScoreBar score={digest.headline.credibility_score} verdict={digest.headline.verdict} showScore={false} />
          </section>
        </RevealOnScroll>
      )}

      {digest?.top_stories && digest.top_stories.length > 0 && (
        <RevealOnScroll delay={0.15}>
          <section className="briefing-stories">
            <h3 className="briefing-section-title">Top Stories</h3>
            <div className="stories-grid">
              {digest.top_stories.slice(0, 12).map((story, i) => (
                <motion.div
                  key={i}
                  className="story-card-lg"
                  whileHover={{ y: -3, boxShadow: '0 8px 24px rgba(0,0,0,0.08)' }}
                >
                  <div className="story-card-lg__rank">{i + 1}</div>
                  <div className="story-card-lg__content">
                    <div className="story-card-lg__title">{story.title}</div>
                    <div className="story-card-lg__meta">
                      <span className="story-source">{story.source_name || story.source || 'Unknown'}</span>
                      <FactlyScoreInline score={story.credibility_score} verdict={story.verdict} />
                    </div>
                    <FactlyScoreBar score={story.credibility_score} verdict={story.verdict} showScore={false} />
                  </div>
                </motion.div>
              ))}
            </div>
          </section>
        </RevealOnScroll>
      )}

      {digest?.categories && Object.keys(digest.categories).length > 0 && (
        <RevealOnScroll delay={0.2}>
          <section className="briefing-categories">
            <h3 className="briefing-section-title">By Category</h3>
            <div className="categories-grid-lg">
              {Object.entries(digest.categories).map(([cat, items]) => (
                <div key={cat} className="category-block">
                  <h4 className="category-block__title">{cat.charAt(0).toUpperCase() + cat.slice(1)}</h4>
                  {items.map((item, i) => (
                    <div key={i} className="category-block__item">
                      <span className="category-block__item-title">{item.title}</span>
                      <FactlyScoreInline score={item.credibility_score} verdict={item.verdict} />
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </section>
        </RevealOnScroll>
      )}

      {digest?.sources_checked && digest.sources_checked.length > 0 && (
        <RevealOnScroll delay={0.25}>
          <section className="briefing-sources">
            <h3 className="briefing-section-title">Sources Checked</h3>
            <div className="sources-list">
              {digest.sources_checked.map((src, i) => (
                <span key={i} className="source-chip">{src}</span>
              ))}
            </div>
          </section>
        </RevealOnScroll>
      )}
    </div>
  );
}

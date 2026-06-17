import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import './TrendingClaims.css';

const CLAIMS_POLL_MS = 10 * 60 * 1000;

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

export default function TrendingClaims() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const pollRef = useRef(null);
  const mountedRef = useRef(false);

  const fetchClaims = useCallback(async () => {
    try {
      const r = await fetch('/api/verification/claims/');
      if (!mountedRef.current) return;
      const data = r.ok ? await r.json() : { claims: [] };
      setClaims(data.claims || []);
      setLastUpdated(new Date().toISOString());
    } catch {
      if (!mountedRef.current) return;
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    fetchClaims();

    pollRef.current = setInterval(fetchClaims, CLAIMS_POLL_MS);

    const handleVisibility = () => {
      if (document.visibilityState === 'visible') fetchClaims();
    };
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      mountedRef.current = false;
      clearInterval(pollRef.current);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, [fetchClaims]);

  if (loading) return null;
  if (claims.length === 0) return null;

  const scoreColors = {};
  claims.forEach(c => {
    const score = c.score;
    let color;
    if (score >= 80) color = '#22c55e';
    else if (score >= 60) color = '#eab308';
    else if (score >= 40) color = '#f97316';
    else color = '#ef4444';
    scoreColors[c.id] = color;
  });

  return (
    <section className="trending-claims">
      <div className="trending-claims__header">
        <div>
          <h2 className="trending-claims__title">Trending Claims</h2>
          <p className="trending-claims__subtitle">Recent fact-check verifications</p>
        </div>
        <div className="trending-claims__actions">
          {lastUpdated && (
            <span className="claims-timestamp">
              <span className="freshness-dot" />
              {formatRelativeTime(lastUpdated)}
            </span>
          )}
          <button className="refresh-button" onClick={fetchClaims}>
            Refresh
          </button>
          <Link to="/verify" className="trending-claims__cta">Verify a Claim</Link>
        </div>
      </div>

      <div className="trending-claims__list">
        {claims.map((claim) => (
          <div key={claim.id} className="trending-claims__item">
            <div
              className="trending-claims__score"
              style={{
                background: scoreColors[claim.id] + '20',
                color: scoreColors[claim.id],
              }}
            >
              {claim.score}
            </div>
            <div className="trending-claims__content">
              <p className="trending-claims__text">{claim.claim}</p>
              <div className="trending-claims__meta">
                <span
                  className="trending-claims__classification"
                  style={{
                    background: scoreColors[claim.id] + '20',
                    color: scoreColors[claim.id],
                  }}
                >
                  {claim.classification}
                </span>
                <span className="trending-claims__date">
                  {new Date(claim.verified_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

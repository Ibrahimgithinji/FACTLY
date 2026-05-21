import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './TrendingClaims.css';

export default function TrendingClaims() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/verification/claims/')
      .then((r) => r.ok ? r.json() : { claims: [] })
      .then((data) => setClaims(data.claims || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

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
        <Link to="/verify" className="trending-claims__cta">Verify a Claim</Link>
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

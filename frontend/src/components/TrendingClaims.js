import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function scoreColor(score) {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#eab308';
  if (score >= 40) return '#f97316';
  return '#ef4444';
}

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

  return (
    <section style={{
      marginTop: 48, padding: '32px 24px',
      background: 'var(--card-bg)',
      borderRadius: 16,
      border: '1px solid var(--border)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 20, color: 'var(--text)' }}>Trending Claims</h2>
          <p style={{ margin: '4px 0 0', fontSize: 13, color: 'var(--text-secondary)' }}>
            Recent fact-check verifications
          </p>
        </div>
        <Link
          to="/verify"
          style={{
            padding: '8px 16px', background: 'var(--accent)', color: '#fff',
            borderRadius: 8, textDecoration: 'none', fontSize: 13, fontWeight: 600,
          }}
        >
          Verify a Claim
        </Link>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {claims.map((claim) => (
          <div key={claim.id} style={{
            display: 'flex', alignItems: 'center', gap: 16,
            padding: '12px 16px',
            background: 'var(--bg-secondary)',
            borderRadius: 10,
          }}>
            <div style={{
              width: 48, height: 48, borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: scoreColor(claim.score) + '20',
              color: scoreColor(claim.score),
              fontWeight: 700, fontSize: 14, flexShrink: 0,
            }}>
              {claim.score}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{ margin: 0, fontSize: 13, color: 'var(--text)', lineHeight: 1.4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {claim.claim}
              </p>
              <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                <span style={{
                  fontSize: 11, padding: '2px 6px', borderRadius: 4,
                  background: scoreColor(claim.score) + '20',
                  color: scoreColor(claim.score),
                  fontWeight: 600, textTransform: 'capitalize',
                }}>
                  {claim.classification}
                </span>
                <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
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

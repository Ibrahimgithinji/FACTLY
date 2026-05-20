import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/content/analytics/dashboard/', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error('Unauthorized');
        return r.json();
      })
      .then((data) => { setStats(data); setLoading(false); })
      .catch((err) => { setError(err.message); setLoading(false); });
  }, []);

  if (!user) return <p style={{ padding: 40, color: 'var(--text-secondary)' }}>Please log in.</p>;
  if (loading) return <p style={{ padding: 40, color: 'var(--text-secondary)' }}>Loading...</p>;
  if (error) return <p style={{ padding: 40, color: 'red' }}>{error}</p>;
  if (!stats) return null;

  const card = (title, value, sub) => (
    <div style={{
      background: 'var(--card-bg)',
      border: '1px solid var(--border)',
      borderRadius: 12,
      padding: '16px 20px',
      flex: '1 1 180px',
    }}>
      <p style={{ margin: 0, fontSize: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 1 }}>{title}</p>
      <p style={{ margin: '8px 0 0', fontSize: 28, fontWeight: 700, color: 'var(--text)' }}>{value}</p>
      {sub && <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--text-secondary)' }}>{sub}</p>}
    </div>
  );

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ fontSize: 24, color: 'var(--text)', marginBottom: 4 }}>Dashboard</h1>
      <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 32 }}>
        Welcome back, {user.name}
      </p>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, marginBottom: 32 }}>
        {card('Articles', stats.articles.published, `${stats.articles.total} total, ${stats.articles.categories} categories`)}
        {card('Page Views', stats.page_views.total.toLocaleString(), `${stats.page_views.today} today, ${stats.page_views.this_week} this week`)}
        {card('Subscribers', stats.subscribers.total, `${stats.subscribers.today} new today`)}
        {card('Push Subs', stats.push_subscriptions)}
        {card('Bookmarks', stats.bookmarks)}
        {card('Comments', stats.comments)}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border)',
          borderRadius: 12,
          padding: 20,
        }}>
          <h2 style={{ fontSize: 16, color: 'var(--text)', margin: '0 0 16px' }}>Most Viewed (30 days)</h2>
          {stats.most_viewed_articles.length === 0 ? (
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>No data yet</p>
          ) : (
            <ol style={{ margin: 0, paddingLeft: 20 }}>
              {stats.most_viewed_articles.map((a) => (
                <li key={a.id} style={{ marginBottom: 8, fontSize: 13 }}>
                  <Link to={`/article/${a.slug}`} style={{ color: 'var(--link)', textDecoration: 'none' }}>
                    {a.title}
                  </Link>
                  <span style={{ color: 'var(--text-secondary)', marginLeft: 8 }}>{a.views} views</span>
                </li>
              ))}
            </ol>
          )}
        </div>

        <div style={{
          background: 'var(--card-bg)',
          border: '1px solid var(--border)',
          borderRadius: 12,
          padding: 20,
        }}>
          <h2 style={{ fontSize: 16, color: 'var(--text)', margin: '0 0 16px' }}>Recent Articles</h2>
          {stats.recent_articles.map((a) => (
            <div key={a.id} style={{ marginBottom: 10, fontSize: 13 }}>
              <Link to={`/article/${a.slug}`} style={{ color: 'var(--link)', textDecoration: 'none' }}>
                {a.title}
              </Link>
              <p style={{ margin: '2px 0 0', fontSize: 11, color: 'var(--text-secondary)' }}>
                {new Date(a.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

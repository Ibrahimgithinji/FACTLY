import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import SEOMeta from '../components/SEOMeta';
import { API_ENDPOINTS } from '../utils/api';
import './NotFoundPage.css';

export default function NotFoundPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [trending, setTrending] = useState([]);

  useEffect(() => {
    const controller = new AbortController();
    fetch(API_ENDPOINTS.TRENDING, { signal: controller.signal })
      .then(r => r.ok ? r.json() : [])
      .then(data => {
        const list = data.results || data.claims || data.trending_topics || [];
        setTrending(list.slice(0, 4));
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        console.warn('Failed to load trending data for 404 page');
      });
    return () => controller.abort();
  }, []);

  const handleSearch = e => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/?search=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <div className="not-found">
      <SEOMeta title="Page Not Found" />

      <div className="not-found__inner">
        <div className="not-found__code">404</div>
        <h1 className="not-found__title">Lost in the void?</h1>
        <p className="not-found__desc">
          The page you're looking for doesn't exist, was moved, or never existed in the first place.
          Let's get you back on track.
        </p>

        <form className="not-found__search" onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search articles..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="not-found__input"
            autoFocus
          />
          <button type="submit" className="not-found__search-btn">Search</button>
        </form>

        <div className="not-found__links">
          <Link to="/" className="not-found__btn not-found__btn--primary">Go Home</Link>
          <Link to="/verify" className="not-found__btn not-found__btn--secondary">Verify a Claim</Link>
        </div>

        {trending.length > 0 && (
          <div className="not-found__trending">
            <h3 className="not-found__trending-title">Trending Now</h3>
            <div className="not-found__trending-list">
              {trending.map(a => (
                <Link key={a.id} to={`/article/${a.slug}`} className="not-found__trending-item">
                  {a.title}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

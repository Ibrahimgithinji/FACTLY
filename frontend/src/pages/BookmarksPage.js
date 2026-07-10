import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ArticleCard from '../components/ArticleCard';
import { ArticleCardSkeleton } from '../components/Skeleton';
import { CONTENT_ENDPOINTS } from '../utils/api';
import SEOMeta from '../components/SEOMeta';
import './BookmarksPage.css';

const fetchOpts = { credentials: 'include' };

export default function BookmarksPage() {
  const { isAuthenticated } = useAuth();
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const abortRef = useRef(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    if (abortRef.current) abortRef.current.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    (async () => {
      try {
        const res = await fetch(CONTENT_ENDPOINTS.BOOKMARKS, { ...fetchOpts, signal: ac.signal });
        if (res.ok) {
          const data = await res.json();
          if (ac.signal.aborted) return;
          setArticles(data.results || data);
          setFetchError(null);
        } else {
          setFetchError('Failed to load bookmarks.');
        }
      } catch (e) {
        if (e.name === 'AbortError') return;
        console.warn('Failed to load bookmarks:', e);
        setFetchError('Failed to load bookmarks.');
      } finally {
        if (!ac.signal.aborted) {
          setLoading(false);
        }
      }
    })();
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="bookmarks-page">
        <SEOMeta title="Saved Articles" noindex={true} />
        <div className="bookmarks-page__empty">
          <h2>Saved Articles</h2>
          <p>Sign in to save articles for later.</p>
          <Link to="/login" className="bookmarks-page__btn">Sign In</Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bookmarks-page">
        <SEOMeta title="Saved Articles" noindex={true} />
        <h1 className="bookmarks-page__title">Saved Articles</h1>
        <div className="bookmarks-page__grid">
          {[...Array(4)].map((_, i) => <ArticleCardSkeleton key={i} />)}
        </div>
      </div>
    );
  }

  return (
    <div className="bookmarks-page">
      <SEOMeta title="Saved Articles" noindex={true} />
      <h1 className="bookmarks-page__title">Saved Articles ({articles.length})</h1>
      {fetchError ? (
        <div className="bookmarks-page__empty">
          <p>{fetchError}</p>
          <button onClick={() => window.location.reload()} className="bookmarks-page__btn">Try Again</button>
        </div>
      ) : articles.length === 0 ? (
        <div className="bookmarks-page__empty">
          <p>You haven't saved any articles yet.</p>
          <Link to="/" className="bookmarks-page__btn">Browse Articles</Link>
        </div>
      ) : (
        <div className="bookmarks-page__grid">
          {articles.map(a => <ArticleCard key={a.id} article={a} />)}
        </div>
      )}
    </div>
  );
}

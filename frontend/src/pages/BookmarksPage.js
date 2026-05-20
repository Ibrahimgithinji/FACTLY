import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ArticleCard from '../components/ArticleCard';
import { ArticleCardSkeleton } from '../components/Skeleton';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './BookmarksPage.css';

export default function BookmarksPage() {
  const { isAuthenticated, getValidAccessToken } = useAuth();
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    (async () => {
      const token = await getValidAccessToken();
      if (!token) return;
      try {
        const res = await fetch(CONTENT_ENDPOINTS.BOOKMARKS, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setArticles(data.results || data);
        }
      } catch {} finally {
        setLoading(false);
      }
    })();
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="bookmarks-page">
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
        <h1 className="bookmarks-page__title">Saved Articles</h1>
        <div className="bookmarks-page__grid">
          {[...Array(4)].map((_, i) => <ArticleCardSkeleton key={i} />)}
        </div>
      </div>
    );
  }

  return (
    <div className="bookmarks-page">
      <h1 className="bookmarks-page__title">Saved Articles ({articles.length})</h1>
      {articles.length === 0 ? (
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

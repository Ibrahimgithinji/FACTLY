import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './BookmarkButton.css';

export default function BookmarkButton({ articleId }) {
  const { isAuthenticated, getValidAccessToken } = useAuth();
  const [isBookmarked, setIsBookmarked] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;
    (async () => {
      const token = await getValidAccessToken();
      if (!token) return;
      fetch(CONTENT_ENDPOINTS.BOOKMARKS, {
        headers: { 'Authorization': `Bearer ${token}` },
      })
        .then(r => r.json())
        .then(data => {
          const ids = (data.results || data).map(a => a.id);
          setIsBookmarked(ids.includes(articleId));
        })
        .catch(() => {});
    })();
  }, [isAuthenticated, articleId, getValidAccessToken]);

  const toggle = async () => {
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }
    const token = await getValidAccessToken();
    if (!token) return;
    const method = isBookmarked ? 'DELETE' : 'POST';
    try {
      const res = await fetch(CONTENT_ENDPOINTS.BOOKMARK(articleId), {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      if (res.ok) {
        setIsBookmarked(!isBookmarked);
      }
    } catch {}
  };

  return (
    <button
      onClick={toggle}
      className={`bookmark-btn ${isBookmarked ? 'bookmark-btn--active' : ''}`}
      aria-label={isBookmarked ? 'Remove bookmark' : 'Save article'}
      title={isBookmarked ? 'Saved' : 'Save for later'}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill={isBookmarked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
      </svg>
    </button>
  );
}

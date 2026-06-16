import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './BookmarkButton.css';

const fetchOpts = { credentials: 'include' };

export default function BookmarkButton({ articleId }) {
  const { isAuthenticated } = useAuth();
  const [isBookmarked, setIsBookmarked] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) return;
    fetch(CONTENT_ENDPOINTS.BOOKMARKS, fetchOpts)
      .then(r => r.json())
      .then(data => {
        const ids = (data.results || data).map(a => a.id);
        setIsBookmarked(ids.includes(articleId));
      })
      .catch(() => {});
  }, [isAuthenticated, articleId]);

  const toggle = useCallback(async () => {
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }
    const method = isBookmarked ? 'DELETE' : 'POST';
    try {
      const res = await fetch(CONTENT_ENDPOINTS.BOOKMARK(articleId), {
        ...fetchOpts,
        method,
        headers: { 'Content-Type': 'application/json' },
      });
      if (res.ok) {
        setIsBookmarked(!isBookmarked);
      }
    } catch {}
  }, [isAuthenticated, isBookmarked, articleId]);

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

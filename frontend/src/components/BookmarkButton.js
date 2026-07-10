import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './BookmarkButton.css';

const fetchOpts = { credentials: 'include' };

export default function BookmarkButton({ articleId }) {
  const { isAuthenticated } = useAuth();
  const [isBookmarked, setIsBookmarked] = useState(false);
  const abortRef = useRef(null);
  const pendingRef = useRef(false);

  useEffect(() => {
    if (!isAuthenticated) return;
    if (abortRef.current) abortRef.current.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    fetch(CONTENT_ENDPOINTS.BOOKMARKS, { ...fetchOpts, signal: ac.signal })
      .then(r => r.json())
      .then(data => {
        if (ac.signal.aborted) return;
        const ids = (data.results || data).map(a => a.id);
        setIsBookmarked(ids.includes(articleId));
      })
      .catch(() => {
        if (ac.signal.aborted) return;
        console.warn('Failed to load bookmark state');
      });
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, [isAuthenticated, articleId]);

  const toggle = useCallback(async () => {
    if (pendingRef.current) return;
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }
    pendingRef.current = true;
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
    } catch (e) { console.warn('Failed to toggle bookmark:', e); }
    finally { pendingRef.current = false; }
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

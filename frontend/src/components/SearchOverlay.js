import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './SearchOverlay.css';

export default function SearchOverlay({ isOpen, onClose }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [isOpen, onClose]);

  const search = useCallback(async (q) => {
    if (!q.trim()) {
      setResults([]);
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${CONTENT_ENDPOINTS.SEARCH}?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      setResults(data.results || []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => search(val), 300);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    search(query);
  };

  if (!isOpen) return null;

  return (
    <div className="search-overlay" onClick={onClose}>
      <div className="search-overlay__content" onClick={e => e.stopPropagation()}>
        <form onSubmit={handleSubmit} className="search-overlay__form">
          <input
            ref={inputRef}
            type="text"
            className="search-overlay__input"
            placeholder="Search articles…"
            value={query}
            onChange={handleChange}
          />
          <button type="button" className="search-overlay__close" onClick={onClose} aria-label="Close search">
            ✕
          </button>
        </form>

        <div className="search-overlay__results">
          {loading && <div className="search-overlay__loading">Searching...</div>}
          {!loading && results.length === 0 && query && (
            <div className="search-overlay__empty">No articles found</div>
          )}
          {results.length > 0 && (
            <div className="search-overlay__list">
              {results.map(article => (
                <Link
                  key={article.id}
                  to={`/article/${article.slug}`}
                  className="search-overlay__item"
                  onClick={onClose}
                >
                  {article.featured_image && (
                    <img src={article.featured_image} alt="" className="search-overlay__item-img" loading="lazy" />
                  )}
                  <div className="search-overlay__item-info">
                    <span className="search-overlay__item-title">{article.title}</span>
                    <span className="search-overlay__item-meta">
                      {article.category?.name} · {article.published_at ? new Date(article.published_at).toLocaleDateString() : ''}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

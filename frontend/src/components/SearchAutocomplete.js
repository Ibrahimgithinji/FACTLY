import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

export default function SearchAutocomplete({ placeholder = 'Search articles...' }) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [show, setShow] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef(null);
  const wrapperRef = useRef(null);
  const debounceRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShow(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchSuggestions = async (q) => {
    if (q.length < 2) {
      setSuggestions([]);
      return;
    }
    try {
      const res = await fetch(`/api/content/search/suggestions/?q=${encodeURIComponent(q)}`);
      if (res.ok) {
        const data = await res.json();
        setSuggestions(data.suggestions || []);
        setShow(true);
      }
    } catch (err) {
      // silent
    }
  };

  const handleChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    setSelectedIndex(-1);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => fetchSuggestions(val), 200);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, -1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && suggestions[selectedIndex]) {
        navigate(`/article/${suggestions[selectedIndex].slug}`);
        setShow(false);
        setQuery('');
      } else if (query.trim()) {
        navigate(`/search?q=${encodeURIComponent(query.trim())}`);
        setShow(false);
        setQuery('');
      }
    } else if (e.key === 'Escape') {
      setShow(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
      setShow(false);
      setQuery('');
    }
  };

  return (
    <div ref={wrapperRef} style={{ position: 'relative', width: '100%' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', width: '100%' }}>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={() => suggestions.length > 0 && setShow(true)}
          placeholder={placeholder}
          aria-label="Search articles"
          autoComplete="off"
          style={{
            width: '100%',
            padding: '10px 14px',
            borderRadius: 8,
            border: '1px solid var(--border)',
            background: 'var(--bg-secondary)',
            color: 'var(--text)',
            fontSize: 14,
            outline: 'none',
          }}
        />
        <button
          type="submit"
          style={{
            padding: '10px 16px',
            background: 'var(--accent)',
            color: '#fff',
            border: 'none',
            borderRadius: '0 8px 8px 0',
            cursor: 'pointer',
            fontWeight: 600,
            fontSize: 14,
            marginLeft: -1,
          }}
        >
          Search
        </button>
      </form>
      {show && suggestions.length > 0 && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          right: 0,
          background: 'var(--card-bg)',
          border: '1px solid var(--border)',
          borderRadius: 8,
          marginTop: 4,
          boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
          zIndex: 100,
          maxHeight: 300,
          overflowY: 'auto',
        }}>
          {suggestions.map((s, i) => (
            <button
              key={s.id}
              onClick={() => {
                navigate(`/article/${s.slug}`);
                setShow(false);
                setQuery('');
              }}
              onMouseEnter={() => setSelectedIndex(i)}
              style={{
                display: 'block',
                width: '100%',
                padding: '10px 14px',
                textAlign: 'left',
                background: i === selectedIndex ? 'var(--bg-secondary)' : 'transparent',
                border: 'none',
                borderBottom: '1px solid var(--border)',
                cursor: 'pointer',
                color: 'var(--text)',
                fontSize: 13,
              }}
            >
              <span style={{ fontWeight: 500 }}>{s.title}</span>
              {s.category && (
                <span style={{
                  marginLeft: 8, fontSize: 11, color: 'var(--accent)',
                  background: 'var(--bg-secondary)', padding: '2px 6px',
                  borderRadius: 4, textTransform: 'capitalize',
                }}>
                  {s.category}
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

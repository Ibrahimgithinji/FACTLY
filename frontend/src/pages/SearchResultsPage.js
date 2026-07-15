import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import ArticleCard from '../components/ArticleCard';
import { ArticleCardSkeleton } from '../components/Skeleton';
import SEOMeta from '../components/SEOMeta';
import { API_BASE_URL } from '../utils/constants';
import './CategoryPage.css';

export default function SearchResultsPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const [results, setResults] = useState([]);
  const [count, setCount] = useState(0);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_BASE_URL}/api/content/categories/`, { signal: controller.signal })
      .then((r) => r.ok ? r.json() : [])
      .then(setCategories)
      .catch((err) => {
        if (err.name === 'AbortError') return;
        console.warn('Failed to load categories for search filters');
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    async function doSearch() {
      if (!query) { setResults([]); setCount(0); setLoading(false); return; }
      setLoading(true);
      try {
        let url = `${API_BASE_URL}/api/content/search/?q=${encodeURIComponent(query)}`;
        if (categoryFilter) url += `&category=${categoryFilter}`;
        if (dateFrom) url += `&date_from=${dateFrom}`;
        if (dateTo) url += `&date_to=${dateTo}`;
        const res = await fetch(url, { signal: controller.signal });
        if (res.ok) {
          const data = await res.json();
          setResults(data.results || []);
          setCount(data.count || 0);
        }
      } catch (err) {
        if (err.name === 'AbortError') return;
        console.error('Search failed:', err);
      } finally {
        setLoading(false);
      }
    }
    doSearch();
    return () => controller.abort();
  }, [query, categoryFilter, dateFrom, dateTo]);

  return (
    <div className="category-page">
      <SEOMeta title="Search Results" description="Search verified news articles and fact-checks on FACTLY." />
      <div className="category-hero" style={{ padding: '40px 20px' }}>
        <div className="category-hero-content">
          <h1>Search Results</h1>
          <p style={{ fontSize: 16, color: 'var(--text-secondary)', marginTop: 8 }}>
            {query ? `"${query}" — ${count} article${count !== 1 ? 's' : ''} found` : 'Enter a search term above'}
          </p>
        </div>
      </div>

      <div className="category-content">
        {query && (
          <div style={{
            display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24,
            padding: 16, background: 'var(--card-bg)', borderRadius: 12, border: '1px solid var(--border)',
            alignItems: 'center',
          }}>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 600 }} id="search-filters-label">Filters:</span>
            <select
              aria-labelledby="search-filters-label"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              style={{
                padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)',
                background: 'var(--bg-secondary)', color: 'var(--text)', fontSize: 13,
              }}
            >
              <option value="">All Categories</option>
              {categories.map((c) => (
                <option key={c.id} value={c.slug}>{c.name}</option>
              ))}
            </select>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              aria-label="Date from"
              placeholder="From"
              style={{
                padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)',
                background: 'var(--bg-secondary)', color: 'var(--text)', fontSize: 13,
              }}
            />
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              aria-label="Date to"
              placeholder="To"
              style={{
                padding: '8px 12px', borderRadius: 8, border: '1px solid var(--border)',
                background: 'var(--bg-secondary)', color: 'var(--text)', fontSize: 13,
              }}
            />
            {(categoryFilter || dateFrom || dateTo) && (
              <button
                onClick={() => { setCategoryFilter(''); setDateFrom(''); setDateTo(''); }}
                style={{
                  padding: '8px 12px', background: 'none', border: '1px solid var(--border)',
                  borderRadius: 8, color: 'var(--text-secondary)', cursor: 'pointer', fontSize: 13,
                }}
              >
                Clear
              </button>
            )}
          </div>
        )}

        {loading ? (
          <div className="article-grid">
            {[1, 2, 3, 4, 5, 6].map((i) => <ArticleCardSkeleton key={i} />)}
          </div>
        ) : results.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <p style={{ fontSize: 18, color: 'var(--text-secondary)', marginBottom: 8 }}>No results found</p>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)' }}>
              Try different keywords or{' '}
              <Link to="/" style={{ color: 'var(--accent)' }}>browse articles</Link>
            </p>
          </div>
        ) : (
          <div className="article-grid">
            {results.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

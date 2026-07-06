import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import ArticleCard from '../components/ArticleCard';
import { CategoryPageSkeleton } from '../components/Skeleton';
import SEOMeta from '../components/SEOMeta';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './CategoryPage.css';

export default function StartupsPage() {
  const [articles, setArticles] = useState([]);
  const [spotlight, setSpotlight] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [listRes, featuredRes] = await Promise.all([
          fetch(`${CONTENT_ENDPOINTS.ARTICLES}?category=startups&page_size=50`),
          fetch(`${CONTENT_ENDPOINTS.ARTICLES}?category=startups&featured=true&page_size=1`),
        ]);
        if (listRes.ok) {
          const data = await listRes.json();
          setArticles(data.results || []);
        }
        if (featuredRes.ok) {
          const data = await featuredRes.json();
          if (data.results && data.results.length > 0) {
            setSpotlight(data.results[0]);
          }
        }
      } catch (err) {
        console.error('Failed to load startups:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Deduplicate: exclude the spotlight article from the grid
  const gridArticles = useMemo(() => {
    if (!spotlight) return articles;
    return articles.filter((a) => a.id !== spotlight.id);
  }, [articles, spotlight]);

  if (loading) return <CategoryPageSkeleton />;

  return (
    <div className="category-page">
      <SEOMeta title="Tech Startups" description="Discover promising tech startups. FACTLY tracks innovation, funding rounds, and startup launches across Africa and globally." />
      <div className="category-hero">
        <div className="category-hero-content">
          <div className="category-icon" style={{ fontSize: 32, marginBottom: 8 }}>🚀</div>
          <h1>Startup Spotlight</h1>
          <p>Discover innovative startups, founder stories, and the ideas shaping tomorrow's tech landscape.</p>
        </div>
      </div>

      <div className="category-content">
        {spotlight && (
          <div className="featured-section" style={{
            marginBottom: 40, padding: 24, background: 'var(--card-bg)',
            borderRadius: 16, border: '1px solid var(--border)',
          }}>
            <h2 style={{ fontSize: 14, textTransform: 'uppercase', letterSpacing: 1, color: 'var(--accent)', marginBottom: 16 }}>
              Featured Startup
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'center' }}>
              <div>
                <h3 style={{ fontSize: 24, margin: '0 0 8px', color: 'var(--text)' }}>{spotlight.title}</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.6 }}>{spotlight.excerpt}</p>
                <Link
                  to={`/article/${spotlight.slug}`}
                  style={{ display: 'inline-block', marginTop: 12, padding: '10px 20px', background: 'var(--accent)', color: '#fff', borderRadius: 8, textDecoration: 'none', fontWeight: 600, fontSize: 14 }}
                >
                  Read Story →
                </Link>
              </div>
              {spotlight.featured_image && (
                <img
                  src={spotlight.featured_image}
                  alt={spotlight.title}
                  style={{ width: '100%', maxHeight: 280, objectFit: 'cover', borderRadius: 12 }}
                  onError={(e) => { e.target.style.display = 'none' }}
                />
              )}
            </div>
          </div>
        )}

        <div className="section-header">
          <h2>All Startup Stories</h2>
                          <span className="article-count">{gridArticles.length} articles</span>
        </div>

        {gridArticles.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: 40 }}>
            No startup stories yet. Check back soon!
          </p>
        ) : (
          <div className="article-grid">
            {gridArticles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

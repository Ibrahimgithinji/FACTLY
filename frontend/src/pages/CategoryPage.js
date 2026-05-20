import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ArticleCard from '../components/ArticleCard';
import Sidebar from '../components/Sidebar';
import { ArticleCardSkeleton, SidebarSkeleton } from '../components/Skeleton';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './CategoryPage.css';

export default function CategoryPage() {
  const { slug } = useParams();
  const [category, setCategory] = useState(null);
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [catRes, artRes] = await Promise.all([
          fetch(CONTENT_ENDPOINTS.CATEGORIES),
          fetch(`${CONTENT_ENDPOINTS.ARTICLES}?category=${slug}&page=${page}`),
        ]);
        const catData = await catRes.json();
        const artData = await artRes.json();
        setCategories(catData);
        setArticles(artData.results || artData);
        setTotal(artData.count || (artData.results ? artData.results.length : artData.length));
        setTotalPages(artData.total_pages || Math.ceil((artData.count || 0) / 12) || 1);
        const found = catData.find(c => c.slug === slug);
        setCategory(found || null);
      } catch (err) {
        console.error('Failed to load category:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [slug, page]);

  useEffect(() => { setPage(1); }, [slug]);

  const goToPage = (p) => {
    setPage(p);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (loading) {
    return (
      <div className="category-page">
        <div className="category-page__header">
          <div className="skeleton" style={{ width: '200px', height: '32px', marginBottom: '8px' }} />
          <div className="skeleton" style={{ width: '140px', height: '16px' }} />
        </div>
        <div className="category-page__layout">
          <div className="category-page__main">
            <div className="category-page__grid">
              {[...Array(6)].map((_, i) => <ArticleCardSkeleton key={i} />)}
            </div>
          </div>
          <aside className="category-page__sidebar">
            <SidebarSkeleton />
          </aside>
        </div>
      </div>
    );
  }

  return (
    <div className="category-page">
      <div className="category-page__header">
        <h1 className="category-page__title">
          {category?.icon && <span>{category.icon} </span>}
          {category?.name || slug}
        </h1>
        {category?.description && (
          <p className="category-page__desc">{category.description}</p>
        )}
        <span className="category-page__count">{total} article{total !== 1 ? 's' : ''}</span>
      </div>

      <div className="category-page__layout">
        <div className="category-page__main">
          {articles.length === 0 ? (
            <p className="category-page__empty">No articles yet in this category.</p>
          ) : (
            <>
              <div className="category-page__grid">
                {articles.map(article => (
                  <ArticleCard key={article.id} article={article} />
                ))}
              </div>
              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="pagination__btn"
                    disabled={page <= 1}
                    onClick={() => goToPage(page - 1)}
                  >
                    ← Previous
                  </button>
                  <div className="pagination__pages">
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
                      <button
                        key={p}
                        className={`pagination__page ${p === page ? 'pagination__page--active' : ''}`}
                        onClick={() => goToPage(p)}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                  <button
                    className="pagination__btn"
                    disabled={page >= totalPages}
                    onClick={() => goToPage(page + 1)}
                  >
                    Next →
                  </button>
                </div>
              )}
            </>
          )}
        </div>
        <aside className="category-page__sidebar">
          <Sidebar categories={categories} recentPosts={articles} />
        </aside>
      </div>
    </div>
  );
}

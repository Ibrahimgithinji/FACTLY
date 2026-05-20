import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ArticleCard from '../components/ArticleCard';
import Sidebar from '../components/Sidebar';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './CategoryPage.css';

export default function CategoryPage() {
  const { slug } = useParams();
  const [category, setCategory] = useState(null);
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [catRes, artRes] = await Promise.all([
          fetch(CONTENT_ENDPOINTS.CATEGORIES),
          fetch(`${CONTENT_ENDPOINTS.ARTICLES}?category=${slug}`),
        ]);
        const catData = await catRes.json();
        const artData = await artRes.json();
        setCategories(catData);
        setArticles(artData);
        const found = catData.find(c => c.slug === slug);
        setCategory(found || null);
      } catch (err) {
        console.error('Failed to load category:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [slug]);

  if (loading) {
    return <div className="page-loading">Loading...</div>;
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
        <span className="category-page__count">{articles.length} article{articles.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="category-page__layout">
        <div className="category-page__main">
          {articles.length === 0 ? (
            <p className="category-page__empty">No articles yet in this category.</p>
          ) : (
            <div className="category-page__grid">
              {articles.map(article => (
                <ArticleCard key={article.id} article={article} />
              ))}
            </div>
          )}
        </div>
        <aside className="category-page__sidebar">
          <Sidebar categories={categories} recentPosts={articles} />
        </aside>
      </div>
    </div>
  );
}

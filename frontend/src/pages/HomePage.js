import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ArticleCard from '../components/ArticleCard';
import Sidebar from '../components/Sidebar';
import TrendingTopics from '../components/TrendingTopics';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './HomePage.css';

function SectionGrid({ section }) {
  if (!section || !section.articles || section.articles.length === 0) return null;
  const { category, articles } = section;
  return (
    <section className="home-section">
      <div className="home-section__header">
        <h2 className="home-section__title">
          {category.icon && <span>{category.icon} </span>}
          {category.name}
        </h2>
        <Link to={`/category/${category.slug}`} className="home-section__view-all">View all →</Link>
      </div>
      <div className="home-section__grid">
        {articles.slice(0, 4).map(article => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </section>
  );
}

export default function HomePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);

  const startupSection = data?.sections?.['startups'];
  const handleTopicClick = (topic) => {
    window.location.href = `/verify?topic=${encodeURIComponent(topic)}`;
  };

  useEffect(() => {
    async function fetchData() {
      try {
        const [homeRes, catRes] = await Promise.all([
          fetch(CONTENT_ENDPOINTS.HOMEPAGE),
          fetch(CONTENT_ENDPOINTS.CATEGORIES),
        ]);
        const homeData = await homeRes.json();
        const catData = await catRes.json();
        setData(homeData);
        setCategories(catData);
      } catch (err) {
        console.error('Failed to load homepage:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return <div className="home-loading">Loading...</div>;
  }

  const sectionKeys = data?.sections ? Object.keys(data.sections) : [];

  return (
    <div className="home-page">
      {/* What's New / Trending strip */}
      {data?.trending && data.trending.length > 0 && (
        <section className="home-trending">
          <div className="home-trending__inner">
            <span className="home-trending__label">What's New</span>
            <div className="home-trending__list">
              {data.trending.slice(0, 5).map(article => (
                <Link key={article.id} to={`/article/${article.slug}`} className="home-trending__item">
                  {article.title}
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Hero / Featured */}
      {data?.featured && data.featured.length > 0 && (
        <section className="home-hero">
          <ArticleCard article={data.featured[0]} featured />
          <div className="home-hero__side">
            {data.featured.slice(1, 3).map(article => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        </section>
      )}

      {/* Startup Spotlight */}
      {startupSection && startupSection.articles && startupSection.articles.length > 0 && (
        <section className="home-section home-section--startups">
          <div className="home-section__header">
            <h2 className="home-section__title">🚀 Startup Spotlight</h2>
            <Link to="/category/startups" className="home-section__view-all">All startups →</Link>
          </div>
          <div className="home-section__grid">
            {startupSection.articles.slice(0, 3).map(article => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        </section>
      )}

      {/* Main content + sidebar layout */}
      <div className="home-layout">
        <div className="home-layout__main">
          {/* Category sections */}
          {sectionKeys.map(key => (
            <SectionGrid key={key} section={data.sections[key]} />
          ))}

          {/* Latest articles */}
          {data?.latest && data.latest.length > 0 && (
            <section className="home-section">
              <div className="home-section__header">
                <h2 className="home-section__title">Latest</h2>
              </div>
              <div className="home-section__grid">
                {data.latest.slice(0, 6).map(article => (
                  <ArticleCard key={article.id} article={article} />
                ))}
              </div>
            </section>
          )}

          {/* Verification/Trending section */}
          <section className="home-section">
            <div className="home-section__header">
              <h2 className="home-section__title">Trending Claims</h2>
              <Link to="/verify" className="home-section__view-all">Verify a claim →</Link>
            </div>
            <TrendingTopics onTopicClick={handleTopicClick} />
          </section>
        </div>

        <aside className="home-layout__sidebar">
          <Sidebar categories={categories} recentPosts={data?.latest} />
        </aside>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ArticleCard from '../components/ArticleCard';
import SocialShare from '../components/SocialShare';
import Sidebar from '../components/Sidebar';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './ArticlePage.css';

export default function ArticlePage() {
  const { slug } = useParams();
  const [article, setArticle] = useState(null);
  const [related, setRelated] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [artRes, catRes] = await Promise.all([
          fetch(CONTENT_ENDPOINTS.ARTICLE(slug)),
          fetch(CONTENT_ENDPOINTS.CATEGORIES),
        ]);
        if (!artRes.ok) throw new Error('Article not found');
        const artData = await artRes.json();
        const catData = catRes.ok ? await catRes.json() : [];
        setArticle(artData);
        setCategories(catData);

        const relRes = await fetch(CONTENT_ENDPOINTS.RELATED(slug));
        if (relRes.ok) {
          const relData = await relRes.json();
          setRelated(relData);
        }
      } catch (err) {
        console.error('Failed to load article:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [slug]);

  if (loading) {
    return <div className="page-loading">Loading article...</div>;
  }

  if (!article) {
    return (
      <div className="article-error">
        <h1>Article not found</h1>
        <Link to="/">Go home</Link>
      </div>
    );
  }

  const url = window.location.href;
  const date = article.published_at ? new Date(article.published_at).toLocaleDateString('en-US', {
    weekday: 'long', month: 'long', day: 'numeric', year: 'numeric'
  }) : '';

  return (
    <div className="article-page">
      <div className="article-page__layout">
        <article className="article-page__main">
          {article.category && (
            <Link to={`/category/${article.category.slug}`} className="article-page__category">
              {article.category.icon && <span>{article.category.icon} </span>}
              {article.category.name}
            </Link>
          )}

          <h1 className="article-page__title">{article.title}</h1>

          <div className="article-page__meta">
            {article.author && (
              <div className="article-page__author">
                {article.author.avatar && (
                  <img src={article.author.avatar} alt="" className="article-page__author-img" />
                )}
                <div>
                  <span className="article-page__author-name">{article.author.display_name}</span>
                  {article.author.position && (
                    <span className="article-page__author-position">{article.author.position}</span>
                  )}
                </div>
              </div>
            )}
            <div className="article-page__meta-info">
              <span>{date}</span>
              {article.read_time && <span>{article.read_time} min read</span>}
            </div>
          </div>

          <SocialShare url={url} title={article.title} />

          {article.featured_image && (
            <div className="article-page__featured">
              <img src={article.featured_image} alt={article.title} />
            </div>
          )}

          {article.excerpt && (
            <p className="article-page__excerpt">{article.excerpt}</p>
          )}

          <div className="article-page__content" dangerouslySetInnerHTML={{ __html: article.content }} />

          {article.tags && article.tags.length > 0 && (
            <div className="article-page__tags">
              {article.tags.map(tag => (
                <span key={tag.id} className="article-page__tag">{tag.name}</span>
              ))}
            </div>
          )}

          <div className="article-page__share-bottom">
            <SocialShare url={url} title={article.title} />
          </div>

          {article.author && (
            <div className="article-page__author-bio">
              <h3>About the Author</h3>
              <div className="article-page__author-bio-inner">
                {article.author.avatar && (
                  <img src={article.author.avatar} alt="" className="article-page__author-bio-img" />
                )}
                <div>
                  <strong>{article.author.display_name}</strong>
                  {article.author.position && <span> — {article.author.position}</span>}
                  {article.author.bio && <p>{article.author.bio}</p>}
                  <div className="article-page__author-social">
                    {article.author.twitter && <a href={article.author.twitter} target="_blank" rel="noopener noreferrer">X</a>}
                    {article.author.linkedin && <a href={article.author.linkedin} target="_blank" rel="noopener noreferrer">LinkedIn</a>}
                    {article.author.website && <a href={article.author.website} target="_blank" rel="noopener noreferrer">Website</a>}
                  </div>
                </div>
              </div>
            </div>
          )}
        </article>

        <aside className="article-page__sidebar">
          <Sidebar categories={categories} recentPosts={related} />
        </aside>
      </div>

      {related.length > 0 && (
        <section className="article-page__related">
          <h2 className="article-page__related-title">Related Articles</h2>
          <div className="article-page__related-grid">
            {related.map(a => (
              <ArticleCard key={a.id} article={a} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

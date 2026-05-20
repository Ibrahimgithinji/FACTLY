import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ArticleCard from '../components/ArticleCard';
import SEOMeta from '../components/SEOMeta';
import { ArticleCardSkeleton } from '../components/Skeleton';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './AuthorPage.css';

export default function AuthorPage() {
  const { id } = useParams();
  const [author, setAuthor] = useState(null);
  const [articles, setArticles] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError(false);
      try {
        const res = await fetch(CONTENT_ENDPOINTS.AUTHOR(id));
        if (!res.ok) { setError(true); return; }
        const data = await res.json();
        setAuthor(data.author);
        setArticles(data.articles);
        setCount(data.article_count);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  if (loading) {
    return (
      <div className="author-page">
        <div className="author-page__header">
          <div className="skeleton" style={{ width: '80px', height: '80px', borderRadius: '50%' }} />
          <div>
            <div className="skeleton" style={{ width: '200px', height: '28px', marginBottom: '8px' }} />
            <div className="skeleton" style={{ width: '140px', height: '16px' }} />
          </div>
        </div>
        <div className="author-page__grid">
          {[...Array(4)].map((_, i) => <ArticleCardSkeleton key={i} />)}
        </div>
      </div>
    );
  }

  if (error || !author) {
    return (
      <div className="author-page__error">
        <h2>Author not found</h2>
        <Link to="/">Go home</Link>
      </div>
    );
  }

  return (
    <div className="author-page">
      <SEOMeta title={author.display_name} description={`Articles by ${author.display_name}${author.position ? `, ${author.position}` : ''}`} />

      <div className="author-page__header">
        {author.avatar ? (
          <img src={author.avatar} alt={author.display_name} className="author-page__avatar" />
        ) : (
          <div className="author-page__avatar author-page__avatar--placeholder">
            {author.display_name.charAt(0).toUpperCase()}
          </div>
        )}
        <div className="author-page__info">
          <h1 className="author-page__name">{author.display_name}</h1>
          {author.position && <span className="author-page__position">{author.position}</span>}
          {author.bio && <p className="author-page__bio">{author.bio}</p>}
          <div className="author-page__meta">
            <span className="author-page__count">{count} article{count !== 1 ? 's' : ''}</span>
            {author.twitter && <a href={author.twitter} target="_blank" rel="noopener noreferrer" className="author-page__social">X</a>}
            {author.linkedin && <a href={author.linkedin} target="_blank" rel="noopener noreferrer" className="author-page__social">LinkedIn</a>}
            {author.website && <a href={author.website} target="_blank" rel="noopener noreferrer" className="author-page__social">Website</a>}
          </div>
        </div>
      </div>

      <h2 className="author-page__section-title">Articles</h2>
      {articles.length === 0 ? (
        <p className="author-page__empty">No articles yet.</p>
      ) : (
        <div className="author-page__grid">
          {articles.map(a => <ArticleCard key={a.id} article={a} />)}
        </div>
      )}
    </div>
  );
}

import React from 'react';
import { Link } from 'react-router-dom';
import './ArticleCard.css';

export default function ArticleCard({ article, featured }) {
  const { title, slug, excerpt, featured_image, category, author, published_at, read_time, tags } = article;

  const date = published_at ? new Date(published_at).toLocaleDateString('en-US', {
    month: 'long', day: 'numeric', year: 'numeric'
  }) : '';

  if (featured) {
    return (
      <article className="article-card article-card--featured">
        <Link to={`/article/${slug}`} className="article-card__link">
          {featured_image && (
            <div className="article-card__image">
              <img src={featured_image} alt={title} loading="lazy" />
              {read_time && <span className="article-card__badge">{read_time} min</span>}
            </div>
          )}
          <div className="article-card__body">
            {category && <span className="article-card__category">{category.name}</span>}
            <h2 className="article-card__title">{title}</h2>
            <p className="article-card__excerpt">{excerpt}</p>
            <div className="article-card__meta">
              {author && <span className="article-card__author">{author.display_name}</span>}
              <span className="article-card__date">{date}</span>
              {read_time && <span className="article-card__read-time">{read_time} min read</span>}
            </div>
          </div>
        </Link>
      </article>
    );
  }

  return (
    <article className="article-card">
      <Link to={`/article/${slug}`} className="article-card__link">
        {featured_image && (
          <div className="article-card__image">
            <img src={featured_image} alt={title} loading="lazy" />
            {read_time && <span className="article-card__badge">{read_time} min</span>}
          </div>
        )}
        <div className="article-card__body">
          {category && <span className="article-card__category">{category.name}</span>}
          <h3 className="article-card__title">{title}</h3>
          <p className="article-card__excerpt">{excerpt}</p>
          <div className="article-card__meta">
            <span className="article-card__date">{date}</span>
            {read_time && <span className="article-card__read-time">{read_time} min read</span>}
          </div>
        </div>
      </Link>
    </article>
  );
}

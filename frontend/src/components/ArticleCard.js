import React from 'react';
import { Link } from 'react-router-dom';
import './ArticleCard.css';

export default function ArticleCard({ article, featured, compact, horizontal }) {
  const { title, slug, excerpt, featured_image, category, author, published_at, read_time } = article;

  const date = published_at ? new Date(published_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  }) : '';

  const score = article.credibility_score || article.verification_score || article.score;
  const verdict = article.verdict || article.classification;
  const showSignal = score || verdict;
  const cardClassName = [
    'article-card',
    featured ? 'article-card--featured' : '',
    compact ? 'article-card--compact' : '',
    horizontal ? 'article-card--horizontal' : '',
  ].filter(Boolean).join(' ');

  if (featured) {
    return (
      <article className={cardClassName}>
        <Link to={`/article/${slug}`} className="article-card__link">
          {featured_image && (
            <div className="article-card__image">
              <img src={featured_image} alt={title} loading="lazy" />
              {showSignal && (
                <span className="article-card__signal">
                  {score ? `${score}% verified` : verdict}
                </span>
              )}
            </div>
          )}
          <div className="article-card__body">
            <div className="article-card__kicker-row">
              {category && <span className="article-card__category">{category.name}</span>}
              {verdict && <span className="article-card__verdict">{verdict}</span>}
            </div>
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
    <article className={cardClassName}>
      <Link to={`/article/${slug}`} className="article-card__link">
        {featured_image && (
          <div className="article-card__image">
            <img src={featured_image} alt={title} loading="lazy" />
            {showSignal && (
              <span className="article-card__signal">
                {score ? `${score}% verified` : verdict}
              </span>
            )}
          </div>
        )}
        <div className="article-card__body">
          <div className="article-card__kicker-row">
            {category && <span className="article-card__category">{category.name}</span>}
            {verdict && <span className="article-card__verdict">{verdict}</span>}
          </div>
          <h3 className="article-card__title">{title}</h3>
          {!compact && <p className="article-card__excerpt">{excerpt}</p>}
          <div className="article-card__meta">
            <span className="article-card__date">{date}</span>
            {read_time && <span className="article-card__read-time">{read_time} min read</span>}
          </div>
        </div>
      </Link>
    </article>
  );
}

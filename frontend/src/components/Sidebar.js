import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css';

export default function Sidebar({ categories, recentPosts }) {
  return (
    <aside className="sidebar">
      {categories && categories.length > 0 && (
        <div className="sidebar__widget">
          <h3 className="sidebar__title">Categories</h3>
          <ul className="sidebar__list">
            {categories.map(cat => (
              <li key={cat.id}>
                <Link to={`/category/${cat.slug}`} className="sidebar__link">
                  {cat.icon && <span className="sidebar__icon">{cat.icon}</span>}
                  {cat.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {recentPosts && recentPosts.length > 0 && (
        <div className="sidebar__widget">
          <h3 className="sidebar__title">Recent Posts</h3>
          <ul className="sidebar__posts">
            {recentPosts.slice(0, 5).map(post => (
              <li key={post.id}>
                <Link to={`/article/${post.slug}`} className="sidebar__post-link">
                  {post.featured_image && (
                    <img src={post.featured_image} alt="" className="sidebar__post-img" loading="lazy" />
                  )}
                  <div className="sidebar__post-info">
                    <span className="sidebar__post-title">{post.title}</span>
                    <span className="sidebar__post-date">
                      {post.published_at ? new Date(post.published_at).toLocaleDateString() : ''}
                    </span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="sidebar__widget sidebar__cta">
        <h3 className="sidebar__title">Verify a Claim</h3>
        <p>Spot something suspicious? Paste it in our verification tool and get a Factly Score.</p>
        <a href="/verify" className="sidebar__cta-btn">
          Verify Now
        </a>
      </div>
    </aside>
  );
}

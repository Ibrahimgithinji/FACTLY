import React, { useState, useEffect, useCallback } from 'react';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './CommentsSection.css';

function CommentForm({ articleId, onCommentAdded }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [content, setContent] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setSending(true);
    try {
      const res = await fetch(CONTENT_ENDPOINTS.COMMENTS(articleId), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, content, article: articleId }),
      });
      if (!res.ok) throw new Error('Failed to post comment');
      setSuccess(true);
      setName('');
      setEmail('');
      setContent('');
      if (onCommentAdded) onCommentAdded();
    } catch {
      setError('Failed to post comment. Please try again.');
    } finally {
      setSending(false);
    }
  };

  if (success) {
    return (
      <div className="comments-form__success">
        Comment submitted! It will appear after approval.
      </div>
    );
  }

  return (
    <form className="comments-form" onSubmit={handleSubmit}>
      <h4 className="comments-form__title">Leave a Comment</h4>
      {error && <div className="comments-form__error">{error}</div>}
      <div className="comments-form__row">
        <div className="comments-form__field">
          <label htmlFor="comment-name">Name *</label>
          <input id="comment-name" type="text" required value={name}
            onChange={e => setName(e.target.value)} placeholder="Your name" />
        </div>
        <div className="comments-form__field">
          <label htmlFor="comment-email">Email *</label>
          <input id="comment-email" type="email" required value={email}
            onChange={e => setEmail(e.target.value)} placeholder="your@email.com" />
        </div>
      </div>
      <div className="comments-form__field">
        <label htmlFor="comment-content">Comment *</label>
        <textarea id="comment-content" rows={4} required value={content}
          onChange={e => setContent(e.target.value)}
          placeholder="Share your thoughts..." />
      </div>
      <button type="submit" className="comments-form__btn" disabled={sending}>
        {sending ? 'Posting...' : 'Post Comment'}
      </button>
    </form>
  );
}

export default function CommentsSection({ articleId }) {
  const [comments, setComments] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchComments = useCallback(async () => {
    try {
      const res = await fetch(CONTENT_ENDPOINTS.COMMENTS(articleId));
      if (res.ok) {
        const data = await res.json();
        setComments(data);
        setCount(data.length);
      }
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, [articleId]);

  useEffect(() => { fetchComments(); }, [articleId, fetchComments]);

  return (
    <section className="comments-section">
      <h3 className="comments-section__heading">
        Comments {count > 0 && <span className="comments-section__count">({count})</span>}
      </h3>

      {loading ? (
        <p className="comments-section__loading">Loading comments...</p>
      ) : comments.length > 0 ? (
        <div className="comments-section__list">
          {comments.map(c => (
            <div key={c.id} className="comments-section__item">
              <div className="comments-section__avatar">
                {c.name.charAt(0).toUpperCase()}
              </div>
              <div className="comments-section__body">
                <div className="comments-section__meta">
                  <span className="comments-section__name">{c.name}</span>
                  <span className="comments-section__date">
                    {new Date(c.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="comments-section__text">{c.content}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="comments-section__empty">No comments yet. Be the first!</p>
      )}

      <CommentForm articleId={articleId} onCommentAdded={fetchComments} />
    </section>
  );
}

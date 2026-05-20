import React, { useState } from 'react';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './NewsletterSignup.css';

export default function NewsletterSignup({ variant = 'sidebar' }) {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setSending(true);
    try {
      const res = await fetch(CONTENT_ENDPOINTS.NEWSLETTER, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to subscribe');
      }
      setDone(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  };

  if (done) {
    return (
      <div className={`newsletter newsletter--${variant} newsletter--done`}>
        <span className="newsletter__icon">✓</span>
        <p>You're subscribed! Stay tuned for updates.</p>
      </div>
    );
  }

  return (
    <div className={`newsletter newsletter--${variant}`}>
      {variant === 'sidebar' ? (
        <>
          <h3 className="newsletter__title">📬 Stay Updated</h3>
          <p className="newsletter__desc">Get the latest tech news and fact-checks delivered to your inbox.</p>
          <form className="newsletter__form" onSubmit={handleSubmit}>
            {error && <div className="newsletter__error">{error}</div>}
            <input
              type="email"
              required
              placeholder="Enter your email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="newsletter__input"
            />
            <button type="submit" className="newsletter__btn" disabled={sending}>
              {sending ? 'Subscribing...' : 'Subscribe'}
            </button>
          </form>
          <p className="newsletter__footnote">No spam. Unsubscribe anytime.</p>
        </>
      ) : (
        <form className="newsletter__form newsletter__form--inline" onSubmit={handleSubmit}>
          {error && <div className="newsletter__error">{error}</div>}
          <div className="newsletter__inline-row">
            <input
              type="text"
              placeholder="Your name"
              value={name}
              onChange={e => setName(e.target.value)}
              className="newsletter__input"
            />
            <input
              type="email"
              required
              placeholder="Your email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="newsletter__input"
            />
            <button type="submit" className="newsletter__btn" disabled={sending}>
              {sending ? '...' : 'Subscribe'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

import React, { useState, useRef } from 'react';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './NewsletterSignup.css';

export default function NewsletterSignup({ variant = 'sidebar' }) {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const abortRef = useRef(null);

  const handleSubmit = async e => {
    e.preventDefault();
    if (abortRef.current) abortRef.current.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    setError('');
    setSending(true);
    try {
      const res = await fetch(CONTENT_ENDPOINTS.NEWSLETTER, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name }),
        signal: ac.signal,
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to subscribe');
      }
      setDone(true);
    } catch (err) {
      if (err.name === 'AbortError') return;
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
              id="newsletter-email"
              type="email"
              required
              placeholder="Enter your email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="newsletter__input"
              aria-label="Email address for newsletter"
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
              id="newsletter-name"
              type="text"
              placeholder="Your name"
              value={name}
              onChange={e => setName(e.target.value)}
              className="newsletter__input"
              aria-label="Your name for newsletter"
            />
            <input
              id="newsletter-email-inline"
              type="email"
              required
              placeholder="Your email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="newsletter__input"
              aria-label="Email address for newsletter"
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

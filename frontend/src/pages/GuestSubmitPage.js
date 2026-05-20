import React, { useState, useEffect } from 'react';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './GuestSubmitPage.css';

export default function GuestSubmitPage() {
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    title: '',
    content: '',
    excerpt: '',
    category_slug: '',
    author_name: '',
    author_email: '',
  });
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetch(CONTENT_ENDPOINTS.CATEGORIES)
      .then(r => r.json())
      .then(setCategories)
      .catch(() => {});
  }, []);

  const handleChange = e => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setSending(true);
    try {
      const res = await fetch(CONTENT_ENDPOINTS.GUEST_SUBMIT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(Object.values(data).flat().join(', '));
        return;
      }
      setSubmitted(true);
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setSending(false);
    }
  };

  if (submitted) {
    return (
      <div className="guest-submit">
        <div className="guest-submit__success">
          <span className="guest-submit__success-icon">✓</span>
          <h1>Thank You!</h1>
          <p>Your article has been submitted for review. Our team will review it and publish it if it meets our guidelines.</p>
          <a href="/" className="guest-submit__btn">Back to Home</a>
        </div>
      </div>
    );
  }

  return (
    <div className="guest-submit">
      <div className="guest-submit__inner">
        <h1 className="guest-submit__title">Write for Factly</h1>
        <p className="guest-submit__desc">
          Have a story, opinion, or insight to share? Submit your article below. Our editors will review and publish it.
        </p>

        {error && <div className="guest-submit__error">{error}</div>}

        <form onSubmit={handleSubmit} className="guest-submit__form">
          <div className="guest-submit__field">
            <label htmlFor="author_name">Your Name *</label>
            <input
              id="author_name"
              name="author_name"
              type="text"
              required
              value={form.author_name}
              onChange={handleChange}
              placeholder="John Doe"
            />
          </div>

          <div className="guest-submit__field">
            <label htmlFor="author_email">Your Email *</label>
            <input
              id="author_email"
              name="author_email"
              type="email"
              required
              value={form.author_email}
              onChange={handleChange}
              placeholder="john@example.com"
            />
          </div>

          <div className="guest-submit__field">
            <label htmlFor="title">Article Title *</label>
            <input
              id="title"
              name="title"
              type="text"
              required
              value={form.title}
              onChange={handleChange}
              placeholder="A compelling title for your article"
            />
          </div>

          <div className="guest-submit__field">
            <label htmlFor="category_slug">Category</label>
            <select
              id="category_slug"
              name="category_slug"
              value={form.category_slug}
              onChange={handleChange}
            >
              <option value="">Select a category</option>
              {categories.map(cat => (
                <option key={cat.id} value={cat.slug}>{cat.icon} {cat.name}</option>
              ))}
            </select>
          </div>

          <div className="guest-submit__field">
            <label htmlFor="excerpt">Short Excerpt</label>
            <textarea
              id="excerpt"
              name="excerpt"
              rows={2}
              value={form.excerpt}
              onChange={handleChange}
              placeholder="A brief summary of your article (1-2 sentences)"
            />
          </div>

          <div className="guest-submit__field">
            <label htmlFor="content">Article Content *</label>
            <textarea
              id="content"
              name="content"
              rows={12}
              required
              value={form.content}
              onChange={handleChange}
              placeholder="Write your article here. You can use plain text or HTML."
            />
          </div>

          <button type="submit" className="guest-submit__btn" disabled={sending}>
            {sending ? 'Submitting...' : 'Submit Article'}
          </button>
        </form>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FactlyScoreInline } from '../components/FactlyScoreBadge';
import { RevealOnScroll, StaggerContainer, StaggerItem } from '../components/Animations';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../utils/constants';
import './CommunityPage.css';

const CLAIMS_API = `${API_BASE_URL}/api/claims/`;
const SUBMIT_API = `${API_BASE_URL}/api/claims/submit/`;

export default function CommunityTipsPage() {
  const { isAuthenticated } = useAuth();
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({ claim_text: '', source_url: '', category: 'general' });
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`${CLAIMS_API}?limit=50`)
      .then((r) => r.json())
      .then((data) => {
        setClaims(data.results || data.claims || []);
        setLoading(false);
      })
      .catch(() => {
        setClaims([]);
        setLoading(false);
      });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.claim_text.trim()) {
      setError('Please enter a claim.');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      const resp = await fetch(SUBMIT_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(formData),
      });
      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.error || err.message || 'Failed to submit');
      }
      const newClaim = await resp.json();
      setClaims((prev) => [newClaim, ...prev]);
      setSubmitted(true);
      setFormData({ claim_text: '', source_url: '', category: 'general' });
      setTimeout(() => setSubmitted(false), 3000);
      setShowForm(false);
    } catch (err) {
      setError(err.message);
    }
    setSubmitting(false);
  };

  const categories = ['general', 'politics', 'health', 'science', 'technology', 'social media', 'finance'];

  return (
    <div className="community-page">
      <header className="community-header">
        <div className="community-header__left">
          <span className="section-label">Community</span>
          <h1 className="community-title">Submit a Tip</h1>
          <p className="community-subtitle">
            Found a suspicious claim? Submit it for our team and community to fact-check.
          </p>
        </div>
        <button
          className="community-submit-btn"
          onClick={() => setShowForm(!showForm)}
          disabled={!isAuthenticated}
        >
          {showForm ? 'Cancel' : 'Submit a Claim'}
        </button>
      </header>

      {!isAuthenticated && (
        <div className="community-auth-notice">
          <p>You need to be signed in to submit claims. <a href="/login">Sign in</a></p>
        </div>
      )}

      <AnimatePresence>
        {showForm && (
          <motion.form
            className="community-form"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            onSubmit={handleSubmit}
          >
            <div className="form-group">
              <label htmlFor="claim-text">Claim Text <span className="required">*</span></label>
              <textarea
                id="claim-text"
                value={formData.claim_text}
                onChange={(e) => setFormData({ ...formData, claim_text: e.target.value })}
                placeholder="Enter the claim you want fact-checked..."
                rows={4}
              />
            </div>
            <div className="form-group">
              <label htmlFor="source-url">Source URL (optional)</label>
              <input
                id="source-url"
                type="url"
                value={formData.source_url}
                onChange={(e) => setFormData({ ...formData, source_url: e.target.value })}
                placeholder="https://example.com/article"
              />
            </div>
            <div className="form-group">
              <label htmlFor="claim-category">Category</label>
              <select
                id="claim-category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
                ))}
              </select>
            </div>
            {error && <div className="community-form__error">{error}</div>}
            <button type="submit" className="community-form__submit" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit for Review'}
            </button>
          </motion.form>
        )}
      </AnimatePresence>

      {submitted && (
        <motion.div
          className="community-success"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          Claim submitted successfully! Our team will review it.
        </motion.div>
      )}

      <div className="community-claims">
        <h2 className="community-section-title">Recent Community Claims</h2>
        {loading ? (
          <div className="community-loading">
            {[1, 2, 3].map((i) => (
              <div key={i} className="claim-skeleton" />
            ))}
          </div>
        ) : claims.length === 0 ? (
          <div className="community-empty">
            <p>No claims submitted yet. Be the first to submit a tip!</p>
          </div>
        ) : (
          <StaggerContainer className="claims-list" staggerDelay={0.05}>
            {claims.map((claim) => (
              <StaggerItem key={claim.id}>
                <div className="claim-card">
                  <div className="claim-card__header">
                    <span className="claim-card__category">{claim.category || 'General'}</span>
                    {claim.verdict && (
                      <FactlyScoreInline
                        score={claim.verdict === 'true' ? 85 : claim.verdict === 'false' ? 20 : 50}
                        verdict={claim.verdict}
                      />
                    )}
                  </div>
                  <p className="claim-card__text">{claim.claim_text}</p>
                  {claim.source_url && (
                    <a href={claim.source_url} target="_blank" rel="noreferrer" className="claim-card__source">
                      View source
                    </a>
                  )}
                  <div className="claim-card__meta">
                    {claim.created_at && (
                      <span>{new Date(claim.created_at).toLocaleDateString()}</span>
                    )}
                    {claim.sensationalist_score !== undefined && (
                      <span>Sensationalism: {claim.sensationalist_score}/100</span>
                    )}
                  </div>
                </div>
              </StaggerItem>
            ))}
          </StaggerContainer>
        )}
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { apiPut } from '../utils/apiClient';
import { API_ENDPOINTS } from '../utils/api';
import { API_BASE_URL } from '../utils/constants';
import { FactlyScoreBadge, FactlyScoreInline, FactlyScoreBar } from '../components/FactlyScoreBadge';
import { RevealOnScroll, StaggerContainer, StaggerItem, CountUp } from '../components/Animations';
import './ProfilePage.css';

export default function ProfilePage() {
  const { user } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState({ total: 0, avgScore: 0, verified: 0, flagged: 0 });

  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem('factCheckHistory') || '[]');
    setHistory(stored);
    if (stored.length > 0) {
      const total = stored.length;
      const avgScore = Math.round(stored.reduce((s, h) => s + (h.factly_score || 0), 0) / total);
      const verified = stored.filter((h) => (h.factly_score || 0) >= 60).length;
      const flagged = stored.filter((h) => (h.factly_score || 0) < 40).length;
      setStats({ total, avgScore, verified, flagged });
    }
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setIsSubmitting(true);
    const body = {};
    let changed = false;
    if (name !== user?.name) { body.name = name; changed = true; }
    if (email !== user?.email) {
      if (!currentPassword) { setError('Current password is required to change your email address.'); setIsSubmitting(false); return; }
      body.email = email; body.current_password = currentPassword; changed = true;
    }
    if (!changed) { setMessage('No changes to save.'); setIsSubmitting(false); return; }
    const result = await apiPut(API_ENDPOINTS.USER, body);
    if (result.success) { setCurrentPassword(''); setMessage(result.data.message || 'Profile updated successfully.'); }
    else { setError(result.error || 'Failed to update profile.'); }
    setIsSubmitting(false);
  };

  const recentVerifications = history.slice(0, 10);

  return (
    <div className="profile-page">
      <header className="profile-hero">
        <div className="profile-hero__avatar">
          {user?.name?.charAt(0).toUpperCase() || 'U'}
        </div>
        <div className="profile-hero__info">
          <h1>{user?.name || 'User'}</h1>
          <p>{user?.email || 'user@example.com'}</p>
          <div className="profile-hero__stats">
            <div className="profile-stat">
              <span className="profile-stat__num"><CountUp end={stats.total} duration={1.2} /></span>
              <span className="profile-stat__label">Verifications</span>
            </div>
            <div className="profile-stat">
              <span className="profile-stat__num"><CountUp end={stats.avgScore} duration={1.2} /></span>
              <span className="profile-stat__label">Avg Score</span>
            </div>
            <div className="profile-stat">
              <span className="profile-stat__num" style={{ color: '#22c55e' }}><CountUp end={stats.verified} duration={1.2} /></span>
              <span className="profile-stat__label">Verified</span>
            </div>
            <div className="profile-stat">
              <span className="profile-stat__num" style={{ color: '#ef4444' }}><CountUp end={stats.flagged} duration={1.2} /></span>
              <span className="profile-stat__label">Flagged</span>
            </div>
          </div>
        </div>
        {stats.avgScore > 0 && (
          <div className="profile-hero__badge">
            <FactlyScoreBadge score={stats.avgScore} size="md" animated={true} />
          </div>
        )}
      </header>

      <div className="profile-tabs">
        <button className={`profile-tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>Overview</button>
        <button className={`profile-tab ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>Verification History</button>
        <button className={`profile-tab ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}>Settings</button>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div key="overview" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="profile-overview">
            <div className="profile-overview__grid">
              <div className="profile-card">
                <h3>Trust Score</h3>
                <FactlyScoreBar score={stats.avgScore} verdict={stats.avgScore >= 70 ? 'mostly_true' : stats.avgScore >= 40 ? 'mixed' : 'false'} />
                <p>Based on your {stats.total} verification{stats.total !== 1 ? 's' : ''}</p>
              </div>
              <div className="profile-card">
                <h3>Activity</h3>
                <div className="profile-activity-list">
                  {recentVerifications.slice(0, 5).map((item, i) => (
                    <div key={i} className="profile-activity-item">
                      <span className="profile-activity-claim">{item.claim || item.originalText?.substring(0, 60)}</span>
                      <FactlyScoreInline score={item.factly_score} verdict={item.classification} />
                    </div>
                  ))}
                  {recentVerifications.length === 0 && <p className="profile-empty">No verifications yet</p>}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'history' && (
          <motion.div key="history" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="profile-history">
            {history.length === 0 ? (
              <div className="profile-empty-state">
                <p>No verification history yet. Start by verifying a claim!</p>
                <a href="/verify" className="profile-cta-btn">Verify a Claim</a>
              </div>
            ) : (
              <StaggerContainer className="profile-history-list" staggerDelay={0.04}>
                {history.map((item, i) => (
                  <StaggerItem key={item.id || i}>
                    <div className="profile-history-item">
                      <div className="profile-history-left">
                        <FactlyScoreBadge score={item.factly_score} size="sm" showLabel={false} />
                      </div>
                      <div className="profile-history-center">
                        <p className="profile-history-claim">{item.claim || item.originalText}</p>
                        <div className="profile-history-meta">
                          <span>{new Date(item.timestamp).toLocaleDateString()}</span>
                          <FactlyScoreInline score={item.factly_score} verdict={item.classification} />
                        </div>
                        <FactlyScoreBar score={item.factly_score} verdict={item.classification} showScore={false} />
                      </div>
                      <div className="profile-history-right">
                        <a href="/results" className="profile-history-view">View</a>
                      </div>
                    </div>
                  </StaggerItem>
                ))}
              </StaggerContainer>
            )}
          </motion.div>
        )}

        {activeTab === 'settings' && (
          <motion.div key="settings" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="profile-settings">
            {message && <div className="profile-message success">{message}</div>}
            {error && <div className="profile-message error">{error}</div>}
            <form className="profile-form" onSubmit={handleSubmit}>
              <div className="profile-form-group">
                <label htmlFor="profile-name">Name</label>
                <input id="profile-name" type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" disabled={isSubmitting} />
              </div>
              <div className="profile-form-group">
                <label htmlFor="profile-email">Email</label>
                <input id="profile-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" disabled={isSubmitting} />
              </div>
              {email !== user?.email && (
                <div className="profile-form-group">
                  <label htmlFor="profile-password">Current Password <span className="required">*</span></label>
                  <input id="profile-password" type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} placeholder="Required to change email" disabled={isSubmitting} />
                </div>
              )}
              <button type="submit" className="profile-form-submit" disabled={isSubmitting}>
                {isSubmitting ? 'Saving...' : 'Save Changes'}
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

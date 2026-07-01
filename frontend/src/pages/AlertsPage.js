import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FactlyScoreInline, FactlyScoreBar } from '../components/FactlyScoreBadge';
import { RevealOnScroll, StaggerContainer, StaggerItem } from '../components/Animations';
import { API_BASE_URL } from '../utils/constants';
import './AlertsPage.css';

const ALERTS_API = `${API_BASE_URL}/api/alerts/`;

const PRIORITY_CONFIG = {
  critical: { color: '#dc2626', bg: '#dc262612', icon: '!!' },
  high: { color: '#ef4444', bg: '#ef444412', icon: '!' },
  medium: { color: '#eab308', bg: '#eab30812', icon: '?' },
  low: { color: '#22c55e', bg: '#22c55e12', icon: 'i' },
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetch(`${ALERTS_API}?limit=50`)
      .then((r) => r.json())
      .then((data) => {
        setAlerts(data.results || data.alerts || []);
        setLoading(false);
      })
      .catch(() => {
        setAlerts([]);
        setLoading(false);
      });
  }, []);

  const filteredAlerts = filter === 'all'
    ? alerts
    : alerts.filter((a) => (a.priority || '').toLowerCase() === filter);

  return (
    <div className="alerts-page">
      <header className="alerts-header">
        <div>
          <span className="section-label">Misinformation Alerts</span>
          <h1 className="alerts-title">Active Alerts</h1>
          <p className="alerts-subtitle">
            Real-time alerts for high-risk misinformation campaigns and viral false claims
          </p>
        </div>
      </header>

      {alerts.length > 0 && (
        <div className="alerts-summary">
          {['critical', 'high', 'medium', 'low'].map((level) => {
            const count = alerts.filter((a) => (a.priority || '').toLowerCase() === level).length;
            const cfg = PRIORITY_CONFIG[level];
            return (
              <div key={level} className="alert-summary-card" style={{ borderLeftColor: cfg.color }}>
                <span className="alert-summary__num" style={{ color: cfg.color }}>{count}</span>
                <span className="alert-summary__label">{level.charAt(0).toUpperCase() + level.slice(1)}</span>
              </div>
            );
          })}
        </div>
      )}

      <div className="alerts-filters">
        {['all', 'critical', 'high', 'medium', 'low'].map((level) => (
          <button
            key={level}
            className={`filter-btn ${filter === level ? 'filter-btn--active' : ''}`}
            onClick={() => setFilter(level)}
            style={filter === level && level !== 'all' && PRIORITY_CONFIG[level]
              ? { background: PRIORITY_CONFIG[level].color, borderColor: PRIORITY_CONFIG[level].color }
              : {}}
          >
            {level === 'all' ? 'All' : level.charAt(0).toUpperCase() + level.slice(1)}
            {level !== 'all' && (
              <span className="filter-count">
                {alerts.filter((a) => (a.priority || '').toLowerCase() === level).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="alerts-loading">
          {[1, 2, 3].map((i) => (
            <div key={i} className="alert-skeleton" />
          ))}
        </div>
      ) : filteredAlerts.length === 0 ? (
        <div className="alerts-empty">
          <div className="alerts-empty__icon">✓</div>
          <h2>No Active Alerts</h2>
          <p>No misinformation alerts match the selected filter. That's good news!</p>
        </div>
      ) : (
        <StaggerContainer className="alerts-list" staggerDelay={0.06}>
          {filteredAlerts.map((alert) => {
            const cfg = PRIORITY_CONFIG[alert.priority] || PRIORITY_CONFIG.medium;
            const isExpanded = expandedId === alert.id;

            return (
              <StaggerItem key={alert.id}>
                <motion.div
                  className={`alert-item ${isExpanded ? 'alert-item--expanded' : ''}`}
                  style={{ borderLeftColor: cfg.color }}
                  onClick={() => setExpandedId(isExpanded ? null : alert.id)}
                  whileHover={{ x: 4 }}
                >
                  <div className="alert-item__header">
                    <span className="alert-priority-badge" style={{ background: cfg.color }}>
                      {cfg.icon}
                    </span>
                    <div className="alert-item__main">
                      <h3 className="alert-item__topic">{alert.topic || 'Unknown Topic'}</h3>
                      <p className="alert-item__message">{alert.alert_message || alert.topic}</p>
                    </div>
                    <span className="alert-item__time">
                      {alert.created_at ? new Date(alert.created_at).toLocaleDateString() : ''}
                    </span>
                  </div>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        className="alert-item__detail"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.25 }}
                      >
                        {alert.triggers && (
                          <div className="alert-detail-section">
                            <h4>Triggers</h4>
                            <p>{typeof alert.triggers === 'string' ? alert.triggers : JSON.stringify(alert.triggers)}</p>
                          </div>
                        )}
                        {alert.status && (
                          <div className="alert-detail-section">
                            <h4>Status</h4>
                            <span className={`alert-status alert-status--${alert.status}`}>{alert.status}</span>
                          </div>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </StaggerItem>
            );
          })}
        </StaggerContainer>
      )}
    </div>
  );
}

import React from 'react';
import { motion } from 'framer-motion';
import './FactlyScoreBadge.css';

const VERDICT_CONFIG = {
  true: { label: 'True', color: '#22c55e', bg: '#22c55e15', icon: '✓' },
  mostly_true: { label: 'Mostly True', color: '#86efac', bg: '#86efac15', icon: '✓' },
  half_true: { label: 'Half True', color: '#eab308', bg: '#eab30815', icon: '◐' },
  mostly_false: { label: 'Mostly False', color: '#fb923c', bg: '#fb923c15', icon: '◑' },
  false: { label: 'False', color: '#ef4444', bg: '#ef444415', icon: '✗' },
  misleading: { label: 'Misleading', color: '#f97316', bg: '#f9731615', icon: '!' },
  unverifiable: { label: 'Unverifiable', color: '#6b7280', bg: '#6b728015', icon: '?' },
  unknown: { label: 'Unknown', color: '#9ca3af', bg: '#9ca3af15', icon: '—' },
};

function getVerdictFromScore(score) {
  if (score >= 80) return 'true';
  if (score >= 60) return 'mostly_true';
  if (score >= 40) return 'half_true';
  if (score >= 20) return 'mostly_false';
  return 'false';
}

function getVerdictConfig(verdict, score) {
  const normalizedVerdict = (verdict || '').toLowerCase().replace(/[\s-]/g, '_');
  if (VERDICT_CONFIG[normalizedVerdict]) return VERDICT_CONFIG[normalizedVerdict];
  if (score !== undefined && score !== null) {
    return VERDICT_CONFIG[getVerdictFromScore(score)];
  }
  return VERDICT_CONFIG.unknown;
}

export function FactlyScoreBadge({ score, verdict, size = 'md', showLabel = true, animated = true }) {
  const numericScore = typeof score === 'number' ? score : parseInt(score, 10) || 0;
  const config = getVerdictConfig(verdict, numericScore);

  const Wrapper = animated ? motion.div : 'div';
  const animProps = animated ? {
    initial: { scale: 0.8, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    transition: { type: 'spring', stiffness: 260, damping: 20 },
  } : {};

  return (
    <Wrapper className={`factly-badge factly-badge--${size}`} style={{ '--badge-color': config.color, '--badge-bg': config.bg }} {...animProps}>
      <div className="factly-badge__ring">
        <svg className="factly-badge__svg" viewBox="0 0 36 36">
          <path
            className="factly-badge__bg-path"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path
            className="factly-badge__fg-path"
            strokeDasharray={`${Math.max(0, numericScore)}, 100`}
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
        </svg>
        <span className="factly-badge__score">{numericScore}</span>
      </div>
      {showLabel && (
        <span className="factly-badge__label" style={{ color: config.color }}>
          <span className="factly-badge__icon">{config.icon}</span>
          {config.label}
        </span>
      )}
    </Wrapper>
  );
}

export function FactlyScoreInline({ score, verdict }) {
  const numericScore = typeof score === 'number' ? score : parseInt(score, 10) || 0;
  const config = getVerdictConfig(verdict, numericScore);

  return (
    <span className="factly-inline-badge" style={{ color: config.color, background: config.bg }}>
      <span className="factly-inline-icon">{config.icon}</span>
      <span className="factly-inline-score">{numericScore}</span>
      <span className="factly-inline-label">{config.label}</span>
    </span>
  );
}

export function FactlyScoreBar({ score, verdict, showScore = true }) {
  const numericScore = typeof score === 'number' ? score : parseInt(score, 10) || 0;
  const config = getVerdictConfig(verdict, numericScore);

  return (
    <div className="factly-score-bar">
      <div className="factly-score-bar__track">
        <motion.div
          className="factly-score-bar__fill"
          style={{ background: config.color }}
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(0, numericScore)}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
      {showScore && (
        <span className="factly-score-bar__label" style={{ color: config.color }}>
          {numericScore} — {config.label}
        </span>
      )}
    </div>
  );
}

export default FactlyScoreBadge;

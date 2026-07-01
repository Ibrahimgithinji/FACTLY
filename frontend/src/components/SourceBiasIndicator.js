import React from 'react';
import './SourceBiasIndicator.css';

const BIAS_LABELS = {
  left: { label: 'Left', color: '#3b82f6', bg: '#eff6ff' },
  'lean-left': { label: 'Lean Left', color: '#60a5fa', bg: '#eff6ff' },
  center: { label: 'Center', color: '#8b5cf6', bg: '#f5f3ff' },
  'lean-right': { label: 'Lean Right', color: '#f97316', bg: '#fff7ed' },
  right: { label: 'Right', color: '#ef4444', bg: '#fef2f2' },
  unknown: { label: 'Unknown', color: '#9ca3af', bg: '#f9fafb' },
};

export default function SourceBiasIndicator({ sources = [], compact = false }) {
  if (!sources || sources.length === 0) return null;

  const biasCounts = { left: 0, 'lean-left': 0, center: 0, 'lean-right': 0, right: 0, unknown: 0 };
  sources.forEach((s) => {
    const bias = s.bias || s.leaning || s.political_leaning || 'unknown';
    const normalized = bias.toLowerCase().replace(/\s+/g, '-');
    if (biasCounts[normalized] !== undefined) {
      biasCounts[normalized]++;
    } else {
      biasCounts.unknown++;
    }
  });

  const total = sources.length;

  if (compact) {
    return (
      <div className="sbi-compact">
        <span className="sbi-compact-label">Bias</span>
        <div className="sbi-compact-bar">
          {Object.entries(biasCounts).filter(([, c]) => c > 0).map(([bias, count]) => (
            <div
              key={bias}
              className="sbi-compact-segment"
              style={{ width: `${(count / total) * 100}%`, background: BIAS_LABELS[bias].color }}
              title={`${BIAS_LABELS[bias].label}: ${count}`}
            />
          ))}
        </div>
        <span className="sbi-compact-total">{total}</span>
      </div>
    );
  }

  return (
    <div className="sbi">
      <h4 className="sbi-title">Source Bias Distribution</h4>
      <div className="sbi-bar">
        {Object.entries(biasCounts).filter(([, c]) => c > 0).map(([bias, count]) => (
          <div
            key={bias}
            className="sbi-segment"
            style={{ width: `${(count / total) * 100}%`, background: BIAS_LABELS[bias].color }}
          >
            {(count / total) * 100 >= 12 && (
              <span className="sbi-segment-label">{count}</span>
            )}
          </div>
        ))}
      </div>
      <div className="sbi-legend">
        {Object.entries(biasCounts).filter(([, c]) => c > 0).map(([bias, count]) => (
          <div key={bias} className="sbi-legend-item">
            <span className="sbi-legend-dot" style={{ background: BIAS_LABELS[bias].color }} />
            <span className="sbi-legend-label">{BIAS_LABELS[bias].label}</span>
            <span className="sbi-legend-count">{count}</span>
          </div>
        ))}
      </div>
      {sources.length > 0 && (
        <div className="sbi-sources">
          <h5>Sources</h5>
          {sources.map((s, i) => {
            const bias = (s.bias || s.leaning || s.political_leaning || 'unknown').toLowerCase().replace(/\s+/g, '-');
            const cfg = BIAS_LABELS[bias] || BIAS_LABELS.unknown;
            return (
              <div key={i} className="sbi-source-row">
                <span className="sbi-source-name">{s.name || s.source_name || s.source || 'Source'}</span>
                <span className="sbi-source-badge" style={{ background: cfg.bg, color: cfg.color }}>
                  {cfg.label}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

import React from 'react';
import './Skeleton.css';

export function Skeleton({ width, height, borderRadius, className = '' }) {
  return (
    <div
      className={`skeleton ${className}`}
      style={{
        width: width || '100%',
        height: height || '20px',
        borderRadius: borderRadius || '8px',
      }}
    />
  );
}

export function ArticleCardSkeleton({ featured }) {
  if (featured) {
    return (
      <div className="skeleton-card skeleton-card--featured">
        <div className="skeleton-card__img">
          <Skeleton height="100%" borderRadius="12px" />
        </div>
        <div className="skeleton-card__body">
          <Skeleton width="80px" height="22px" />
          <Skeleton width="100%" height="24px" />
          <Skeleton width="100%" height="24px" />
          <Skeleton width="65%" height="24px" />
          <Skeleton width="100%" height="16px" />
          <Skeleton width="90%" height="16px" />
          <Skeleton width="120px" height="14px" />
        </div>
      </div>
    );
  }

  return (
    <div className="skeleton-card">
      <Skeleton height="180px" borderRadius="12px" />
      <div className="skeleton-card__body">
        <Skeleton width="60px" height="18px" />
        <Skeleton width="100%" height="20px" />
        <Skeleton width="100%" height="20px" />
        <Skeleton width="45%" height="20px" />
        <Skeleton width="100%" height="14px" />
        <Skeleton width="80px" height="12px" />
      </div>
    </div>
  );
}

export function SidebarSkeleton() {
  return (
    <div className="skeleton-sidebar">
      <Skeleton width="100%" height="14px" />
      {[...Array(5)].map((_, i) => (
        <div key={i} className="skeleton-sidebar__item">
          <Skeleton width="100%" height="36px" />
        </div>
      ))}
      <Skeleton width="100%" height="14px" />
      {[...Array(3)].map((_, i) => (
        <div key={i} className="skeleton-sidebar__item">
          <Skeleton width="60px" height="60px" borderRadius="8px" />
          <div style={{ flex: 1 }}>
            <Skeleton width="100%" height="16px" />
            <Skeleton width="100%" height="16px" />
            <Skeleton width="40%" height="12px" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function ArticlePageSkeleton() {
  return (
    <div className="skeleton-article">
      <Skeleton width="120px" height="20px" />
      <Skeleton width="90%" height="32px" />
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '16px' }}>
        <Skeleton width="40px" height="40px" borderRadius="50%" />
        <div>
          <Skeleton width="140px" height="16px" />
          <Skeleton width="100px" height="12px" />
        </div>
      </div>
      <Skeleton width="100%" height="320px" borderRadius="12px" />
      <div style={{ marginTop: '20px' }}>
        {[...Array(8)].map((_, i) => (
          <Skeleton key={i} width={i % 2 === 0 ? '100%' : '92%'} height="16px" style={{ marginBottom: '10px' }} />
        ))}
      </div>
    </div>
  );
}

export function CategoryPageSkeleton() {
  return (
    <div>
      <Skeleton width="200px" height="32px" />
      <Skeleton width="140px" height="16px" />
      <div className="skeleton-grid">
        {[...Array(6)].map((_, i) => (
          <ArticleCardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

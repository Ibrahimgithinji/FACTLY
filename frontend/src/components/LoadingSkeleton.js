import React from 'react';
import './LoadingSkeleton.css';

/**
 * Loading Skeleton Component
 * Shows placeholder content while data is loading
 */
const LoadingSkeleton = ({
  count = 1,
  type = 'card', // card, line, circle, box
  height = 'auto',
  width = '100%',
}) => {
  const skeletons = Array.from({ length: count }, (_, i) => (
    <div key={i} className={`skeleton skeleton-${type}`} style={{ height, width }} />
  ));

  return <div className="skeleton-container">{skeletons}</div>;
};

/**
 * Card Skeleton Component
 * Loading skeleton for card-like content
 */
export const CardSkeleton = ({ count = 3 }) => (
  <div className="cards-skeleton">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="card-skeleton">
        <div className="skeleton skeleton-line" style={{ height: '20px', marginBottom: '12px' }} />
        <div className="skeleton skeleton-line" style={{ height: '16px', marginBottom: '12px', width: '80%' }} />
        <div className="skeleton skeleton-line" style={{ height: '16px', marginBottom: '12px', width: '60%' }} />
        <div className="skeleton skeleton-line" style={{ height: '40px', marginTop: '16px' }} />
      </div>
    ))}
  </div>
);

/**
 * Table Skeleton Component
 * Loading skeleton for table-like content
 */
export const TableSkeleton = ({ rows = 5, columns = 4 }) => (
  <div className="table-skeleton">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="table-row-skeleton">
        {Array.from({ length: columns }).map((_, j) => (
          <div key={j} className="table-cell-skeleton">
            <div className="skeleton skeleton-line" />
          </div>
        ))}
      </div>
    ))}
  </div>
);

/**
 * List Skeleton Component
 * Loading skeleton for list-like content
 */
export const ListSkeleton = ({ count = 5 }) => (
  <div className="list-skeleton">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="list-item-skeleton">
        <div className="skeleton skeleton-circle" />
        <div style={{ flex: 1 }}>
          <div className="skeleton skeleton-line" style={{ marginBottom: '8px' }} />
          <div className="skeleton skeleton-line" style={{ width: '70%' }} />
        </div>
      </div>
    ))}
  </div>
);

export default LoadingSkeleton;

import React from 'react';
import './EmptyState.css';

/**
 * Empty State Component
 * Displays when there's no data to show
 */
const EmptyState = ({
  icon = '📭',
  title = 'No Results',
  message = 'No data available. Try adjusting your filters or search criteria.',
  action,
  actionText = 'Try Again',
}) => {
  return (
    <div className="empty-state-container">
      <div className="empty-state-icon">{icon}</div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-message">{message}</p>
      {action && (
        <button className="empty-state-button" onClick={action}>
          {actionText}
        </button>
      )}
    </div>
  );
};

export default EmptyState;

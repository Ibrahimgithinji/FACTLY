import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './Auth.css';

const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const navigate = useNavigate();

  // Load history from localStorage
  useEffect(() => {
    const loadHistory = () => {
      try {
        const storedHistory = localStorage.getItem('factCheckHistory');
        if (storedHistory) {
          const parsedHistory = JSON.parse(storedHistory);
          // Sort by timestamp (newest first)
          parsedHistory.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
          setHistory(parsedHistory);
        }
      } catch (error) {
        console.error('Error loading history:', error);
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, []);

  // Get score color based on classification
  const getScoreColor = (classification) => {
    switch (classification?.toLowerCase()) {
      case 'likely authentic':
        return '#10b981'; // green
      case 'uncertain':
        return '#f59e0b'; // yellow
      case 'likely fake':
        return '#ef4444'; // red
      default:
        return '#64748b'; // gray
    }
  };

  // Format date
  const formatDate = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return timestamp;
    }
  };

  // Handle delete item
  const handleDelete = useCallback((e, id) => {
    e.stopPropagation();
    const updatedHistory = history.filter(item => item.id !== id);
    setHistory(updatedHistory);
    localStorage.setItem('factCheckHistory', JSON.stringify(updatedHistory));
    if (selectedItem?.id === id) {
      setSelectedItem(null);
    }
  }, [history, selectedItem]);

  // Handle clear all
  const handleClearAll = () => {
    if (window.confirm('Are you sure you want to clear all history?')) {
      setHistory([]);
      localStorage.removeItem('factCheckHistory');
      setSelectedItem(null);
    }
  };

  // Handle view details
  const handleViewDetails = (item) => {
    setSelectedItem(item);
  };

  // Handle close details panel
  const handleCloseDetails = () => {
    setSelectedItem(null);
  };

  // Handle re-verify
  const handleReverify = (item) => {
    // Store the item for re-verification
    localStorage.setItem('reverifyClaim', JSON.stringify({
      claim: item.claim,
      originalText: item.originalText || item.claim
    }));
    navigate('/');
  };

  if (loading) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Loading...</h1>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card history-card">
        <div className="auth-header">
          <h1>Verification History</h1>
          <p>View your past fact-check results</p>
        </div>

        {history.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon" aria-hidden="true">📜</div>
            <h2>No History Yet</h2>
            <p>Your verification history will appear here after you check some claims.</p>
            <button 
              className="auth-button primary"
              onClick={() => navigate('/')}
            >
              Start Verifying
            </button>
          </div>
        ) : (
          <>
            <div className="history-controls">
              <span className="history-count">{history.length} items</span>
              <button 
                className="clear-button"
                onClick={handleClearAll}
              >
                Clear All
              </button>
            </div>

            <div className="history-content">
              <div className="history-list">
                {history.map((item) => (
                  <div 
                    key={item.id}
                    className={`history-item ${selectedItem?.id === item.id ? 'selected' : ''}`}
                    onClick={() => handleViewDetails(item)}
                    role="button"
                    tabIndex={0}
                    onKeyPress={(e) => e.key === 'Enter' && handleViewDetails(item)}
                  >
                    <div className="history-item-header">
                      <span 
                        className="score-badge"
                        style={{ backgroundColor: getScoreColor(item.classification) }}
                      >
                        {item.factly_score}/100
                      </span>
                      <span className="classification">
                        {item.classification || 'Unknown'}
                      </span>
                    </div>
                    <p className="history-claim">
                      {item.claim?.substring(0, 100)}
                      {item.claim?.length > 100 ? '...' : ''}
                    </p>
                    <div className="history-meta">
                      <span className="history-date">{formatDate(item.timestamp)}</span>
                      <button 
                        className="delete-button"
                        onClick={(e) => handleDelete(e, item.id)}
                        aria-label="Delete this item"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {selectedItem && (
                <div className="history-details">
                  <div className="details-header">
                    <h2>Verification Details</h2>
                    <button className="close-button" onClick={handleCloseDetails}>×</button>
                  </div>
                  
                  <div className="details-section">
                    <h3>Claim</h3>
                    <p>{selectedItem.claim}</p>
                  </div>

                  <div className="details-section">
                    <h3>Result</h3>
                    <div className="result-overview">
                      <span 
                        className="score-large"
                        style={{ color: getScoreColor(selectedItem.classification) }}
                      >
                        {selectedItem.factly_score}
                      </span>
                      <span className="classification-large">
                        {selectedItem.classification || 'Unknown'}
                      </span>
                    </div>
                  </div>

                  {selectedItem.components && (
                    <div className="details-section">
                      <h3>Component Breakdown</h3>
                      {selectedItem.components.map((comp, index) => (
                        <div key={index} className="component-item">
                          <div className="component-header">
                            <span className="component-name">{comp.name}</span>
                            <span className="component-score">{Math.round(comp.score * 100)}%</span>
                          </div>
                          <div className="component-bar">
                            <div 
                              className="component-fill"
                              style={{ width: `${comp.score * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {selectedItem.justifications && selectedItem.justifications.length > 0 && (
                    <div className="details-section">
                      <h3>Justifications</h3>
                      <ul className="justifications-list">
                        {selectedItem.justifications.map((just, index) => (
                          <li key={index}>{just}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="details-actions">
                    <button 
                      className="auth-button primary"
                      onClick={() => handleReverify(selectedItem)}
                    >
                      Re-verify This Claim
                    </button>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default HistoryPage;

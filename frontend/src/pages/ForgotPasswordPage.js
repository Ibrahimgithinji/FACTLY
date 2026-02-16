import React, { useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [resetLink, setResetLink] = useState(null);
  const navigate = useNavigate();

  const { forgotPassword, getResetLink } = useAuth();

  const validateEmail = useCallback((email) => {
    if (!email.trim()) {
      return 'Email is required';
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return 'Please enter a valid email address';
    }
    return '';
  }, []);

  const handleChange = useCallback((e) => {
    const { value } = e.target;
    setEmail(value);
    setErrors((prev) => ({ ...prev, email: '' }));
    setSubmitStatus(null);
    setResetLink(null);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitStatus(null);
    setResetLink(null);

    const emailError = validateEmail(email);
    if (emailError) {
      setErrors({ email: emailError });
      return;
    }

    setIsSubmitting(true);
    const emailToUse = email;  // Capture email before async calls

    try {
      const result = await forgotPassword(emailToUse);

      if (result.success) {
        setSubmitStatus({
          type: 'success',
          message: 'If an account exists with this email, a password reset link has been sent. Please check your inbox.',
        });
        
        // In development mode, also try to get the reset link for testing
        if (process.env.NODE_ENV === 'development') {
          const linkResult = await getResetLink(emailToUse);  // Use captured email
          if (linkResult.success) {
            setResetLink(linkResult.resetLink);
          }
        }
        
        setEmail('');  // Clear after getting dev link
      } else {
        setSubmitStatus({
          type: 'error',
          message: result.error || 'Failed to send reset email. Please try again.',
        });
      }
    } catch (err) {
      setSubmitStatus({
        type: 'error',
        message: 'An unexpected error occurred. Please try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUseDevLink = () => {
    if (resetLink) {
      navigate(resetLink.replace('http://localhost:3000', ''));
    }
  };

  const handleCopyLink = () => {
    if (resetLink) {
      navigator.clipboard.writeText(resetLink).then(() => {
        alert('Reset link copied to clipboard!');
      }).catch(err => {
        console.error('Failed to copy link:', err);
      });
    }
  };

  const handleOpenInNewTab = () => {
    if (resetLink) {
      window.open(resetLink, '_blank');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <div className="auth-logo" aria-hidden="true">✓</div>
          <h1>Reset Password</h1>
          <p>Enter your email address to receive a password reset link</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          {submitStatus && (
            <div
              className={`auth-${submitStatus.type}`}
              role="alert"
              aria-live="assertive"
            >
              {submitStatus.message}
            </div>
          )}

          {resetLink && (
            <div
              style={{
                backgroundColor: '#e8f5e9',
                border: '2px solid #4caf50',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px'
              }}
              role="alert"
            >
              <p style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: 'bold', color: '#2e7d32' }}>
                🔧 Development Mode: Password Reset Link
              </p>
              <div
                style={{
                  backgroundColor: '#fff',
                  border: '1px solid #4caf50',
                  borderRadius: '4px',
                  padding: '12px',
                  marginBottom: '12px',
                  wordBreak: 'break-all',
                  fontSize: '13px',
                  fontFamily: 'monospace',
                  color: '#1b5e20'
                }}
              >
                {resetLink}
              </div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={handleUseDevLink}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    fontWeight: 'bold',
                    backgroundColor: '#4caf50',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    flex: '1',
                    minWidth: '140px'
                  }}
                  onMouseOver={(e) => e.target.style.backgroundColor = '#388e3c'}
                  onMouseOut={(e) => e.target.style.backgroundColor = '#4caf50'}
                >
                  ✓ Use This Link
                </button>
                <button
                  type="button"
                  onClick={handleOpenInNewTab}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    fontWeight: 'bold',
                    backgroundColor: '#2196f3',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    flex: '1',
                    minWidth: '140px'
                  }}
                  onMouseOver={(e) => e.target.style.backgroundColor = '#1976d2'}
                  onMouseOut={(e) => e.target.style.backgroundColor = '#2196f3'}
                >
                  🔗 Open in New Tab
                </button>
                <button
                  type="button"
                  onClick={handleCopyLink}
                  style={{
                    padding: '8px 16px',
                    fontSize: '13px',
                    fontWeight: 'bold',
                    backgroundColor: '#ff9800',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    flex: '1',
                    minWidth: '140px'
                  }}
                  onMouseOver={(e) => e.target.style.backgroundColor = '#f57c00'}
                  onMouseOut={(e) => e.target.style.backgroundColor = '#ff9800'}
                >
                  📋 Copy Link
                </button>
              </div>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">
              Email Address
              <span className="required" aria-hidden="true">*</span>
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={email}
              onChange={handleChange}
              placeholder="Enter your email"
              disabled={isSubmitting}
              className={errors.email ? 'error' : ''}
              aria-required="true"
              aria-invalid={errors.email ? 'true' : 'false'}
              aria-describedby={errors.email ? 'email-error' : undefined}
              autoComplete="email"
              autoFocus
            />
            {errors.email && (
              <span id="email-error" className="field-error" role="alert">
                {errors.email}
              </span>
            )}
          </div>

          <button
            type="submit"
            className="auth-button"
            disabled={isSubmitting}
            aria-busy={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <span className="spinner" aria-hidden="true"></span>
                <span>Sending...</span>
              </>
            ) : (
              'Send Reset Link'
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Remember your password?{' '}
            <Link to="/login" className="auth-link">
              Sign in
            </Link>
          </p>
          <p>
            Don't have an account?{' '}
            <Link to="/signup" className="auth-link">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;

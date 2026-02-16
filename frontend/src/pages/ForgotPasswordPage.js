import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  const { forgotPassword } = useAuth();

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
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitStatus(null);

    const emailError = validateEmail(email);
    if (emailError) {
      setErrors({ email: emailError });
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await forgotPassword(email);

      if (result.success) {
        setSubmitStatus({
          type: 'success',
          message: 'Password reset link has been sent to your email. Please check your inbox and click the link to reset your password.',
        });
        setEmail('');
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

import React, { useState, useCallback, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

const ResetPasswordPage = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const { verifyResetToken, resetPassword } = useAuth();

  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isVerifying, setIsVerifying] = useState(true);
  const [isTokenValid, setIsTokenValid] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  useEffect(() => {
    const verifyToken = async () => {
      const result = await verifyResetToken(token);

      if (result.success) {
        setIsTokenValid(true);
      } else {
        setSubmitStatus({
          type: 'error',
          message: result.error || 'This reset link is invalid or has expired.',
        });
      }
      setIsVerifying(false);
    };

    if (token) {
      verifyToken();
    } else {
      setSubmitStatus({
        type: 'error',
        message: 'Invalid reset link. Please request a new password reset.',
      });
      setIsVerifying(false);
    }
  }, [token, verifyResetToken]);

  const calculatePasswordStrength = useCallback((password) => {
    if (!password) return '';
    if (password.length < 6) return 'weak';
    if (password.length < 10 || !/[A-Z]/.test(password) || !/[0-9]/.test(password)) return 'medium';
    return 'strong';
  }, []);

  const [passwordStrength, setPasswordStrength] = useState('');

  const validateForm = useCallback(() => {
    const newErrors = {};

    if (!formData.newPassword) {
      newErrors.newPassword = 'New password is required';
    } else if (formData.newPassword.length < 6) {
      newErrors.newPassword = 'Password must be at least 6 characters';
    }

    if (formData.newPassword !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    if (name === 'newPassword') {
      setPasswordStrength(calculatePasswordStrength(value));
    }

    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
    setSubmitStatus(null);
  }, [errors, calculatePasswordStrength]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitStatus(null);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await resetPassword(token, formData.newPassword, formData.confirmPassword);

      if (result.success) {
        setSubmitStatus({
          type: 'success',
          message: 'Your password has been reset successfully. Redirecting to login...',
        });
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        setSubmitStatus({
          type: 'error',
          message: result.error || 'Failed to reset password. Please try again.',
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

  const getStrengthLabel = () => {
    switch (passwordStrength) {
      case 'weak': return 'Weak';
      case 'medium': return 'Medium';
      case 'strong': return 'Strong';
      default: return '';
    }
  };

  if (isVerifying) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <div className="auth-header">
            <div className="auth-logo" aria-hidden="true">✓</div>
            <h1>Verifying Reset Link</h1>
            <p>Please wait while we verify your reset link...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <div className="auth-logo" aria-hidden="true">✓</div>
          <h1>Set New Password</h1>
          <p>Enter your new password below</p>
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

          {isTokenValid && (
            <>
              <div className="form-group">
                <label htmlFor="newPassword">
                  New Password
                  <span className="required" aria-hidden="true">*</span>
                </label>
                <input
                  type="password"
                  id="newPassword"
                  name="newPassword"
                  value={formData.newPassword}
                  onChange={handleChange}
                  placeholder="Create a new password"
                  disabled={isSubmitting}
                  className={errors.newPassword ? 'error' : ''}
                  aria-required="true"
                  aria-invalid={errors.newPassword ? 'true' : 'false'}
                  aria-describedby={errors.newPassword ? 'newPassword-error' : 'password-help'}
                  autoComplete="new-password"
                />
                {formData.newPassword && (
                  <div className="password-strength">
                    <div className="password-strength-label">
                      <span>Password strength:</span>
                      <span className={`strength-${passwordStrength}`}>
                        {getStrengthLabel()}
                      </span>
                    </div>
                    <div className="password-strength-bar">
                      <div className={`password-strength-fill ${passwordStrength}`}></div>
                    </div>
                  </div>
                )}
                <p id="password-help" className="sr-only">
                  Password must be at least 6 characters long
                </p>
                {errors.newPassword && (
                  <span id="newPassword-error" className="field-error" role="alert">
                    {errors.newPassword}
                  </span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">
                  Confirm Password
                  <span className="required" aria-hidden="true">*</span>
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Confirm your new password"
                  disabled={isSubmitting}
                  className={errors.confirmPassword ? 'error' : ''}
                  aria-required="true"
                  aria-invalid={errors.confirmPassword ? 'true' : 'false'}
                  aria-describedby={errors.confirmPassword ? 'confirm-error' : undefined}
                  autoComplete="new-password"
                />
                {errors.confirmPassword && (
                  <span id="confirm-error" className="field-error" role="alert">
                    {errors.confirmPassword}
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
                    <span>Resetting Password...</span>
                  </>
                ) : (
                  'Reset Password'
                )}
              </button>
            </>
          )}

          <div className="auth-footer">
            <p>
              Remember your password?{' '}
              <Link to="/login" className="auth-link">
                Sign in
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ResetPasswordPage;

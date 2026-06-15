import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiPut } from '../utils/apiClient';
import { API_ENDPOINTS } from '../utils/api';
import '../pages/Auth.css';

export default function ProfilePage() {
  const { user, setTokens } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [currentPassword, setCurrentPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setIsSubmitting(true);

    const body = {};
    let changed = false;

    if (name !== user?.name) {
      body.name = name;
      changed = true;
    }

    if (email !== user?.email) {
      if (!currentPassword) {
        setError('Current password is required to change your email address.');
        setIsSubmitting(false);
        return;
      }
      body.email = email;
      body.current_password = currentPassword;
      changed = true;
    }

    if (!changed) {
      setMessage('No changes to save.');
      setIsSubmitting(false);
      return;
    }

    const result = await apiPut(API_ENDPOINTS.USER, body);

    if (result.success) {
      setTokens(
        sessionStorage.getItem('authToken'),
        sessionStorage.getItem('refreshToken'),
        { id: result.data.id, email: result.data.email, name: result.data.name }
      );
      setCurrentPassword('');
      setMessage(result.data.message || 'Profile updated successfully.');
    } else {
      setError(result.error || 'Failed to update profile.');
    }

    setIsSubmitting(false);
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <div className="auth-logo">
            {user?.name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <h1>Profile</h1>
          <p>Manage your account information</p>
        </div>

        {message && (
          <div className="auth-success">
            {message}
          </div>
        )}

        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              disabled={isSubmitting}
            />
          </div>

          {email !== user?.email && (
            <div className="form-group">
              <label htmlFor="currentPassword">
                Current Password <span className="required">*</span>
              </label>
              <input
                id="currentPassword"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Required to change email"
                disabled={isSubmitting}
              />
            </div>
          )}

          <button
            type="submit"
            className="auth-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <span className="spinner" />
                Saving...
              </>
            ) : (
              'Save Changes'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

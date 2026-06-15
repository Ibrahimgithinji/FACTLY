import React, { useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useSettings } from '../context/SettingsContext';
import './UserMenu.css';

export default function UserMenu({ isOpen, onClose }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { settings, updateSetting } = useSettings();
  const menuRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleLogout = () => {
    logout();
    onClose();
  };

  return (
    <div className="user-menu" ref={menuRef} role="dialog" aria-label="User menu">
      <div className="user-menu__header">
        <span className="user-menu__avatar">
          {user?.name?.charAt(0).toUpperCase() || 'U'}
        </span>
        <div className="user-menu__info">
          <span className="user-menu__name">{user?.name || 'User'}</span>
          <span className="user-menu__email">{user?.email || ''}</span>
        </div>
      </div>

      <div className="user-menu__links">
        <Link to="/history" className="user-menu__link" onClick={onClose}>History</Link>
        <Link to="/bookmarks" className="user-menu__link" onClick={onClose}>Saved</Link>
        <Link to="/results" className="user-menu__link" onClick={onClose}>Results</Link>
      </div>

      <div className="user-menu__divider" />

      <div className="user-menu__settings">
        <div className="user-menu__section-title">Preferences</div>

        <div className="user-menu__row">
          <span>Dark Mode</span>
          <button
            className={`user-menu__toggle ${theme === 'dark' ? 'user-menu__toggle--active' : ''}`}
            onClick={toggleTheme}
            aria-label="Toggle dark mode"
          >
            <span className="user-menu__toggle-knob" />
          </button>
        </div>

        <div className="user-menu__row">
          <span>Font Size</span>
          <div className="user-menu__segmented user-menu__segmented--font">
            {[
              { key: 'sm', label: 'A', cls: 'user-menu__size-sm' },
              { key: 'md', label: 'A', cls: 'user-menu__size-md' },
              { key: 'lg', label: 'A', cls: 'user-menu__size-lg' },
            ].map(({ key, label, cls }) => (
              <button
                key={key}
                className={`user-menu__segment ${settings.fontSize === key ? 'user-menu__segment--active' : ''} ${cls}`}
                onClick={() => updateSetting('fontSize', key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="user-menu__row">
          <span>Serif Font</span>
          <button
            className={`user-menu__toggle ${settings.readingFont === 'serif' ? 'user-menu__toggle--active' : ''}`}
            onClick={() => updateSetting('readingFont', settings.readingFont === 'serif' ? 'sans-serif' : 'serif')}
            aria-label="Toggle serif font"
          >
            <span className="user-menu__toggle-knob" />
          </button>
        </div>

        <div className="user-menu__row">
          <span>Compact</span>
          <button
            className={`user-menu__toggle ${settings.contentDensity === 'compact' ? 'user-menu__toggle--active' : ''}`}
            onClick={() => updateSetting('contentDensity', settings.contentDensity === 'compact' ? 'comfortable' : 'compact')}
            aria-label="Toggle compact layout"
          >
            <span className="user-menu__toggle-knob" />
          </button>
        </div>

        <div className="user-menu__row">
          <span>Reduced Motion</span>
          <button
            className={`user-menu__toggle ${settings.reducedMotion ? 'user-menu__toggle--active' : ''}`}
            onClick={() => updateSetting('reducedMotion', !settings.reducedMotion)}
            aria-label="Toggle reduced motion"
          >
            <span className="user-menu__toggle-knob" />
          </button>
        </div>

        <div className="user-menu__row">
          <span>High Contrast</span>
          <button
            className={`user-menu__toggle ${settings.highContrast ? 'user-menu__toggle--active' : ''}`}
            onClick={() => updateSetting('highContrast', !settings.highContrast)}
            aria-label="Toggle high contrast"
          >
            <span className="user-menu__toggle-knob" />
          </button>
        </div>
      </div>

      <div className="user-menu__divider" />

      <button onClick={handleLogout} className="user-menu__signout">Sign out</button>
    </div>
  );
}

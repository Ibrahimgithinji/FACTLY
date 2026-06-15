import React, { useState, useEffect, useCallback } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import SearchOverlay from './SearchOverlay';
import ThemeToggle from './ThemeToggle';
import './Navbar.css';

const NAV_CATEGORIES = [
  { name: 'News', path: '/category/news' },
  { name: 'Startups', path: '/category/startups' },
  { name: 'Business', path: '/category/business' },
  { name: 'Reviews', path: '/category/reviews' },
  { name: 'Opinion', path: '/category/opinion' },
  { name: 'Fact Checks', path: '/verify' },
  { name: 'Explain', path: '/category/deep-dive' },
];

const getTodayLabel = () => new Intl.DateTimeFormat('en-US', {
  weekday: 'long',
  month: 'short',
  day: 'numeric',
  year: 'numeric',
}).format(new Date());

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  const handleScroll = useCallback(() => {
    setIsScrolled(window.scrollY > 8);
  }, []);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location]);

  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') setIsMobileMenuOpen(false);
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  useEffect(() => {
    document.body.style.overflow = isMobileMenuOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);

  const accountLinks = isAuthenticated
    ? [
        { path: '/history', label: 'History' },
        { path: '/bookmarks', label: 'Saved' },
        { path: '/results', label: 'Results' },
      ]
    : [];

  const handleLogout = () => {
    logout();
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <header className={`navbar ${isScrolled ? 'navbar--scrolled' : ''}`} role="banner">
        <div className="navbar__topbar">
          <div className="navbar__topbar-inner">
            <span>{getTodayLabel()}</span>
            <Link to="/verify" className="navbar__topbar-link">Verify a claim</Link>
            <Link to="/write-for-us" className="navbar__topbar-link">Submit a tip</Link>
            <Link to="/about" className="navbar__topbar-link">Community</Link>
          </div>
        </div>

        <div className="navbar__main">
          <div className="navbar__container">
            <Link to="/" className="navbar__logo" aria-label="FACTLY Home">
              <span className="navbar__logo-mark">F</span>
              <span className="navbar__logo-copy">
                <span className="navbar__logo-text">FACTLY</span>
                <span className="navbar__tagline">Verify. Understand. Share.</span>
              </span>
            </Link>

            <nav className="navbar__nav" role="navigation" aria-label="Editorial navigation">
              <ul className="navbar__menu">
                {NAV_CATEGORIES.map((item) => (
                  <li key={item.path} className="navbar__menu-item">
                    <NavLink
                      to={item.path}
                      className={({ isActive }) =>
                        `navbar__link ${isActive ? 'navbar__link--active' : ''}`
                      }
                    >
                      {item.label || item.name}
                    </NavLink>
                  </li>
                ))}
                {accountLinks.map((item) => (
                  <li key={item.path} className="navbar__menu-item navbar__menu-item--account">
                    <NavLink
                      to={item.path}
                      className={({ isActive }) =>
                        `navbar__link ${isActive ? 'navbar__link--active' : ''}`
                      }
                    >
                      {item.label}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </nav>

            <div className="navbar__actions">
              <button
                onClick={() => setSearchOpen(true)}
                className="navbar__icon-button"
                aria-label="Search articles"
              >
                <span className="navbar__search-icon" aria-hidden="true" />
              </button>
              <ThemeToggle />
              {isAuthenticated ? (
                <div className="navbar__user">
                  <span className="navbar__user-avatar" aria-hidden="true">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </span>
                  <button onClick={handleLogout} className="navbar__auth-button">Sign out</button>
                </div>
              ) : (
                <Link to="/login" className="navbar__auth-button">Sign in</Link>
              )}
              <Link to="/verify" className="navbar__verify-button">Verify</Link>
            </div>

            <button
              className={`navbar__toggle ${isMobileMenuOpen ? 'navbar__toggle--active' : ''}`}
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              aria-expanded={isMobileMenuOpen}
              aria-controls="mobile-menu"
              aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
            >
              <span className="navbar__toggle-bar" />
              <span className="navbar__toggle-bar" />
              <span className="navbar__toggle-bar" />
            </button>
          </div>
        </div>
      </header>

      <div
        className={`navbar__overlay ${isMobileMenuOpen ? 'navbar__overlay--active' : ''}`}
        onClick={() => setIsMobileMenuOpen(false)}
        aria-hidden="true"
      />

      <div
        id="mobile-menu"
        className={`navbar__mobile ${isMobileMenuOpen ? 'navbar__mobile--open' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label="Mobile navigation"
      >
        <div className="navbar__mobile-header">
          <Link to="/" className="navbar__mobile-logo">FACTLY</Link>
          <button
            className="navbar__mobile-close"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-label="Close menu"
          >
            Close
          </button>
        </div>

        <nav className="navbar__mobile-nav" role="navigation" aria-label="Mobile navigation">
          <button
            onClick={() => { setSearchOpen(true); setIsMobileMenuOpen(false); }}
            className="navbar__mobile-search"
          >
            Search Factly
          </button>
          <ul className="navbar__mobile-menu">
            <li className="navbar__mobile-item">
              <NavLink to="/" end className="navbar__mobile-link">Home</NavLink>
            </li>
            {NAV_CATEGORIES.map((item) => (
              <li key={item.path} className="navbar__mobile-item">
                <NavLink to={item.path} className="navbar__mobile-link">{item.name}</NavLink>
              </li>
            ))}
            {accountLinks.map((item) => (
              <li key={item.path} className="navbar__mobile-item">
                <NavLink to={item.path} className="navbar__mobile-link">{item.label}</NavLink>
              </li>
            ))}
          </ul>
          <div className="navbar__mobile-actions">
            <ThemeToggle />
            {isAuthenticated ? (
              <button onClick={handleLogout} className="navbar__mobile-button">Sign out</button>
            ) : (
              <Link to="/login" className="navbar__mobile-button">Sign in</Link>
            )}
          </div>
        </nav>
      </div>

      <SearchOverlay isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
};

export default Navbar;

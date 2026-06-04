import React, { useState, useEffect, useCallback } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import SearchOverlay from './SearchOverlay';
import ThemeToggle from './ThemeToggle';
import './Navbar.css';

/**
 * Enterprise-grade Navigation Component
 * 
 * Features:
 * - Responsive design with mobile hamburger menu
 * - Active route indicators
 * - Accessible keyboard navigation
 * - Smooth transitions and hover states
 * - Semantic HTML structure
 */

const NAV_CATEGORIES = [
  { name: 'News', slug: 'news' },
  { name: 'Reviews', slug: 'reviews' },
  { name: 'Startups', slug: 'startups' },
  { name: 'Business', slug: 'business' },
  { name: 'Opinion', slug: 'opinion' },
  { name: 'Deep Dive', slug: 'deep-dive' },
];

const SocialIcons = () => (
  <div className="navbar__social">
    <a href="https://twitter.com/factly" target="_blank" rel="noopener noreferrer" className="navbar__social-link" aria-label="Follow us on X">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    </a>
    <a href="https://facebook.com/factly" target="_blank" rel="noopener noreferrer" className="navbar__social-link" aria-label="Like us on Facebook">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
      </svg>
    </a>
    <a href="https://youtube.com/@factly" target="_blank" rel="noopener noreferrer" className="navbar__social-link" aria-label="Subscribe on YouTube">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
      </svg>
    </a>
    <a href="https://t.me/factly" target="_blank" rel="noopener noreferrer" className="navbar__social-link navbar__social-link--telegram" aria-label="Join our Telegram channel">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
      </svg>
    </a>
  </div>
);

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [searchOpen, setSearchOpen] = useState(false);

  // Handle scroll behavior for sticky header
  const handleScroll = useCallback(() => {
    const currentScrollY = window.scrollY;
    
    // Add shadow when scrolled
    setIsScrolled(currentScrollY > 10);
    
    // Hide navbar on scroll down (only after significant scroll distance)
    if (currentScrollY > lastScrollY && currentScrollY > 300) {
      setIsVisible(false);
    } else {
      setIsVisible(true);
    }
    
    setLastScrollY(currentScrollY);
  }, [lastScrollY]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location]);

  // Close mobile menu on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        setIsMobileMenuOpen(false);
      }
    };
    
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleLogout = () => {
    logout();
    setIsMobileMenuOpen(false);
  };

  const navItems = [
    { path: '/', label: 'Home', exact: true },
    { path: '/startups', label: 'Startups' },
    { path: '/verify', label: 'Verify' },
    { path: '/write-for-us', label: 'Write for Us' },
    { path: '/about', label: 'About' },
  ];

  if (isAuthenticated) {
    navItems.push(
      { path: '/results', label: 'Results' },
      { path: '/history', label: 'History' },
      { path: '/bookmarks', label: 'Saved' }
    );
  }

  return (
    <>
      <header 
        className={`navbar ${isScrolled ? 'navbar--scrolled' : ''} ${isVisible ? 'navbar--visible' : 'navbar--hidden'}`}
        role="banner"
      >
        <div className="navbar__container">
          {/* Logo Section */}
          <div className="navbar__brand">
            <Link to="/" className="navbar__logo" aria-label="FACTLY Home">
              <span className="navbar__logo-icon">✓</span>
              <span className="navbar__logo-text">FACTLY</span>
            </Link>
            <span className="navbar__tagline">Verify. Understand. Share.</span>
          </div>

          {/* Desktop Navigation */}
          <nav className="navbar__nav" role="navigation" aria-label="Main navigation">
            <ul className="navbar__menu">
              {navItems.map((item) => (
                <li key={item.path} className="navbar__menu-item">
                  <NavLink
                    to={item.path}
                    end={item.exact}
                    className={({ isActive }) => 
                      `navbar__link ${isActive ? 'navbar__link--active' : ''}`
                    }
                  >
                    <span className="navbar__link-text">{item.label}</span>
                  </NavLink>
                </li>
              ))}
              {/* Categories dropdown */}
              <li className="navbar__menu-item navbar__dropdown">
                <button className="navbar__link navbar__dropdown-trigger">
                  Categories
                  <span className="navbar__dropdown-arrow">▾</span>
                </button>
                <div className="navbar__dropdown-menu">
                  {NAV_CATEGORIES.map(cat => (
                    <Link key={cat.slug} to={`/category/${cat.slug}`} className="navbar__dropdown-item">
                      {cat.name}
                    </Link>
                  ))}
                </div>
              </li>
            </ul>
          </nav>

          {/* Actions */}
          <div className="navbar__actions">
            <SocialIcons />
            <a
              href="https://t.me/factly"
              target="_blank"
              rel="noopener noreferrer"
              className="navbar__telegram-btn"
              aria-label="Join our Telegram channel"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
              </svg>
              <span>Telegram</span>
            </a>
            <button
              onClick={() => setSearchOpen(true)}
              className="navbar__action-btn"
              aria-label="Search articles"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
            </button>
            <ThemeToggle />

            {/* Auth Section */}
            <div className="navbar__auth">
              {isAuthenticated ? (
                <div className="navbar__user">
                  <div className="navbar__user-info">
                    <span className="navbar__user-avatar">
                      {user?.name?.charAt(0).toUpperCase() || 'U'}
                    </span>
                    <span className="navbar__user-name">{user?.name}</span>
                  </div>
                  <button 
                    onClick={handleLogout}
                    className="navbar__button navbar__button--secondary"
                    aria-label="Sign out"
                  >
                    Sign Out
                  </button>
                </div>
              ) : (
                <div className="navbar__auth-actions">
                  <Link 
                    to="/login" 
                    className="navbar__button navbar__button--ghost"
                  >
                    Sign In
                  </Link>
                  <Link 
                    to="/signup" 
                    className="navbar__button navbar__button--primary"
                  >
                    Get Started
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Mobile Menu Toggle */}
          <button
            className={`navbar__toggle ${isMobileMenuOpen ? 'navbar__toggle--active' : ''}`}
            onClick={toggleMobileMenu}
            aria-expanded={isMobileMenuOpen}
            aria-controls="mobile-menu"
            aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
          >
            <span className="navbar__toggle-bar"></span>
            <span className="navbar__toggle-bar"></span>
            <span className="navbar__toggle-bar"></span>
          </button>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      <div 
        className={`navbar__overlay ${isMobileMenuOpen ? 'navbar__overlay--active' : ''}`}
        onClick={() => setIsMobileMenuOpen(false)}
        aria-hidden="true"
      />

      {/* Mobile Menu */}
      <div
        id="mobile-menu"
        className={`navbar__mobile ${isMobileMenuOpen ? 'navbar__mobile--open' : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label="Mobile navigation"
      >
        <div className="navbar__mobile-header">
          <span className="navbar__mobile-title">Menu</span>
          <button
            className="navbar__mobile-close"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-label="Close menu"
          >
            ✕
          </button>
        </div>

        <nav className="navbar__mobile-nav" role="navigation" aria-label="Mobile navigation">
          <ul className="navbar__mobile-menu">
            {navItems.map((item) => (
              <li key={item.path} className="navbar__mobile-item">
                <NavLink
                  to={item.path}
                  end={item.exact}
                  className={({ isActive }) => 
                    `navbar__mobile-link ${isActive ? 'navbar__mobile-link--active' : ''}`
                  }
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <span className="navbar__mobile-text">{item.label}</span>
                </NavLink>
              </li>
            ))}
            <li className="navbar__mobile-item">
              <span className="navbar__mobile-link navbar__mobile-link--label">Categories</span>
            </li>
            {NAV_CATEGORIES.map(cat => (
              <li key={cat.slug} className="navbar__mobile-item">
                <Link
                  to={`/category/${cat.slug}`}
                  className="navbar__mobile-link"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <span className="navbar__mobile-text">{cat.name}</span>
                </Link>
              </li>
            ))}
          </ul>
          <div className="navbar__mobile-actions">
            <button
              onClick={() => { setSearchOpen(true); setIsMobileMenuOpen(false); }}
              className="navbar__mobile-action-btn"
            >
              🔍 Search
            </button>
            <ThemeToggle />
          </div>
        </nav>

        <div className="navbar__mobile-footer">
          {isAuthenticated ? (
            <div className="navbar__mobile-user">
              <div className="navbar__mobile-user-info">
                <span className="navbar__mobile-avatar">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </span>
                <span className="navbar__mobile-username">{user?.name}</span>
              </div>
              <button 
                onClick={handleLogout}
                className="navbar__mobile-button navbar__mobile-button--logout"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <div className="navbar__mobile-auth">
              <Link 
                to="/login" 
                className="navbar__mobile-button navbar__mobile-button--secondary"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Sign In
              </Link>
              <Link 
                to="/signup" 
                className="navbar__mobile-button navbar__mobile-button--primary"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>

      <SearchOverlay isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
};

export default Navbar;

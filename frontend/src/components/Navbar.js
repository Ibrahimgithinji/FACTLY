import React, { useState, useEffect, useCallback } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
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

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  // Handle scroll behavior for sticky header
  const handleScroll = useCallback(() => {
    const currentScrollY = window.scrollY;
    
    // Add shadow when scrolled
    setIsScrolled(currentScrollY > 10);
    
    // Hide/show on scroll direction (optional - can be removed if always visible preferred)
    if (currentScrollY > lastScrollY && currentScrollY > 100) {
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

  // Navigation items based on auth state
  const getNavItems = () => {
    const items = [
      { path: '/', label: 'Verify', icon: '🔍', exact: true },
    ];

    if (isAuthenticated) {
      items.push(
        { path: '/results', label: 'Results', icon: '📊' },
        { path: '/history', label: 'History', icon: '📜' }
      );
    }

    items.push(
      { path: '/about', label: 'About', icon: 'ℹ️' }
    );

    return items;
  };

  const navItems = getNavItems();

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
            <span className="navbar__tagline">Truth Verification</span>
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
                    <span className="navbar__link-icon" aria-hidden="true">
                      {item.icon}
                    </span>
                    <span className="navbar__link-text">{item.label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>

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
                  <span className="navbar__button-icon">🚪</span>
                  <span className="navbar__button-text">Sign Out</span>
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
                  <span className="navbar__mobile-icon">{item.icon}</span>
                  <span className="navbar__mobile-text">{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
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
    </>
  );
};

export default Navbar;

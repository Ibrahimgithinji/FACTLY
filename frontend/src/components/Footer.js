import React from 'react';
import { Link } from 'react-router-dom';
import NewsletterSignup from './NewsletterSignup';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="footer">
      {/* Telegram CTA Banner */}
      <div className="footer__telegram-banner">
        <div className="footer__telegram-inner">
          <div className="footer__telegram-content">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="footer__telegram-icon">
              <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
            </svg>
            <div>
              <h4>Join us on Telegram</h4>
              <p>Catch the Kenyan tech conversation on Telegram.</p>
            </div>
          </div>
          <a href="https://t.me/factly" target="_blank" rel="noopener noreferrer" className="footer__telegram-btn">
            Join on Telegram
          </a>
        </div>
      </div>

      <div className="footer__inner">
        <div className="footer__main">
          <div className="footer__brand">
            <h3 className="footer__logo">
              <span className="footer__logo-icon">✓</span>
              FACTLY
            </h3>
            <p className="footer__tagline">Verifying claims, tracking tech, keeping you informed with real-time fact-checking and in-depth analysis.</p>
            <div className="footer__social">
              <a href="https://twitter.com/factly" target="_blank" rel="noopener noreferrer" className="footer__social-link" aria-label="Follow us on X">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
              </a>
              <a href="https://facebook.com/factly" target="_blank" rel="noopener noreferrer" className="footer__social-link" aria-label="Like us on Facebook">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
              </a>
              <a href="https://youtube.com/@factly" target="_blank" rel="noopener noreferrer" className="footer__social-link" aria-label="Subscribe on YouTube">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
              </a>
              <a href="https://t.me/factly" target="_blank" rel="noopener noreferrer" className="footer__social-link footer__social-link--telegram" aria-label="Join our Telegram channel">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>
              </a>
            </div>
          </div>

          <div className="footer__newsletter">
            <h4 className="footer__col-title">Subscribe to our newsletter</h4>
            <p className="footer__newsletter-desc">Get the latest fact-checks and analysis delivered to your inbox.</p>
            <NewsletterSignup variant="inline" />
          </div>
        </div>

        <div className="footer__links">
          <div className="footer__col">
            <h4 className="footer__col-title">Categories</h4>
            <Link to="/category/news">News</Link>
            <Link to="/category/reviews">Reviews</Link>
            <Link to="/category/startups">Startups</Link>
            <Link to="/category/business">Business</Link>
            <Link to="/category/opinion">Opinion</Link>
          </div>
          <div className="footer__col">
            <h4 className="footer__col-title">More</h4>
            <Link to="/category/how-to">How-To</Link>
            <Link to="/category/interesting-reads">Interesting Reads</Link>
            <Link to="/category/deep-dive">Deep Dive</Link>
            <Link to="/category/quick-check">Quick Check</Link>
          </div>
          <div className="footer__col">
            <h4 className="footer__col-title">Useful Links</h4>
            <Link to="/verify">Verification Tool</Link>
            <Link to="/login">Sign In</Link>
            <Link to="/signup">Create Account</Link>
            <Link to="/about">About Us</Link>
          </div>
        </div>
      </div>
      <div className="footer__bottom">
        <span>&copy; {new Date().getFullYear()} FACTLY. All rights reserved.</span>
        <div className="footer__bottom-links">
          <Link to="/privacy-policy">Privacy Policy</Link>
          <Link to="/disclaimer">Disclaimer</Link>
        </div>
      </div>
    </footer>
  );
}

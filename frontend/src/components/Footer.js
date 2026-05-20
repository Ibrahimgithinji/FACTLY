import React from 'react';
import { Link } from 'react-router-dom';
import NewsletterSignup from './NewsletterSignup';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer__inner">
        <div className="footer__brand">
          <h3 className="footer__logo">FACTLY</h3>
          <p className="footer__tagline">Verifying claims, tracking tech, keeping you informed.</p>
        </div>

        <div className="footer__newsletter">
          <h4 className="footer__col-title">Subscribe to our newsletter</h4>
          <NewsletterSignup variant="inline" />
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
          </div>
        </div>
      </div>
      <div className="footer__bottom">
        <span>&copy; {new Date().getFullYear()} FACTLY. All rights reserved.</span>
      </div>
    </footer>
  );
}

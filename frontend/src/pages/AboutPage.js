import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './AboutPage.css';

export default function AboutPage() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('/api/content/analytics/dashboard/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
      },
    })
      .then((r) => r.ok ? r.json() : null)
      .then((data) => {
        if (data) {
          setStats({
            articles: data.articles.published,
            categories: data.articles.categories,
            subscribers: data.subscribers.total,
            views: data.page_views.total,
          });
        }
      })
      .catch(() => {});
  }, []);

  return (
    <div className="about-page">
      {/* Hero */}
      <div className="about-hero">
        <h1>About Factly</h1>
        <p className="tagline">Tech News &bull; Verification &bull; Startup Stories</p>
        <p className="description">
          Factly is your trusted source for technology news, startup coverage, and fact verification.
          We combine original journalism with AI-powered analysis to help you navigate the
          information landscape with confidence.
        </p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="about-stats">
          <div className="about-stat">
            <p className="number">{stats.articles}+</p>
            <p className="label">Articles Published</p>
          </div>
          <div className="about-stat">
            <p className="number">{stats.categories}</p>
            <p className="label">Categories</p>
          </div>
          <div className="about-stat">
            <p className="number">{stats.subscribers}</p>
            <p className="label">Newsletter Subscribers</p>
          </div>
          <div className="about-stat">
            <p className="number">{stats.views.toLocaleString()}+</p>
            <p className="label">Page Views</p>
          </div>
        </div>
      )}

      {/* What We Offer */}
      <div className="about-section">
        <h2><span className="emoji">📰</span> What We Offer</h2>
        <p>Factly covers the full spectrum of technology with original content across ten categories.</p>
        <div className="offer-grid">
          <div className="offer-card">
            <span className="icon">📰</span>
            <h3>Tech News & Analysis</h3>
            <p>Daily coverage of the technology landscape — from African startups to global tech giants, with original reporting and curated analysis.</p>
          </div>
          <div className="offer-card">
            <span className="icon">🚀</span>
            <h3>Startup Spotlight</h3>
            <p>Dedicated coverage of emerging startups, founder interviews, funding news, and the innovations shaping tomorrow's economy.</p>
          </div>
          <div className="offer-card">
            <span className="icon">🔍</span>
            <h3>Fact Verification</h3>
            <p>AI-powered verification tool that cross-references claims against multiple fact-checking databases and returns a Factly Score from 0-100.</p>
          </div>
          <div className="offer-card">
            <span className="icon">📬</span>
            <h3>Newsletter</h3>
            <p>Weekly digest of the most important stories and verifications, delivered straight to your inbox.</p>
          </div>
          <div className="offer-card">
            <span className="icon">💬</span>
            <h3>Community</h3>
            <p>Comment on articles, bookmark stories for later, and submit guest articles to share your voice with our audience.</p>
          </div>
          <div className="offer-card">
            <span className="icon">📊</span>
            <h3>Factly Score</h3>
            <p>Our proprietary scoring algorithm analyzes source credibility, evidence quality, content analysis, and cross-references to rate claims.</p>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="about-section">
        <h2><span className="emoji">⚡</span> How Verification Works</h2>
        <div className="about-two-col">
          <div className="col">
            <h3>📥 1. Submit</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              Paste a claim or article URL into our verification tool. Our system extracts the
              core claims and prepares them for analysis.
            </p>
          </div>
          <div className="col">
            <h3>🤖 2. Analyze</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              NLP technology detects bias, sentiment, and credibility indicators while our
              fact-checking service cross-references against multiple sources.
            </p>
          </div>
          <div className="col">
            <h3>📊 3. Score</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              The Factly Score is calculated from four weighted components: Fact-Check Consensus (45%),
              Source Credibility (25%), Evidence Quality (20%), and Content Analysis (10%).
            </p>
          </div>
          <div className="col">
            <h3>📋 4. Review</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              Get a detailed breakdown with evidence from multiple sources, credibility assessments,
              and clear classifications — Likely Fake, Uncertain, or Likely Authentic.
            </p>
          </div>
        </div>
      </div>

      {/* Content Platform */}
      <div className="about-section">
        <h2><span className="emoji">📚</span> Content Categories</h2>
        <p>We publish across seven content categories and three dedicated verification categories.</p>
        <div className="about-two-col">
          <div className="col">
            <h3>📱 Blog Categories</h3>
            <ul>
              <li>News — Breaking tech news and analysis</li>
              <li>Reviews — In-depth product and service reviews</li>
              <li>Startups — Startup stories, funding, and founder interviews</li>
              <li>Business — Tech business strategy and market analysis</li>
              <li>Opinion — Expert perspectives on tech trends</li>
              <li>How-To — Practical guides and tutorials</li>
              <li>Interesting Reads — Curated stories worth your time</li>
            </ul>
          </div>
          <div className="col">
            <h3>✅ Verification Categories</h3>
            <ul>
              <li>Verified Claims — Claims that have been fact-checked</li>
              <li>Deep Dive — In-depth investigation of complex claims</li>
              <li>Quick Check — Rapid verification of trending claims</li>
            </ul>
            <h3 style={{ marginTop: 16 }}>📡 RSS Sources</h3>
            <ul>
              <li>TechCrunch, Ars Technica, WIRED</li>
              <li>Techpoint Africa, TechCabal</li>
              <li>Benjamin Dada, African Business</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Score Classifications */}
      <div className="about-section">
        <h2><span className="emoji">🎯</span> Score Classifications</h2>
        <p>Every verification returns a Factly Score that falls into one of three classifications:</p>
        <div className="about-two-col">
          <div className="col" style={{ borderLeft: '4px solid #ef4444' }}>
            <h3 style={{ color: '#ef4444' }}>0-35 &mdash; Likely Fake</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              High likelihood of misinformation or false claims. Multiple fact-checking sources
              contradict the claim or strong evidence of fabrication exists.
            </p>
          </div>
          <div className="col" style={{ borderLeft: '4px solid #eab308' }}>
            <h3 style={{ color: '#eab308' }}>36-65 &mdash; Uncertain</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              Insufficient evidence or mixed signals from sources. The claim may contain elements
              of truth alongside misleading information.
            </p>
          </div>
          <div className="col" style={{ borderLeft: '4px solid #22c55e' }}>
            <h3 style={{ color: '#22c55e' }}>66-100 &mdash; Likely Authentic</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
              Strong evidence supporting the claim's accuracy. Multiple credible sources
              corroborate the information with high confidence.
            </p>
          </div>
        </div>
      </div>

      {/* Team */}
      <div className="about-section">
        <h2><span className="emoji">👥</span> Our Team</h2>
        <p>Factly is built by a small team passionate about technology, journalism, and the fight against misinformation.</p>
        <div className="team-grid">
          <div className="team-card">
            <div className="avatar">IG</div>
            <h3>Ibrahim Gitau</h3>
            <p className="role">Founder & Developer</p>
          </div>
          <div className="team-card">
            <div className="avatar">AI</div>
            <h3>Factly AI</h3>
            <p className="role">Verification Engine</p>
          </div>
          <div className="team-card">
            <div className="avatar">📡</div>
            <h3>RSS Sources</h3>
            <p className="role">Content Partners</p>
          </div>
          <div className="team-card">
            <div className="avatar">🌍</div>
            <h3>Our Readers</h3>
            <p className="role">Community</p>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="about-cta">
        <h2>Ready to explore?</h2>
        <p>Join thousands of readers staying informed with verified tech news.</p>
        <div className="cta-buttons">
          <Link to="/" className="cta-btn primary">Browse Articles</Link>
          <Link to="/verify" className="cta-btn secondary">Verify a Claim</Link>
          <Link to="/write-for-us" className="cta-btn secondary">Write for Us</Link>
        </div>
      </div>
    </div>
  );
}

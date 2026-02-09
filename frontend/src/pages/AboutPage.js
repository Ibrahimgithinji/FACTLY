import React from 'react';
import './Auth.css';
import './AboutPage.css';

const AboutPage = () => {
  return (
    <div className="auth-container">
      <div className="auth-card about-card">
        <div className="auth-header">
          <h1>About FACTLY</h1>
          <p>AI-Powered News Credibility Verification</p>
        </div>

        <div className="about-content">
          <section className="about-section">
            <h2>Our Mission</h2>
            <p>
              FACTLY is dedicated to combating misinformation by providing users with 
              powerful tools to verify the credibility of news content. We combine 
              advanced AI technology with multiple fact-checking sources to deliver 
              accurate, unbiased assessments of news claims.
            </p>
          </section>

          <section className="about-section">
            <h2>How It Works</h2>
            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon" aria-hidden="true">🔍</div>
                <h3>Multi-Source Verification</h3>
                <p>
                  FACTLY cross-references claims against multiple fact-checking databases 
                  including Google Fact Check API and NewsLdr to provide comprehensive verification.
                </p>
              </div>
              <div className="feature-card">
                <div className="feature-icon" aria-hidden="true">📊</div>
                <h3>Factly Score™</h3>
                <p>
                  Our proprietary scoring algorithm analyzes multiple factors including 
                  source credibility, evidence quality, and content analysis to provide 
                  a comprehensive credibility score from 0-100.
                </p>
              </div>
              <div className="feature-card">
                <div className="feature-icon" aria-hidden="true">🤖</div>
                <h3>AI-Powered Analysis</h3>
                <p>
                  Advanced NLP technology detects bias, sensationalism, and credibility 
                  indicators in text content to provide deeper insights.
                </p>
              </div>
              <div className="feature-card">
                <div className="feature-icon" aria-hidden="true">📚</div>
                <h3>Evidence-Based Results</h3>
                <p>
                  Every verification includes detailed evidence from multiple sources, 
                  giving users the context they need to make informed decisions.
                </p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>Scoring Methodology</h2>
            <p>The Factly Score™ is calculated using four key components:</p>
            <ul className="methodology-list">
              <li>
                <strong>Fact-Check Consensus (45%)</strong> - 
                Weighted analysis of verdicts from multiple fact-checking organizations
              </li>
              <li>
                <strong>Source Credibility (25%)</strong> - 
                Assessment of the reliability and track record of information sources
              </li>
              <li>
                <strong>Evidence Quality (20%)</strong> - 
                Evaluation of the quantity and quality of supporting evidence
              </li>
              <li>
                <strong>Content Analysis (10%)</strong> - 
                AI-driven detection of bias, sensationalism, and credibility indicators
              </li>
            </ul>
          </section>

          <section className="about-section">
            <h2>Score Classifications</h2>
            <div className="classifications-grid">
              <div className="classification-card likely-fake">
                <span className="score-range">0-35</span>
                <h3>Likely Fake</h3>
                <p>High likelihood of misinformation or false claims</p>
              </div>
              <div className="classification-card uncertain">
                <span className="score-range">36-65</span>
                <h3>Uncertain</h3>
                <p>Insufficient evidence or mixed signals from sources</p>
              </div>
              <div className="classification-card likely-authentic">
                <span className="score-range">66-100</span>
                <h3>Likely Authentic</h3>
                <p>Strong evidence supporting the claim's accuracy</p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>Trusted Sources</h2>
            <p>
              FACTLY integrates with leading fact-checking organizations and news 
              verification services to provide comprehensive coverage:
            </p>
            <div className="sources-list">
              <div className="source-item">
                <span className="source-icon" aria-hidden="true">🔗</span>
                <span>Google Fact Check API</span>
              </div>
              <div className="source-item">
                <span className="source-icon" aria-hidden="true">📰</span>
                <span>NewsLdr API</span>
              </div>
              <div className="source-item">
                <span className="source-icon" aria-hidden="true">🔒</span>
                <span>Direct Source Verification</span>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>Limitations</h2>
            <p>
              While FACTLY provides valuable insights, users should be aware of certain 
              limitations:
            </p>
            <ul className="limitations-list">
              <li>AI-powered analysis may not catch all forms of misinformation</li>
              <li>Fact-checking coverage varies by topic and language</li>
              <li>Scores should be considered alongside human judgment</li>
              <li>New or emerging claims may have limited verification data</li>
            </ul>
          </section>

          <section className="about-section">
            <h2>Technology Stack</h2>
            <div className="tech-stack">
              <div className="tech-category">
                <h3>Frontend</h3>
                <ul>
                  <li>React 18</li>
                  <li>React Router 6</li>
                  <li>CSS Custom Properties</li>
                </ul>
              </div>
              <div className="tech-category">
                <h3>Backend</h3>
                <ul>
                  <li>Python/Django</li>
                  <li>REST Framework</li>
                  <li>Fact-Checking APIs</li>
                </ul>
              </div>
              <div className="tech-category">
                <h3>AI & NLP</h3>
                <ul>
                  <li>Natural Language Processing</li>
                  <li>Sentiment Analysis</li>
                  <li>Bias Detection</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>Contact & Support</h2>
            <p>
              For questions, feedback, or support, please reach out through 
              our official channels. We're committed to continuously improving 
              FACTLY to better serve our users in the fight against misinformation.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;

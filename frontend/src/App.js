import React, { Suspense, lazy, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ResultsProvider } from './context/ResultsContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import ErrorBoundary from './components/ErrorBoundary';
import { setupChunkErrorRecovery } from './utils/chunkRecovery';
import './App.css';

// Initialize chunk error recovery for HMR
setupChunkErrorRecovery();

// Lazy load components for code splitting
// React-scripts webpack config supports basic code splitting with lazy()
const VerificationForm = lazy(() => import('./components/VerificationForm'));
const ScoreDisplay = lazy(() => import('./components/ScoreDisplay'));
const EvidencePanel = lazy(() => import('./components/EvidencePanel'));
const CredibilityChart = lazy(() => import('./components/CredibilityChart'));
const TrendingTopics = lazy(() => import('./components/TrendingTopics'));
const RealTimeVerification = lazy(() => import('./components/RealTimeVerification'));
const EnhancedVerification = lazy(() => import('./components/EnhancedVerification'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const SignupPage = lazy(() => import('./pages/SignupPage'));
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPasswordPage'));
const ResetPasswordPage = lazy(() => import('./pages/ResetPasswordPage'));
const HistoryPage = lazy(() => import('./pages/HistoryPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));

// Loading fallback component
const PageLoader = () => (
  <div className="loading-container" role="status" aria-live="polite">
    <div className="loading-spinner" aria-hidden="true"></div>
    <p className="loading-text">Loading...</p>
  </div>
);

// Results page component
const ResultsPage = () => (
  <div className="results-container">
    <ScoreDisplay />
    <EnhancedVerification />
    <RealTimeVerification />
    <div className="results-grid">
      <EvidencePanel />
      <CredibilityChart />
    </div>
  </div>
);

// Home page with trending topics
const HomePage = () => {
  const [selectedTopic, setSelectedTopic] = useState('');

  const handleTopicClick = (topic) => {
    setSelectedTopic(topic);

    const formSection = document.getElementById('verification-form-section');
    if (formSection) {
      formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="home-container">
      <section className="home-hero">
        <div className="hero-copy">
          <span className="hero-eyebrow">Fact checking workspace</span>
          <h1>Verify fast-moving stories before they spread.</h1>
          <p>
            Run a credibility check, review supporting evidence, and use the trending
            stream to inspect the stories people are talking about right now.
          </p>
          <div className="hero-metrics" aria-label="Factly highlights">
            <div className="hero-metric">
              <strong>Live</strong>
              <span>Trending topics feed</span>
            </div>
            <div className="hero-metric">
              <strong>Multi-source</strong>
              <span>Evidence-led scoring</span>
            </div>
            <div className="hero-metric">
              <strong>Instant</strong>
              <span>Verification workflow</span>
            </div>
          </div>
        </div>

        <aside className="hero-panel">
          <h2>How to use Factly</h2>
          <ol className="hero-steps">
            <li>Paste a headline, article text, or URL into the verifier.</li>
            <li>Use Trending Topics to prefill the form with a current story.</li>
            <li>Review the score, evidence, and source credibility before sharing.</li>
          </ol>
        </aside>
      </section>

      <section id="verification-form-section" className="home-primary-section">
        <VerificationForm initialValue={selectedTopic} />
      </section>

      <section className="home-secondary-section">
        <TrendingTopics onTopicClick={handleTopicClick} />
      </section>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <ResultsProvider>
        <Router future={{ v7_relativeSplatPath: true }}>
          <div className="App">
            <Navbar />
            <main id="main-content" className="app-main" role="main">
              <ErrorBoundary>
                <Suspense fallback={<PageLoader />}>
                <Routes>
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/signup" element={<SignupPage />} />
                  <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                  <Route path="/reset-password/:token" element={<ResetPasswordPage />} />
                  <Route 
                    path="/" 
                    element={
                      <ProtectedRoute>
                        <HomePage />
                      </ProtectedRoute>
                    } 
                  />
                  {/* previously there was a dedicated /verify route; it's still available but now the form is shown on home page too */}
                  <Route 
                    path="/verify" 
                    element={
                      <ProtectedRoute>
                        <VerificationForm />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/results" 
                    element={
                      <ProtectedRoute>
                        <ResultsPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route 
                    path="/history" 
                    element={
                      <ProtectedRoute>
                        <HistoryPage />
                      </ProtectedRoute>
                    } 
                  />
                  <Route path="/about" element={<AboutPage />} />
                  <Route 
                    path="*" 
                    element={
                      <div className="error-container" role="alert">
                        <div className="error-icon" aria-hidden="true">404</div>
                        <h1 className="error-title">Page Not Found</h1>
                        <p className="error-message">
                          The page you're looking for doesn't exist or has been moved.
                        </p>
                      </div>
                    } 
                  />
                </Routes>
                </Suspense>
                </ErrorBoundary>
          </main>
        </div>
      </Router>
    </ResultsProvider>
    </AuthProvider>
  );
}

export default App;

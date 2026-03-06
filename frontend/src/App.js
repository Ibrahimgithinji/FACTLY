import React, { Suspense, lazy, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
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
    {/* add real-time verification panel under the score for richer context */}
    <RealTimeVerification />
    <div className="results-grid">
      <EvidencePanel />
      <CredibilityChart />
    </div>
  </div>
);

// Home page with trending topics
const HomePage = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  
  const handleTopicClick = (topic) => {
    setSearchQuery(topic);
    // Navigate to verification with the topic
    navigate('/results', { state: { topic } });
  };
  
  return (
    <div className="home-container">
      {/* verification form is now part of the home landing page */}
      <VerificationForm />
      <TrendingTopics onTopicClick={handleTopicClick} />
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router future={{ v7_relativeSplatPath: true }}>
        <div className="App">
          <Navbar />
          <main id="main-content" className="app-main" role="main">
            <Suspense fallback={<PageLoader />}>
              <ErrorBoundary>
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
              </ErrorBoundary>
            </Suspense>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;

import React, { Suspense, lazy, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ResultsProvider } from './context/ResultsContext';
import { ThemeProvider } from './context/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import { setupChunkErrorRecovery } from './utils/chunkRecovery';
import './App.css';

setupChunkErrorRecovery();

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
const HomePage = lazy(() => import('./pages/HomePage'));
const CategoryPage = lazy(() => import('./pages/CategoryPage'));
const ArticlePage = lazy(() => import('./pages/ArticlePage'));
const GuestSubmitPage = lazy(() => import('./pages/GuestSubmitPage'));
const BookmarksPage = lazy(() => import('./pages/BookmarksPage'));

const PageLoader = () => (
  <div className="loading-container" role="status" aria-live="polite">
    <div className="loading-spinner" aria-hidden="true"></div>
    <p className="loading-text">Loading...</p>
  </div>
);

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

function App() {
  return (
    <AuthProvider>
      <ResultsProvider>
        <ThemeProvider>
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
                    <Route path="/category/:slug" element={<CategoryPage />} />
                    <Route path="/article/:slug" element={<ArticlePage />} />
                    <Route path="/about" element={<AboutPage />} />
                    <Route path="/write-for-us" element={<GuestSubmitPage />} />
                    <Route path="/bookmarks" element={<BookmarksPage />} />
                    <Route
                      path="/"
                      element={
                        <HomePage />
                      }
                    />
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
            <Footer />
          </div>
        </Router>
      </ThemeProvider>
    </ResultsProvider>
    </AuthProvider>
  );
}

export default App;

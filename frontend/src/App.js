import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from './context/AuthContext';
import { ResultsProvider } from './context/ResultsContext';
import { ThemeProvider } from './context/ThemeContext';
import { SettingsProvider } from './context/SettingsContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import InstallPrompt from './components/InstallPrompt';
import PushNotificationPrompt from './components/PushNotificationPrompt';
import { setupChunkErrorRecovery } from './utils/chunkRecovery';
import './App.css';

setupChunkErrorRecovery();

const VerificationForm = lazy(() => import('./components/VerificationForm'));
const ScoreDisplay = lazy(() => import('./components/ScoreDisplay'));
const EvidencePanel = lazy(() => import('./components/EvidencePanel'));
const CredibilityChart = lazy(() => import('./components/CredibilityChart'));
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
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const AuthorPage = lazy(() => import('./pages/AuthorPage'));
const StartupsPage = lazy(() => import('./pages/StartupsPage'));
const SearchResultsPage = lazy(() => import('./pages/SearchResultsPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));

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
          <SettingsProvider>
          <HelmetProvider>
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
                    <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
                    <Route path="/author/:id" element={<AuthorPage />} />
                    <Route path="/startups" element={<StartupsPage />} />
                    <Route path="/search" element={<SearchResultsPage />} />
                    <Route path="/dashboard" element={<AdminDashboard />} />
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
                    <Route path="*" element={<NotFoundPage />} />
                  </Routes>
                  </Suspense>
                  </ErrorBoundary>
            </main>
            <Footer />
            <InstallPrompt />
            <PushNotificationPrompt />
          </div>
        </Router>
        </HelmetProvider>
          </SettingsProvider>
        </ThemeProvider>
    </ResultsProvider>
    </AuthProvider>
  );
}

export default App;

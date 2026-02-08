# FACTLY Technical Specification & Implementation Plan

## Executive Summary

This document provides a comprehensive technical specification for FACTLY, a professional-grade misinformation verification platform. The specification addresses all aspects of platform integrity, from frontend architecture to accessibility compliance, ensuring FACTLY delivers a flawless user experience that reflects its role as an authoritative source verification platform.

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FACTLY Platform                          │
├─────────────────────────────────────────────────────────────────┤
│  Presentation Layer (React 18 + TypeScript)                     │
│  ├── Components (Modular, Scoped Styles)                        │
│  ├── Pages (Route-Based Code Splitting)                         │
│  ├── Hooks (Custom Business Logic)                              │
│  └── Contexts (State Management)                                │
├─────────────────────────────────────────────────────────────────┤
│  API Gateway Layer (Django REST Framework)                       │
│  ├── Authentication & Authorization                              │
│  ├── Rate Limiting (10 requests/hour/IP)                         │
│  ├── Request Validation & Sanitization                           │
│  └── Response Serialization                                      │
├─────────────────────────────────────────────────────────────────┤
│  Service Layer                                                   │
│  ├── Fact Checking Service (Multi-source orchestration)          │
│  ├── NLP Service (Text preprocessing, claim extraction)           │
│  ├── Scoring Service (Factly Score™ algorithm)                    │
│  └── Caching Service (Redis-compatible caching)                   │
├─────────────────────────────────────────────────────────────────┤
│  External Integrations                                            │
│  ├── Google Fact Check API                                       │
│  ├── NewsLdr API                                                 │
│  └── Content Extraction Services                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| Frontend | React | 18.x | UI Framework |
| Frontend | TypeScript | 5.x | Type Safety |
| Frontend | React Router | 6.x | Routing |
| Frontend | Axios | 1.x | HTTP Client |
| Backend | Django | 4.x | API Framework |
| Backend | Django REST Framework | 3.x | REST API |
| Database | SQLite (dev) / PostgreSQL (prod) | - | Data Persistence |
| Caching | Redis (or in-memory fallback) | 7.x | Response Caching |
| NLP | NLTK | 3.8 | Text Processing |
| NLP | scikit-learn | 1.3 | ML Features |

---

## 2. Frontend Architecture Specification

### 2.1 Component Architecture

#### 2.1.1 Atomic Design System

```
frontend/src/components/
├── atoms/
│   ├── Button/
│   │   ├── Button.jsx
│   │   ├── Button.css
│   │   ├── Button.test.jsx
│   │   └── index.js
│   ├── Input/
│   │   ├── Input.jsx
│   │   ├── Input.css
│   │   └── index.js
│   ├── Label/
│   │   ├── Label.jsx
│   │   ├── Label.css
│   │   └── index.js
│   ├── Icon/
│   │   ├── Icon.jsx
│   │   ├── Icon.css
│   │   └── index.js
│   └── Badge/
│       ├── Badge.jsx
│       ├── Badge.css
│       └── index.js
├── molecules/
│   ├── FormField/
│   │   ├── FormField.jsx
│   │   ├── FormField.css
│   │   └── index.js
│   ├── SearchBar/
│   │   ├── SearchBar.jsx
│   │   ├── SearchBar.css
│   │   └── index.js
│   └── Card/
│       ├── Card.jsx
│       ├── Card.css
│       └── index.js
├── organisms/
│   ├── VerificationForm/
│   │   ├── VerificationForm.jsx
│   │   ├── VerificationForm.css
│   │   └── index.js
│   ├── ScoreDisplay/
│   │   ├── ScoreDisplay.jsx
│   │   ├── ScoreDisplay.css
│   │   └── index.js
│   └── EvidencePanel/
│       ├── EvidencePanel.jsx
│       ├── EvidencePanel.css
│       └── index.js
├── templates/
│   ├── MainLayout/
│   │   ├── MainLayout.jsx
│   │   ├── MainLayout.css
│   │   └── index.js
│   └── VerificationPage/
│       ├── VerificationPage.jsx
│       ├── VerificationPage.css
│       └── index.js
└── pages/
    ├── HomePage/
    ├── VerificationPage/
    ├── ResultsPage/
    └── AuthPage/
```

#### 2.1.2 Component Props Interface

```typescript
// Example: Button Component Props
interface ButtonProps {
  /** Button variant */
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  /** Button size */
  size?: 'small' | 'medium' | 'large';
  /** Button type */
  type?: 'button' | 'submit' | 'reset';
  /** Disabled state */
  disabled?: boolean;
  /** Loading state */
  loading?: boolean;
  /** Full width */
  fullWidth?: boolean;
  /** Click handler */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  /** Button content */
  children: React.ReactNode;
  /** Accessibility label */
  ariaLabel?: string;
  /** Icon to display */
  icon?: React.ReactNode;
  /** Icon position */
  iconPosition?: 'left' | 'right';
}
```

### 2.2 CSS Architecture

#### 2.2.1 CSS Modules with BEM Naming Convention

```css
/* Button.css - Scoped styles with BEM naming */
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
  border-radius: 8px;
  font-family: var(--font-family-primary);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-duration-base) ease;
  position: relative;
  overflow: hidden;
}

.button--primary {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.button--primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-medium);
}

.button--primary:active:not(:disabled) {
  transform: translateY(0);
}

.button--medium {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  line-height: 1.5;
}

.button__icon {
  display: inline-flex;
  flex-shrink: 0;
}

.button__spinner {
  width: 1.25rem;
  height: 1.25rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .button--medium {
    padding: 0.625rem 1.25rem;
    font-size: 0.875rem;
  }
}
```

#### 2.2.2 Design Tokens (CSS Custom Properties)

```css
/* design-tokens.css - Global design tokens */
:root {
  /* Colors - Professional Palette */
  --color-primary: #2563eb;
  --color-primary-light: #3b82f6;
  --color-primary-dark: #1d4ed8;
  --color-primary-subtle: #eff6ff;
  
  --color-secondary: #64748b;
  --color-secondary-light: #94a3b8;
  --color-secondary-dark: #475569;
  
  --color-success: #10b981;
  --color-success-light: #34d399;
  --color-success-dark: #059669;
  
  --color-warning: #f59e0b;
  --color-warning-light: #fbbf24;
  --color-warning-dark: #d97706;
  
  --color-error: #ef4444;
  --color-error-light: #f87171;
  --color-error-dark: #dc2626;
  
  --color-info: #0ea5e9;
  --color-info-light: #38bdf8;
  --color-info-dark: #0284c7;
  
  /* Semantic Colors */
  --color-text-primary: #1e293b;
  --color-text-secondary: #64748b;
  --color-text-tertiary: #94a3b8;
  --color-text-inverse: #ffffff;
  
  --color-background-primary: #ffffff;
  --color-background-secondary: #f8fafc;
  --color-background-tertiary: #f1f5f9;
  
  --color-border-light: #e2e8f0;
  --color-border-medium: #cbd5e1;
  --color-border-dark: #94a3b8;
  
  /* Credibility Score Colors */
  --score-high: #10b981;
  --score-medium: #f59e0b;
  --score-low: #ef4444;
  --score-unknown: #64748b;
  
  /* Typography */
  --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  --font-size-4xl: 2.25rem;   /* 36px */
  
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  --line-height-tight: 1.25;
  --line-height-base: 1.5;
  --line-height-relaxed: 1.75;
  
  /* Spacing */
  --spacing-xs: 0.25rem;   /* 4px */
  --spacing-sm: 0.5rem;    /* 8px */
  --spacing-md: 1rem;      /* 16px */
  --spacing-lg: 1.5rem;    /* 24px */
  --spacing-xl: 2rem;      /* 32px */
  --spacing-2xl: 3rem;     /* 48px */
  --spacing-3xl: 4rem;     /* 64px */
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  
  /* Transitions */
  --transition-duration-fast: 150ms;
  --transition-duration-base: 250ms;
  --transition-duration-slow: 400ms;
  --transition-timing-ease: ease;
  --transition-timing-ease-in-out: ease-in-out;
  
  /* Z-Index */
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-fixed: 300;
  --z-modal-backdrop: 400;
  --z-modal: 500;
  --z-popover: 600;
  --z-tooltip: 700;
}
```

### 2.3 Critical Rendering Path Optimization

#### 2.3.1 CSS Loading Strategy

```javascript
// webpack.config.js - Optimized CSS extraction
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: {
              modules: {
                mode: 'local',
                auto: true,
                localIdentName: '[hash:base64:8]',
              },
            },
          },
          {
            loader: 'postcss-loader',
            options: {
              plugins: [
                'postcss-preset-env',
                'autoprefixer',
              ],
            },
          },
        ],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash:8].css',
      chunkFilename: '[name].[contenthash:8].chunk.css',
    }),
  ],
  optimization: {
    splitChunks: {
      cacheGroups: {
        styles: {
          name: 'styles',
          type: 'css/mini-extract',
          chunks: 'all',
          enforce: true,
        },
      },
    },
  },
};
```

#### 2.3.2 FOUC Prevention

```html
<!-- public/index.html - Preload critical CSS -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#2563eb" />
  <meta name="description" content="FACTLY - AI-Powered News Credibility Verification" />
  
  <!-- Preload critical fonts -->
  <link 
    rel="preload" 
    href="/fonts/inter-var.woff2" 
    as="font" 
    type="font/woff2" 
    crossorigin="anonymous" 
  />
  
  <!-- Preload critical CSS -->
  <link 
    rel="preload" 
    href="/css/main.[contenthash].css" 
    as="style" 
  />
  
  <!-- Critical inline CSS for above-the-fold content -->
  <style>
    /* Critical CSS - Minified */
    :root{--color-primary:#2563eb;--font-family-primary:'Inter',sans-serif}
    *,*::before,*::after{box-sizing:border-box}
    body{margin:0;font-family:var(--font-family-primary);background-color:#fff;color:var(--color-text-primary)}
    .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
    #root{min-height:100vh;display:flex;flex-direction:column}
    
    /* Loading skeleton for verification form */
    .verification-skeleton{background:linear-gradient(90deg,#f0f0f0 25%,#e0e0e0 50%,#f0f0f0 75%);background-size:200% 100%;animation:skeleton-loading 1.5s infinite}
    @keyframes skeleton-loading{0%{background-position:200% 0}100%{background-position:-200% 0}}
    
    /* Initial visible elements */
    .initial-loader{display:flex;align-items:center;justify-content:center;min-height:100vh}
  </style>
  
  <!-- Main stylesheet (async) -->
  <link rel="stylesheet" href="/css/main.[contenthash].css" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="/css/main.[contenthash].css"></noscript>
</head>
<body>
  <noscript>You need to enable JavaScript to run FACTLY.</noscript>
  <div id="root">
    <!-- Server-side rendered initial state or loading state -->
    <div class="initial-loader" role="status" aria-label="Loading FACTLY">
      <div class="verification-skeleton" style="width:200px;height:200px;border-radius:50%"></div>
    </div>
  </div>
</body>
</html>
```

### 2.4 Layout System

#### 2.4.1 Main Layout Component

```jsx
// components/templates/MainLayout/MainLayout.jsx
import React, { Suspense, lazy } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../../organisms/Navbar';
import Footer from '../../organisms/Footer';
import LoadingSpinner from '../../atoms/LoadingSpinner';
import SkipLink from '../../atoms/SkipLink';
import ErrorBoundary from '../../molecules/ErrorBoundary';
import styles from './MainLayout.css';

const MainLayout = () => {
  return (
    <div className={styles.layout}>
      <SkipLink 
        href="#main-content" 
        text="Skip to main content" 
      />
      
      <Navbar />
      
      <ErrorBoundary 
        fallback={
          <div className={styles.errorContainer} role="alert">
            <h1>Something went wrong</h1>
            <p>We encountered an unexpected error. Please try again.</p>
            <button 
              onClick={() => window.location.reload()}
              className={styles.retryButton}
            >
              Refresh Page
            </button>
          </div>
        }
      >
        <Suspense 
          fallback={
            <div className={styles.loadingContainer} role="status" aria-live="polite">
              <LoadingSpinner 
                size="large" 
                label="Loading content..." 
              />
            </div>
          }
        >
          <main 
            id="main-content" 
            className={styles.main}
            tabIndex={-1}
          >
            <Outlet />
          </main>
        </Suspense>
      </ErrorBoundary>
      
      <Footer />
    </div>
  );
};

export default MainLayout;
```

#### 2.4.2 Layout CSS

```css
/* MainLayout.css */
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100%;
}

.loadingContainer {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: var(--spacing-xl);
}

.errorContainer {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: var(--spacing-xl);
  text-align: center;
}

.retryButton {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md) var(--spacing-xl);
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: background-color var(--transition-duration-base) ease;
}

.retryButton:hover {
  background-color: var(--color-primary-dark);
}

/* Responsive */
@media (max-width: 768px) {
  .loadingContainer,
  .errorContainer {
    padding: var(--spacing-lg);
    min-height: 300px;
  }
}
```

---

## 3. Accessibility Specification (WCAG 2.1 AA)

### 3.1 Skip Link Component

```jsx
// components/atoms/SkipLink/SkipLink.jsx
import React from 'react';
import styles from './SkipLink.css';

const SkipLink = ({ href, text }) => {
  const handleClick = (event) => {
    event.preventDefault();
    const targetElement = document.querySelector(href);
    if (targetElement) {
      targetElement.focus();
      targetElement.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
      });
    }
  };

  return (
    <a 
      href={href} 
      className={styles.skipLink}
      onClick={handleClick}
    >
      {text}
    </a>
  );
};

export default SkipLink;
```

```css
/* SkipLink.css */
.skipLink {
  position: absolute;
  top: -100%;
  left: 50%;
  transform: translateX(-50%);
  z-index: var(--z-tooltip);
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  text-decoration: none;
  font-weight: var(--font-weight-semibold);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  box-shadow: var(--shadow-lg);
  transition: top var(--transition-duration-fast) ease;
}

.skipLink:focus {
  top: 0;
  outline: 3px solid var(--color-warning);
  outline-offset: 2px;
}
```

### 3.2 Form Accessibility

```jsx
// components/molecules/FormField/FormField.jsx
import React, { forwardRef } from 'react';
import Label from '../../atoms/Label';
import Input from '../../atoms/Input';
import styles from './FormField.css';

const FormField = forwardRef(({
  id,
  label,
  type = 'text',
  value,
  onChange,
  onBlur,
  placeholder,
  required = false,
  disabled = false,
  error,
  hint,
  autoComplete,
  maxLength,
  ariaDescribedBy,
}, ref) => {
  const describedByIds = [];
  if (error) describedByIds.push(`${id}-error`);
  if (hint) describedByIds.push(`${id}-hint`);
  
  return (
    <div className={`${styles.field} ${error ? styles.fieldError : ''}`}>
      {label && (
        <Label 
          htmlFor={id} 
          required={required}
        >
          {label}
        </Label>
      )}
      
      <Input
        ref={ref}
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        autoComplete={autoComplete}
        maxLength={maxLength}
        aria-invalid={!!error}
        aria-describedby={describedByIds.length > 0 ? describedByIds.join(' ') : undefined}
        aria-required={required}
      />
      
      {hint && !error && (
        <p id={`${id}-hint`} className={styles.hint}>
          {hint}
        </p>
      )}
      
      {error && (
        <p id={`${id}-error`} className={styles.error} role="alert">
          <span aria-hidden="true">⚠</span> {error}
        </p>
      )}
    </div>
  );
});

FormField.displayName = 'FormField';

export default FormField;
```

### 3.3 Keyboard Navigation

```jsx
// components/molecules/InteractiveGrid/InteractiveGrid.jsx
import React, { useMemo } from 'react';
import styles from './InteractiveGrid.css';

const InteractiveGrid = ({ items, renderItem, onItemSelect }) => {
  const handleKeyDown = (event, item, index) => {
    const gridLength = items.length;
    let newIndex = index;
    
    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        event.preventDefault();
        newIndex = (index + 1) % gridLength;
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        event.preventDefault();
        newIndex = (index - 1 + gridLength) % gridLength;
        break;
      case 'Home':
        event.preventDefault();
        newIndex = 0;
        break;
      case 'End':
        event.preventDefault();
        newIndex = gridLength - 1;
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (onItemSelect) {
          onItemSelect(item);
        }
        break;
      default:
        return;
    }
    
    const newElement = document.querySelector(`[data-grid-index="${newIndex}"]`);
    if (newElement) {
      newElement.focus();
    }
  };

  return (
    <div 
      className={styles.grid}
      role="grid"
      aria-label="Interactive items grid"
    >
      {items.map((item, index) => (
        <div
          key={index}
          data-grid-index={index}
          role="gridcell"
          tabIndex={0}
          onKeyDown={(e) => handleKeyDown(e, item, index)}
          onClick={() => onItemSelect && onItemSelect(item)}
          className={styles.gridItem}
        >
          {renderItem(item)}
        </div>
      ))}
    </div>
  );
};

export default InteractiveGrid;
```

### 3.4 Live Regions

```jsx
// components/molecules/StatusMessage/StatusMessage.jsx
import React, { useEffect, useState } from 'react';
import styles from './StatusMessage.css';

const StatusMessage = ({ type = 'status', children, timeout = 5000 }) => {
  const [visible, setVisible] = useState(true);
  const [exited, setExited] = useState(false);

  useEffect(() => {
    if (timeout > 0) {
      const timer = setTimeout(() => {
        setVisible(false);
        setTimeout(() => setExited(true), 300);
      }, timeout);
      
      return () => clearTimeout(timer);
    }
  }, [timeout]);

  if (exited) return null;

  const roleMap = {
    status: 'status',
    alert: 'alert',
    progressbar: 'status',
  };

  return (
    <div
      role={roleMap[type]}
      aria-live={type === 'alert' ? 'assertive' : 'polite'}
      aria-atomic="true"
      className={`${styles.message} ${styles[type]} ${visible ? styles.visible : styles.exiting}`}
    >
      {children}
    </div>
  );
};

export default StatusMessage;
```

---

## 4. Responsive Design Specification

### 4.1 Breakpoint System

```css
/* breakpoints.css */
:root {
  /* Breakpoints */
  --breakpoint-xs: 0px;
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
  
  /* Container widths */
  --container-xs: 480px;
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
}

/* Mobile-first media queries */
@media (min-width: 640px) {
  /* sm breakpoint */
}

@media (min-width: 768px) {
  /* md breakpoint */
}

@media (min-width: 1024px) {
  /* lg breakpoint */
}

@media (min-width: 1280px) {
  /* xl breakpoint */
}

/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }
}
```

### 4.2 Responsive Verification Form

```jsx
// components/organisms/VerificationForm/VerificationForm.jsx
import React, { useState, useCallback, useRef, useEffect } from 'react';
import FormField from '../../molecules/FormField';
import Button from '../../atoms/Button';
import LoadingSpinner from '../../atoms/LoadingSpinner';
import StatusMessage from '../../molecules/StatusMessage';
import useMediaQuery from '../../../hooks/useMediaQuery';
import styles from './VerificationForm.css';

const VerificationForm = ({ onSubmit, isLoading, error }) => {
  const [text, setText] = useState('');
  const [touched, setTouched] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const formRef = useRef(null);
  
  const isMobile = useMediaQuery('(max-width: 640px)');
  const isTablet = useMediaQuery('(min-width: 641px) and (max-width: 1024px)');

  const validate = useCallback((value) => {
    if (!value.trim()) {
      return 'Please enter text to verify';
    }
    if (value.trim().length < 10) {
      return 'Please enter at least 10 characters';
    }
    if (value.length > 5000) {
      return `Text exceeds maximum length of 5000 characters (current: ${value.length})`;
    }
    return null;
  }, []);

  const handleChange = useCallback((e) => {
    const value = e.target.value;
    setText(value);
    setTouched(true);
    if (validationError) {
      setValidationError(null);
    }
  }, [validationError]);

  const handleBlur = useCallback(() => {
    setTouched(true);
    const error = validate(text);
    setValidationError(error);
  }, [text, validate]);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    const error = validate(text);
    if (error) {
      setValidationError(error);
      setTouched(true);
      return;
    }
    await onSubmit(text.trim());
  }, [text, validate, onSubmit]);

  const characterCount = text.length;
  const characterPercentage = (characterCount / 5000) * 100;
  const isNearLimit = characterPercentage > 90;

  return (
    <form 
      ref={formRef}
      className={styles.form}
      onSubmit={handleSubmit}
      noValidate
      aria-label="News credibility verification form"
    >
      <div className={styles.header}>
        <h2 className={styles.title}>Verify News Credibility</h2>
        <p className={styles.subtitle}>
          Enter a headline, article URL, or paste text to check its credibility
        </p>
      </div>

      <div className={styles.content}>
        <FormField
          id="verification-text"
          type="textarea"
          label="Content to verify"
          value={text}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder={isMobile 
            ? "Paste headline or text here..." 
            : "Paste a news headline, article URL, or article text here..."
          }
          required
          disabled={isLoading}
          error={touched ? validationError : null}
          hint={`${characterCount.toLocaleString()} / 5,000 characters`}
          autoComplete="off"
          maxLength={5000}
        />

        {isNearLimit && (
          <StatusMessage type="warning" timeout={null}>
            You're approaching the character limit
          </StatusMessage>
        )}

        {error && (
          <StatusMessage type="error" timeout={10000}>
            {error}
          </StatusMessage>
        )}

        <div className={styles.actions}>
          <Button
            type="submit"
            variant="primary"
            size={isMobile ? 'medium' : 'large'}
            fullWidth={isMobile}
            disabled={isLoading || !text.trim()}
            loading={isLoading}
            ariaLabel={isLoading ? "Verifying content..." : "Verify content credibility"}
          >
            {isLoading ? (
              <>
                <LoadingSpinner size="small" />
                <span>Verifying...</span>
              </>
            ) : (
              <>
                <span aria-hidden="true">🔍</span>
                <span>Verify Now</span>
              </>
            )}
          </Button>
        </div>

        <div className={styles.features} role="list" aria-label="Platform features">
          <div className={styles.feature} role="listitem">
            <span aria-hidden="true">🔍</span>
            <span>Multi-source fact-checking</span>
          </div>
          <div className={styles.feature} role="listitem">
            <span aria-hidden="true">📊</span>
            <span>Credibility scoring</span>
          </div>
          <div className={styles.feature} role="listitem">
            <span aria-hidden="true">📚</span>
            <span>Evidence analysis</span>
          </div>
        </div>
      </div>
    </form>
  );
};

export default VerificationForm;
```

```css
/* VerificationForm.css */
.form {
  width: 100%;
  max-width: var(--container-md);
  margin: 0 auto;
  padding: var(--spacing-lg);
}

.header {
  margin-bottom: var(--spacing-xl);
  text-align: center;
}

.title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm);
}

.subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  margin: 0;
}

.content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.actions {
  display: flex;
  justify-content: center;
}

.features {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.feature {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Responsive */
@media (max-width: 640px) {
  .form {
    padding: var(--spacing-md);
  }

  .title {
    font-size: var(--font-size-2xl);
  }

  .subtitle {
    font-size: var(--font-size-base);
  }

  .features {
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
  }
}

@media (min-width: 641px) {
  .actions {
    justify-content: flex-start;
  }
}
```

---

## 5. Loading States & Transitions

### 5.1 Skeleton Loading Components

```jsx
// components/atoms/Skeleton/Skeleton.jsx
import React from 'react';
import styles from './Skeleton.css';

const Skeleton = ({ 
  variant = 'text', 
  width, 
  height, 
  borderRadius,
  className = '' 
}) => {
  const style = {
    width: width || (variant === 'text' ? '100%' : undefined),
    height: height || (variant === 'text' ? '1em' : undefined),
    borderRadius: borderRadius || (variant === 'circle' ? '50%' : undefined),
  };

  return (
    <div 
      className={`${styles.skeleton} ${styles[variant]} ${className}`}
      style={style}
      aria-hidden="true"
    />
  );
};

export default Skeleton;
```

```css
/* Skeleton.css */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-background-tertiary) 25%,
    var(--color-border-light) 50%,
    var(--color-background-tertiary) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

.skeleton--text {
  height: 1em;
  border-radius: var(--radius-sm);
}

.skeleton--circle {
  border-radius: 50%;
}

.skeleton--rect {
  border-radius: var(--radius-md);
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  .skeleton {
    animation: none;
    background: var(--color-background-tertiary);
  }
}
```

### 5.2 Score Display with Animation

```jsx
// components/organisms/ScoreDisplay/ScoreDisplay.jsx
import React, { useEffect, useState, useRef, useMemo } from 'react';
import Skeleton from '../../atoms/Skeleton';
import styles from './ScoreDisplay.css';

const ScoreDisplay = ({ score, confidence, breakdown, isLoading }) => {
  const [animatedScore, setAnimatedScore] = useState(0);
  const [animatedConfidence, setAnimatedConfidence] = useState(0);
  const circleRef = useRef(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    if (isLoading || score === undefined || hasAnimated.current) return;
    
    hasAnimated.current = true;
    const duration = 1500;
    const steps = 60;
    const scoreIncrement = score / steps;
    const confidenceIncrement = confidence / steps;
    
    let currentStep = 0;
    const timer = setInterval(() => {
      currentStep++;
      setAnimatedScore(Math.min(currentStep * scoreIncrement, score));
      setAnimatedConfidence(Math.min(currentStep * confidenceIncrement, confidence));
      
      if (currentStep >= steps) {
        clearInterval(timer);
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [isLoading, score, confidence]);

  const scoreColor = useMemo(() => {
    if (animatedScore >= 80) return styles.colorHigh;
    if (animatedScore >= 60) return styles.colorMedium;
    return styles.colorLow;
  }, [animatedScore]);

  const scoreLabel = useMemo(() => {
    if (animatedScore >= 80) return 'Highly Credible';
    if (animatedScore >= 60) return 'Moderately Credible';
    if (animatedScore >= 40) return 'Low Credibility';
    return 'Not Credible';
  }, [animatedScore]);

  const scoreCircleStyle = useMemo(() => {
    const circumference = 2 * Math.PI * 45;
    const progress = animatedScore / 100;
    const offset = circumference * (1 - progress);
    return {
      strokeDasharray: circumference,
      strokeDashoffset: offset,
    };
  }, [animatedScore]);

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>
          <Skeleton variant="circle" width="160px" height="160px" />
          <div style={{ marginTop: '1rem' }}>
            <Skeleton width="120px" height="2rem" />
          </div>
        </div>
        <div className={styles.loadingBreakdown}>
          {[1, 2, 3, 4].map(i => (
            <Skeleton key={i} height="60px" borderRadius="8px" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container} role="region" aria-label="Credibility Score">
      <h2 className={styles.title}>FACTLY Score™</h2>
      
      <div className={styles.circleContainer}>
        <svg 
          className={styles.scoreCircle} 
          viewBox="0 0 100 100"
          role="img"
          aria-label={`Credibility score: ${Math.round(animatedScore)}%, ${scoreLabel}`}
        >
          <circle 
            className={styles.circleBackground}
            cx="50" 
            cy="50" 
            r="45" 
          />
          <circle 
            ref={circleRef}
            className={`${styles.circleProgress} ${scoreColor}`}
            cx="50" 
            cy="50" 
            r="45"
            style={scoreCircleStyle}
          />
        </svg>
        
        <div className={styles.scoreContent}>
          <span className={styles.scoreValue}>{Math.round(animatedScore)}</span>
          <span className={styles.scoreSymbol}>%</span>
        </div>
      </div>

      <p className={`${styles.scoreLabel} ${scoreColor}`}>
        {scoreLabel}
      </p>

      <div className={styles.confidenceSection}>
        <div className={styles.confidenceHeader}>
          <span>Confidence Level</span>
          <span className={styles.confidenceValue}>
            {Math.round(animatedConfidence)}%
          </span>
        </div>
        <div 
          className={styles.confidenceBar}
          role="progressbar"
          aria-valuenow={Math.round(animatedConfidence)}
          aria-valuemin="0"
          aria-valuemax="100"
          aria-label="Verification confidence level"
        >
          <div 
            className={styles.confidenceFill}
            style={{ width: `${animatedConfidence}%` }}
          />
        </div>
      </div>

      {breakdown && Object.keys(breakdown).length > 0 && (
        <div className={styles.breakdown}>
          <h3 className={styles.breakdownTitle}>Score Breakdown</h3>
          {Object.entries(breakdown).map(([key, value]) => (
            <div key={key} className={styles.breakdownItem}>
              <span className={styles.breakdownLabel}>
                {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
              </span>
              <div className={styles.breakdownBar}>
                <div 
                  className={`${styles.breakdownFill} ${value >= 0.8 ? styles.fillHigh : value >= 0.6 ? styles.fillMedium : styles.fillLow}`}
                  style={{ width: `${value * 100}%` }}
                />
                <span className={styles.breakdownValue}>
                  {Math.round(value * 100)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ScoreDisplay;
```

```css
/* ScoreDisplay.css */
.container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: var(--spacing-xl);
  background-color: var(--color-background-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  text-align: center;
  margin: 0 0 var(--spacing-lg);
}

.circleContainer {
  position: relative;
  width: 160px;
  height: 160px;
  margin: 0 auto var(--spacing-lg);
}

.scoreCircle {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.circleBackground {
  fill: none;
  stroke: var(--color-border-light);
  stroke-width: 8;
}

.circleProgress {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 1.5s ease-out;
}

.colorHigh {
  stroke: var(--score-high);
}

.colorMedium {
  stroke: var(--score-medium);
}

.colorLow {
  stroke: var(--score-low);
}

.scoreContent {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.scoreValue {
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.scoreSymbol {
  font-size: var(--font-size-xl);
  color: var(--color-text-secondary);
}

.scoreLabel {
  text-align: center;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-lg);
}

.scoreLabel.colorHigh { color: var(--score-high); }
.scoreLabel.colorMedium { color: var(--score-medium); }
.scoreLabel.colorLow { color: var(--score-low); }

.confidenceSection {
  margin-bottom: var(--spacing-lg);
}

.confidenceHeader {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.confidenceValue {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.confidenceBar {
  height: 8px;
  background-color: var(--color-background-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.confidenceFill {
  height: 100%;
  background-color: var(--color-primary);
  border-radius: var(--radius-full);
  transition: width 1.5s ease-out;
}

.breakdown {
  border-top: 1px solid var(--color-border-light);
  padding-top: var(--spacing-lg);
}

.breakdownTitle {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md);
}

.breakdownItem {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.breakdownLabel {
  flex: 0 0 120px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.breakdownBar {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  height: 20px;
  background-color: var(--color-background-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.breakdownFill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 1s ease-out;
}

.fillHigh { background-color: var(--score-high); }
.fillMedium { background-color: var(--score-medium); }
.fillLow { background-color: var(--score-low); }

.breakdownValue {
  flex: 0 0 40px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  text-align: right;
}

/* Loading state */
.loadingContainer {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-xl);
}

.loadingBreakdown {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

/* Responsive */
@media (max-width: 640px) {
  .container {
    padding: var(--spacing-lg);
  }

  .circleContainer {
    width: 140px;
    height: 140px;
  }

  .scoreValue {
    font-size: var(--font-size-3xl);
  }
}
```

---

## 6. Error Handling & Recovery

### 6.1 Global Error Boundary

```jsx
// components/molecules/ErrorBoundary/ErrorBoundary.jsx
import React, { Component, Fragment } from 'react';
import Button from '../../atoms/Button';
import styles from './ErrorBoundary.css';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    // Log to error tracking service (Sentry, etc.)
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  handleRefresh = () => {
    window.location.reload();
  };

  render() {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      if (fallback) {
        return typeof fallback === 'function' 
          ? fallback({ error, resetErrorBoundary: this.handleRetry })
          : fallback;
      }

      return (
        <div className={styles.container} role="alert">
          <div className={styles.icon} aria-hidden="true">⚠️</div>
          <h1 className={styles.title}>Something went wrong</h1>
          <p className={styles.message}>
            We encountered an unexpected error while processing your request.
          </p>
          {process.env.NODE_ENV === 'development' && (
            <details className={styles.details}>
              <summary>Error details</summary>
              <pre className={styles.stackTrace}>
                {error?.toString()}
                {errorInfo?.componentStack}
              </pre>
            </details>
          )}
          <div className={styles.actions}>
            <Button 
              variant="primary" 
              onClick={this.handleRetry}
            >
              Try Again
            </Button>
            <Button 
              variant="secondary" 
              onClick={this.handleRefresh}
            >
              Refresh Page
            </Button>
          </div>
        </div>
      );
    }

    return children;
  }
}

export default ErrorBoundary;
```

### 6.2 API Error Handling

```jsx
// hooks/useVerification/useVerification.js
import { useState, useCallback, useEffect } from 'react';

const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Unable to connect to the verification service. Please check your internet connection.',
  TIMEOUT_ERROR: 'The verification request timed out. Please try again.',
  SERVER_ERROR: 'The verification service encountered an error. Please try again later.',
  RATE_LIMIT: 'You have exceeded the maximum number of verification requests. Please wait before trying again.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
};

const useVerification = () => {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const getErrorMessage = (error) => {
    if (!error) return ERROR_MESSAGES.UNKNOWN_ERROR;
    
    if (error.name === 'AbortError') {
      return ERROR_MESSAGES.TIMEOUT_ERROR;
    }
    
    if (error.message?.includes('Failed to fetch')) {
      return ERROR_MESSAGES.NETWORK_ERROR;
    }
    
    if (error.status === 429) {
      return ERROR_MESSAGES.RATE_LIMIT;
    }
    
    if (error.status >= 500) {
      return ERROR_MESSAGES.SERVER_ERROR;
    }
    
    if (error.status === 400) {
      return ERROR_MESSAGES.VALIDATION_ERROR;
    }
    
    return error.message || ERROR_MESSAGES.UNKNOWN_ERROR;
  };

  const verify = useCallback(async (text) => {
    setIsLoading(true);
    setError(null);
    setRetryCount(prev => prev + 1);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    try {
      const response = await fetch('http://localhost:8000/api/verify/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text.trim() }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw {
          status: response.status,
          message: errorData.message || `Server error: ${response.status}`,
        };
      }

      const data = await response.json();
      setResult(data);
      return data;
    } catch (err) {
      clearTimeout(timeoutId);
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);
      throw { message: errorMessage, originalError: err };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearResult = useCallback(() => {
    setResult(null);
  }, []);

  return {
    result,
    isLoading,
    error,
    retryCount,
    verify,
    clearError,
    clearResult,
  };
};

export default useVerification;
```

---

## 7. Testing Strategy

### 7.1 Test File Structure

```
frontend/
├── src/
│   ├── __tests__/
│   │   ├── unit/
│   │   │   ├── components/
│   │   │   │   ├── Button.test.jsx
│   │   │   │   ├── Input.test.jsx
│   │   │   │   └── Skeleton.test.jsx
│   │   │   ├── hooks/
│   │   │   │   ├── useVerification.test.js
│   │   │   │   └── useMediaQuery.test.js
│   │   │   └── utils/
│   │   │       ├── formatters.test.js
│   │   │       └── validators.test.js
│   │   ├── integration/
│   │   │   ├── VerificationForm.integration.test.jsx
│   │   │   └── ScoreDisplay.integration.test.jsx
│   │   └── e2e/
│   │       ├── home.page.test.js
│   │       ├── verification.page.test.js
│   │       └── results.page.test.js
│   ├── components/
│   │   └── ...
│   └── setupTests.js
├── jest.config.js
└── playwright.config.js
```

### 7.2 Unit Test Example

```jsx
// __tests__/unit/components/Button.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Button from '../../../components/atoms/Button';

describe('Button Component', () => {
  describe('Rendering', () => {
    it('renders button with correct text', () => {
      render(<Button>Click Me</Button>);
      expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
    });

    it('renders button with icon', () => {
      render(
        <Button icon={<span aria-hidden="true">✓</span>}>
          Submit
        </Button>
      );
      expect(screen.getByRole('button')).toContainHTML('<span aria-hidden="true">✓</span>');
    });

    it('renders loading state', () => {
      render(<Button loading>Loading</Button>);
      expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
      expect(screen.getByLabelText(/loading/i)).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('calls onClick when clicked', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();
      
      render(<Button onClick={handleClick}>Click Me</Button>);
      await user.click(screen.getByRole('button'));
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when disabled', async () => {
      const handleClick = jest.fn();
      const user = userEvent.setup();
      
      render(<Button disabled onClick={handleClick}>Click Me</Button>);
      await user.click(screen.getByRole('button'));
      
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('has correct aria-label when provided', () => {
      render(<Button ariaLabel="Custom label">Button</Button>);
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Custom label');
    });

    it('focuses with keyboard navigation', () => {
      render(<Button>Test Button</Button>);
      expect(document.body).toHaveFocus();
      fireEvent.keyDown(document.body, { key: 'Tab', code: 'Tab' });
      expect(screen.getByRole('button')).toHaveFocus();
    });
  });

  describe('Variants', () => {
    it('applies primary variant styles', () => {
      render(<Button variant="primary">Primary</Button>);
      expect(screen.getByRole('button')).toHaveClass('button--primary');
    });

    it('applies danger variant styles', () => {
      render(<Button variant="danger">Delete</Button>);
      expect(screen.getByRole('button')).toHaveClass('button--danger');
    });
  });
});
```

---

## 8. Performance Optimization

### 8.1 Code Splitting Strategy

```jsx
// App.jsx - Route-based code splitting
import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './components/templates/MainLayout';
import LoadingSpinner from './components/atoms/LoadingSpinner';
import ErrorBoundary from './components/molecules/ErrorBoundary';

// Lazy load pages
const HomePage = lazy(() => import('./pages/HomePage'));
const VerificationPage = lazy(() => import('./pages/VerificationPage'));
const ResultsPage = lazy(() => import('./pages/ResultsPage'));
const AuthPage = lazy(() => import('./pages/AuthPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

const LoadingFallback = () => (
  <div className="loading-fallback" role="status" aria-live="polite">
    <LoadingSpinner size="large" label="Loading page..." />
  </div>
);

const App = () => {
  return (
    <ErrorBoundary
      fallback={({ error, resetErrorBoundary }) => (
        <div className="error-page" role="alert">
          <h1>Application Error</h1>
          <p>Failed to load application. Please refresh.</p>
          <button onClick={resetErrorBoundary}>Try Again</button>
        </div>
      )}
    >
      <BrowserRouter>
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<HomePage />} />
              <Route path="verify" element={<VerificationPage />} />
              <Route path="results" element={<ResultsPage />} />
              <Route path="auth/*" element={<AuthPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  );
};

export default App;
```

### 8.2 Image Optimization

```jsx
// components/atoms/Avatar/Avatar.jsx
import React, { useState } from 'react';
import styles from './Avatar.css';

const Avatar = ({ 
  src, 
  alt, 
  size = 'medium', 
  fallback = null,
  loading = 'lazy' 
}) => {
  const [hasError, setHasError] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  const handleError = () => {
    setHasError(true);
  };

  const handleLoad = () => {
    setIsLoaded(true);
  };

  const sizeMap = {
    small: 32,
    medium: 48,
    large: 64,
    xlarge: 96,
  };

  const dimension = sizeMap[size] || 48;

  if (hasError || !src) {
    return (
      <div 
        className={`${styles.avatar} ${styles[size]} ${styles.fallback}`}
        style={{ width: dimension, height: dimension }}
        role="img"
        aria-label={alt || 'Avatar'}
      >
        {fallback || <span aria-hidden="true">👤</span>}
      </div>
    );
  }

  return (
    <div 
      className={`${styles.avatar} ${styles[size]} ${isLoaded ? styles.loaded : ''}`}
      style={{ width: dimension, height: dimension }}
    >
      <img
        src={src}
        alt={alt || ''}
        width={dimension}
        height={dimension}
        loading={loading}
        onError={handleError}
        onLoad={handleLoad}
        className={styles.image}
      />
    </div>
  );
};

export default Avatar;
```

---

## 9. Browser Support

### 9.1 Browser Compatibility Matrix

| Browser | Minimum Version | Status |
|---------|----------------|--------|
| Chrome | 90+ | ✅ Full Support |
| Firefox | 88+ | ✅ Full Support |
| Safari | 14+ | ✅ Full Support |
| Edge | 90+ | ✅ Full Support |
| Chrome (Android) | 90+ | ✅ Full Support |
| Safari (iOS) | 14+ | ✅ Full Support |
| IE 11 | N/A | ❌ Not Supported |

### 9.2 Polyfills Strategy

```javascript
// src/polyfills.js
// Core JS polyfills for older browsers
import 'core-js/stable';

// Async/await support
import 'regenerator-runtime/runtime';

// Fetch API polyfill (if needed)
import 'whatwg-fetch';

// ResizeObserver polyfill
import 'resize-observer-polyfill';

// MatchMedia polyfill
import 'matchmedia-polyfill';
```

---

## 10. Security Considerations

### 10.1 Content Security Policy

```html
<!-- public/index.html - CSP Header (via meta tag or server config) -->
<meta 
  http-equiv="Content-Security-Policy" 
  content="
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com;
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    font-src 'self' https://fonts.gstatic.com;
    img-src 'self' data: https:;
    connect-src 'self' http://localhost:8000 https://api.factly.app;
    frame-src 'self';
    base-uri 'self';
    form-action 'self';
    upgrade-insecure-requests;
  "
/>
```

### 10.2 XSS Prevention

```jsx
// utils/sanitization.js
import DOMPurify from 'dompurify';

export const sanitizeHTML = (html) => {
  if (!html) return '';
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
    ALLOW_DATA_ATTR: false,
  });
};

export const sanitizeUrl = (url) => {
  if (!url) return null;
  
  const allowedProtocols = ['http:', 'https:'];
  try {
    const parsed = new URL(url, window.location.href);
    if (!allowedProtocols.includes(parsed.protocol)) {
      return null;
    }
    return parsed.href;
  } catch {
    return null;
  }
};
```

---

## 11. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up project structure with Create React App or Vite
- [ ] Configure TypeScript and ESLint
- [ ] Implement design tokens and CSS architecture
- [ ] Build atomic components (atoms)
- [ ] Set up testing environment (Jest + React Testing Library)

### Phase 2: Core Features (Week 3-4)
- [ ] Build molecule components
- [ ] Implement verification form with accessibility
- [ ] Create score display with animations
- [ ] Build evidence panel with metadata
- [ ] Implement main layout and routing

### Phase 3: Integration (Week 5-6)
- [ ] Connect to backend API
- [ ] Implement error handling and loading states
- [ ] Add skeleton loading components
- [ ] Optimize critical rendering path
- [ ] Performance testing and optimization

### Phase 4: Polish (Week 7-8)
- [ ] Cross-browser testing
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Responsive design testing
- [ ] Security review
- [ ] Documentation

---

## 12. Quality Metrics

### 12.1 Performance Targets
| Metric | Target | Measurement |
|--------|--------|------------|
| First Contentful Paint (FCP) | < 1.0s | Lighthouse |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| First Input Delay (FID) | < 100ms | Lighthouse |
| Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse |
| Time to Interactive (TTI) | < 3.5s | Lighthouse |

### 12.2 Accessibility Targets
- [ ] 100% WCAG 2.1 AA compliance
- [ ] All interactive elements keyboard accessible
- [ ] Proper ARIA labels on all components
- [ ] Screen reader compatibility
- [ ] Color contrast ratio 4.5:1 minimum

### 12.3 Test Coverage Targets
- [ ] Unit tests: 80% coverage minimum
- [ ] Integration tests: All critical paths
- [ ] E2E tests: Core user journeys
- [ ] Visual regression testing

---

*Document Version: 1.0*  
*Last Updated: February 2026*  
*Status: Technical Specification*

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';

const ThemeContext = createContext();

const STORAGE_KEY = 'factly-theme';

function getInitialTheme() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === 'dark' || stored === 'light') return stored;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(getInitialTheme);
  const [ready, setReady] = useState(false);
  const mqRef = useRef(null);

  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    mqRef.current = mq;

    const handler = (e) => {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) {
        setTheme(e.matches ? 'dark' : 'light');
      }
    };

    mq.addEventListener('change', handler);
    const timer = setTimeout(() => setReady(true), 80);

    return () => {
      mq.removeEventListener('change', handler);
      clearTimeout(timer);
    };
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  useEffect(() => {
    if (ready) {
      document.documentElement.classList.add('theme-transition');
    } else {
      document.documentElement.classList.remove('theme-transition');
    }
  }, [ready]);

  const toggleTheme = useCallback(() => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  const value = {
    theme,
    darkMode: theme === 'dark',
    toggleTheme,
    ready,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}

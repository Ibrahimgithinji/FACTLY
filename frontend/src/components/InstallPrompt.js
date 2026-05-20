import { useState, useEffect } from 'react';

export default function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [show, setShow] = useState(false);

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShow(true);
    };
    window.addEventListener('beforeinstallprompt', handler);

    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setShow(false);
    }

    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const result = await deferredPrompt.userChoice;
    if (result.outcome === 'accepted') {
      setShow(false);
    }
    setDeferredPrompt(null);
  };

  if (!show) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: 20,
      left: 20,
      right: 20,
      maxWidth: 400,
      margin: '0 auto',
      background: 'var(--card-bg)',
      border: '1px solid var(--border)',
      borderRadius: 12,
      padding: 16,
      boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      gap: 12,
    }}>
      <div style={{ flex: 1 }}>
        <p style={{ margin: 0, fontWeight: 600, fontSize: 14, color: 'var(--text)' }}>
          Install Factly
        </p>
        <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--text-secondary)' }}>
          Get the app for a better experience
        </p>
      </div>
      <button
        onClick={handleInstall}
        style={{
          padding: '8px 16px',
          background: 'var(--accent)',
          color: '#fff',
          border: 'none',
          borderRadius: 8,
          fontWeight: 600,
          cursor: 'pointer',
          fontSize: 13,
        }}
      >
        Install
      </button>
      <button
        onClick={() => setShow(false)}
        style={{
          padding: 8,
          background: 'none',
          border: 'none',
          color: 'var(--text-secondary)',
          cursor: 'pointer',
          fontSize: 16,
        }}
      >
        ✕
      </button>
    </div>
  );
}

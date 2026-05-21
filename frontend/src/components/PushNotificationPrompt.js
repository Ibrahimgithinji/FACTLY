import { useState, useEffect } from 'react';

const PUBLIC_VAPID_KEY = 'BGb5sRFzl-JOMxXNG3t0xMJi0s5LiioU7lfSWBW5fkwFr_wYAe0d2GlXdAHBeJERGCQsl5rDjZm1BXXDEXk7KRI';

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  return new Uint8Array([...rawData].map((c) => c.charCodeAt(0)));
}

export default function PushNotificationPrompt() {
  const [, setStatus] = useState('idle'); // idle | denied | subscribed | unsupported
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (!('Notification' in window) || !('serviceWorker' in navigator)) {
      setStatus('unsupported');
      return;
    }
    if (Notification.permission === 'granted') {
      setStatus('subscribed');
      return;
    }
    if (Notification.permission === 'denied') {
      setStatus('denied');
      return;
    }
    // Show prompt after 5 seconds
    const timer = setTimeout(() => setShow(true), 5000);
    return () => clearTimeout(timer);
  }, []);

  const handleSubscribe = async () => {
    try {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        setStatus('denied');
        setShow(false);
        return;
      }

      const reg = await navigator.serviceWorker.ready;
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(PUBLIC_VAPID_KEY),
      });

      await fetch('/api/content/push/subscribe/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sub),
      });

      setStatus('subscribed');
      setShow(false);
    } catch (err) {
      console.error('Push subscription failed:', err);
    }
  };

  const handleDismiss = () => setShow(false);

  if (!show) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: 80,
      left: 20,
      right: 20,
      maxWidth: 400,
      margin: '0 auto',
      background: 'var(--card-bg)',
      border: '1px solid var(--border)',
      borderRadius: 12,
      padding: 16,
      boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
      zIndex: 999,
    }}>
      <p style={{ margin: '0 0 8px', fontWeight: 600, fontSize: 14, color: 'var(--text)' }}>
        Get notified about new articles
      </p>
      <p style={{ margin: '0 0 12px', fontSize: 12, color: 'var(--text-secondary)' }}>
        Enable push notifications to stay updated with the latest news.
      </p>
      <div style={{ display: 'flex', gap: 8 }}>
        <button
          onClick={handleSubscribe}
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
          Enable
        </button>
        <button
          onClick={handleDismiss}
          style={{
            padding: '8px 16px',
            background: 'none',
            border: '1px solid var(--border)',
            borderRadius: 8,
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            fontSize: 13,
          }}
        >
          Not now
        </button>
      </div>
    </div>
  );
}

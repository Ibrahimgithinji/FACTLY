export function registerSW() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => {
          console.log('SW registered:', reg.scope);
        })
        .catch((err) => {
          console.log('SW registration failed:', err);
        });
    });
  }
}

export function unregisterSW() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((reg) => {
      reg.unregister();
    });
  }
}

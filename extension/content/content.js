let factlyBadge = null;
let factlyHighlights = [];

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'FACTLY_AUTO_RESULT') {
    showInlineBadge(message.data);
    highlightClaims(message.data);
  }
  if (message.type === 'FACTLY_CLEAR') {
    clearHighlights();
  }
});

function showInlineBadge(data) {
  removeExistingBadge();

  const badge = document.createElement('div');
  badge.id = 'factly-inline-badge';
  badge.style.cssText = `
    position: fixed; bottom: 20px; right: 20px; z-index: 2147483647;
    background: white; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.15);
    padding: 16px; max-width: 320px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    cursor: pointer; transition: transform 0.2s; border: 1px solid #e5e7eb;
  `;

  const score = data.factly_score;
  let color, label;
  if (score >= 66) { color = '#22c55e'; label = 'Likely Authentic'; }
  else if (score >= 36) { color = '#eab308'; label = 'Uncertain'; }
  else { color = '#ef4444'; label = 'Likely Fake'; }

  badge.innerHTML = `
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
      <div style="width:48px;height:48px;border-radius:50%;background:conic-gradient(${color} ${score}%, #e5e7eb ${score}%);display:flex;align-items:center;justify-content:center">
        <div style="width:40px;height:40px;border-radius:50%;background:white;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;color:#1f2937">${score}</div>
      </div>
      <div>
        <div style="font-weight:600;font-size:14px;color:#1f2937">Factly Score</div>
        <div style="font-size:12px;color:${color};font-weight:500">${label}</div>
      </div>
    </div>
    <div style="font-size:11px;color:#6b7280;border-top:1px solid #f3f4f6;padding-top:8px">
      Confidence: ${data.confidence_level} &middot; ${data.sources_consulted || 0} sources
    </div>
    <div style="display:flex;gap:8px;margin-top:8px">
      <button id="factly-badge-open" style="flex:1;padding:6px 12px;font-size:12px;border:none;border-radius:6px;background:#1f2937;color:white;cursor:pointer;font-weight:500">View Details</button>
      <button id="factly-badge-close" style="padding:6px 10px;font-size:12px;border:1px solid #e5e7eb;border-radius:6px;background:white;color:#6b7280;cursor:pointer">X</button>
    </div>
  `;

  document.body.appendChild(badge);
  factlyBadge = badge;

  document.getElementById('factly-badge-open').addEventListener('click', () => {
    chrome.runtime.sendMessage({
      type: 'QUICK_CHECK',
      text: document.title + ' ' + (document.querySelector('meta[name="description"]')?.content || '')
    });
    chrome.action.openPopup();
  });

  document.getElementById('factly-badge-close').addEventListener('click', () => {
    removeExistingBadge();
  });

  setTimeout(() => {
    badge.style.transform = 'translateY(0)';
    badge.style.opacity = '1';
  }, 100);
}

function removeExistingBadge() {
  if (factlyBadge) {
    factlyBadge.remove();
    factlyBadge = null;
  }
}

function highlightClaims(data) {
  clearHighlights();

  const suspectScore = data.factly_score < 50;
  if (!suspectScore) return;

  const textNodes = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (node.parentElement?.closest('script, style, noscript, #factly-inline-badge')) continue;
    textNodes.push(node);
  }

  const sensitivityThreshold = data.factly_score < 30 ? 0.1 : 0.15;
  textNodes.forEach(node => {
    const text = node.textContent.trim();
    if (text.length < 60) return;

    const exclaimCount = (text.match(/!/g) || []).length;
    const capsRatio = (text.match(/[A-Z]{3,}/g) || []).length / text.length;
    const sensationalWords = ['shocking', 'outrageous', 'unbelievable', 'you won\'t believe', 'doctors hate', 'secret they don\'t want'];

    const hasSensational = sensationalWords.some(w => text.toLowerCase().includes(w));
    const score = (exclaimCount * 0.05) + (capsRatio * 10) + (hasSensational ? 0.3 : 0);

    if (score > sensitivityThreshold) {
      const range = document.createRange();
      range.selectNode(node);
      const highlight = document.createElement('mark');
      highlight.style.cssText = 'background:#fef2f2;color:#991b1b;padding:1px 2px;border-radius:2px;border-bottom:2px solid #ef4444;cursor:help';
      highlight.title = 'Potentially misleading content (Factly)';
      highlight.dataset.factlyFlagged = 'true';
      try {
        range.surroundContents(highlight);
        factlyHighlights.push(highlight);
      } catch (e) {}
    }
  });
}

function clearHighlights() {
  factlyHighlights.forEach(el => {
    const parent = el.parentNode;
    if (parent) {
      while (el.firstChild) parent.insertBefore(el.firstChild, el);
      parent.removeChild(el);
    }
  });
  factlyHighlights = [];
}

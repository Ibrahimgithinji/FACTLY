const STORAGE_KEY = 'factlySettings';

async function getApiBase() {
  const result = await chrome.storage.local.get(STORAGE_KEY);
  return (result[STORAGE_KEY] || {}).apiBase || FACTLY_CONFIG.API_BASE;
}

function getFrontendUrl() {
  return FACTLY_CONFIG.FRONTEND_URL;
}

const $ = (id) => document.getElementById(id);

let currentResult = null;

function showView(viewId) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  $(viewId).classList.add('active');
}

$('claim-input').addEventListener('input', () => {
  const text = $('claim-input').value.trim();
  $('verify-btn').disabled = !text || text.length < 3;
});

$('claim-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!$('verify-btn').disabled) verifyClaim();
  }
});

$('verify-btn').addEventListener('click', verifyClaim);

$('page-btn').addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const [result] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        const title = document.title;
        const meta = document.querySelector('meta[name="description"]');
        const desc = meta ? meta.content : '';
        const text = document.body.innerText.slice(0, 2000);
        return `${title}\n\n${desc ? desc + '\n\n' : ''}${text}`;
      }
    });
    if (result?.result) {
      $('claim-input').value = result.result.slice(0, 5000);
      $('claim-input').dispatchEvent(new Event('input'));
      verifyClaim();
    }
  } catch (err) {
    showStatus('Could not read page content. Try pasting text manually.', 'error');
  }
});

$('back-btn').addEventListener('click', () => {
  $('claim-input').value = '';
  $('claim-input').dispatchEvent(new Event('input'));
  showView('view-input');
});

$('history-btn').addEventListener('click', loadHistory);

$('history-back-btn').addEventListener('click', () => showView('view-input'));

$('clear-history-btn').addEventListener('click', async () => {
  await chrome.storage.local.set({ factlyHistory: [] });
  loadHistory();
});

$('error-retry-btn').addEventListener('click', () => showView('view-input'));

$('full-report-btn').addEventListener('click', () => {
  const params = new URLSearchParams({ text: $('claim-input').value || currentResult?.query || '' });
  chrome.tabs.create({ url: `${getFrontendUrl()}/verify?${params}` });
});

$('share-btn').addEventListener('click', async () => {
  if (!currentResult) return;
  const text = `Factly Score: ${currentResult.factly_score}/100 - ${currentResult.classification}`;
  try {
    await navigator.clipboard.writeText(text);
    showStatus('Result copied to clipboard!', 'success');
  } catch {
    showStatus('Could not copy to clipboard', 'error');
  }
});

async function verifyClaim() {
  const text = $('claim-input').value.trim();
  if (!text || text.length < 3) return;

  showView('view-loading');

  try {
    const apiBase = await getApiBase();
    const response = await fetch(`${apiBase}/quick-check/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.error || `Server error (${response.status})`);
    }

    const data = await response.json();
    currentResult = { ...data, query: text };

    await saveHistory(text, data);
    showResult(data);
  } catch (err) {
    $('error-title').textContent = 'Verification Failed';
    $('error-msg').textContent = err.message.includes('Failed to fetch')
      ? 'Cannot connect to Factly API. Make sure the backend server is running.'
      : err.message;
    showView('view-error');
  }
}

function showResult(data) {
  const score = data.factly_score;
  let color, label, labelClass;
  if (score >= 66) {
    color = '#22c55e'; label = 'Likely Authentic'; labelClass = 'authentic';
  } else if (score >= 36) {
    color = '#eab308'; label = 'Uncertain'; labelClass = 'uncertain';
  } else {
    color = '#ef4444'; label = 'Likely Fake'; labelClass = 'fake';
  }

  const ring = $('score-ring');
  const circumference = 339.292;
  const offset = circumference - (score / 100) * circumference;
  ring.style.strokeDashoffset = offset;
  ring.style.stroke = color;

  $('score-value').textContent = score;
  $('score-label').textContent = label;
  $('score-label').className = `score-label ${labelClass}`;
  $('confidence-value').textContent = data.confidence_level || '--';
  $('sources-value').textContent = `${data.sources_consulted || 0} sources`;

  const list = $('evidence-list');
  list.innerHTML = '';
  if (data.brief_evidence && data.brief_evidence.length > 0) {
    const sentiments = ['positive', 'neutral', 'negative'];
    data.brief_evidence.forEach((item, i) => {
      const li = document.createElement('li');
      li.className = sentiments[i % 3];
      li.textContent = item;
      list.appendChild(li);
    });
  } else {
    const li = document.createElement('li');
    li.className = 'neutral';
    li.textContent = 'No evidence found for this claim.';
    list.appendChild(li);
  }

  showView('view-result');
}

async function loadHistory() {
  showView('view-history');
  const list = $('history-list');
  list.innerHTML = '<div class="empty-state">Loading...</div>';

  try {
    const result = await chrome.storage.local.get('factlyHistory');
    const history = result.factlyHistory || [];
    list.innerHTML = '';

    if (history.length === 0) {
      list.innerHTML = '<div class="empty-state">No verification history yet.</div>';
      return;
    }

    history.forEach((item, idx) => {
      const div = document.createElement('div');
      div.className = 'history-item';

      let scoreClass = 'medium';
      if (item.score >= 66) scoreClass = 'high';
      else if (item.score <= 35) scoreClass = 'low';

      const time = item.timestamp ? new Date(item.timestamp).toLocaleString() : '';
      div.innerHTML = `
        <div class="history-score ${scoreClass}">${escapeHtml(String(item.score))}</div>
        <div class="history-text">${escapeHtml(item.text || 'Unknown')}</div>
        <div class="history-time">${escapeHtml(time)}</div>
      `;
      const rawText = item.fullText || item.text || '';
      div.addEventListener('click', () => {
        $('claim-input').value = rawText;
        $('claim-input').dispatchEvent(new Event('input'));
        verifyClaim();
      });
      list.appendChild(div);
    });
  } catch {
    list.innerHTML = '<div class="empty-state">Could not load history.</div>';
  }
}

async function saveHistory(text, data) {
  const result = await chrome.storage.local.get('factlyHistory');
  const history = result.factlyHistory || [];
  history.unshift({
    text: text.slice(0, 100),
    fullText: text,
    score: data.factly_score,
    classification: data.classification,
    timestamp: new Date().toISOString()
  });
  await chrome.storage.local.set({ factlyHistory: history.slice(0, 50) });
}

function showStatus(msg, type) {
  const el = $('status-msg');
  el.textContent = msg;
  el.className = `status-message ${type}`;
  setTimeout(() => { el.className = 'status-message'; }, 4000);
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str == null ? '' : String(str);
  return div.innerHTML;
}

(async function init() {
  const result = await chrome.storage.local.get('pendingVerification');
  if (result.pendingVerification) {
    $('claim-input').value = result.pendingVerification;
    $('claim-input').dispatchEvent(new Event('input'));
    await chrome.storage.local.remove('pendingVerification');
    verifyClaim();
  }

  const autoResult = (await chrome.storage.local.get('lastAutoResult')).lastAutoResult;
  if (autoResult) {
    currentResult = autoResult;
  }
})();

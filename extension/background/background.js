const STORAGE_KEY = 'factlySettings';
const HISTORY_KEY = 'factlyHistory';
const API_BASE = 'http://localhost:8000/api/verification';

const NEWS_DOMAINS = [
  'bbc.com', 'bbc.co.uk', 'cnn.com', 'reuters.com', 'ap.org',
  'nytimes.com', 'theguardian.com', 'wsj.com', 'washingtonpost.com',
  'nbcnews.com', 'cbsnews.com', 'abcnews.go.com', 'foxnews.com',
  'usatoday.com', 'latimes.com', 'politico.com', 'huffpost.com',
  'buzzfeednews.com', 'vice.com', 'vox.com', 'bloomberg.com',
  'news.yahoo.com', 'news.google.com', 'msnbc.com', 'npr.org',
  'aljazeera.com', 'dw.com', 'france24.com', 'rt.com', 'scmp.com'
];

async function getSettings() {
  const result = await chrome.storage.local.get(STORAGE_KEY);
  return result[STORAGE_KEY] || { apiBase: API_BASE, autoDetect: true };
}

chrome.runtime.onInstalled.addListener(async () => {
  await chrome.storage.local.set({
    [STORAGE_KEY]: { apiBase: API_BASE, autoDetect: true },
    [HISTORY_KEY]: []
  });

  chrome.contextMenus.create({
    id: 'verify-selection',
    title: 'Verify with Factly',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'verify-page',
    title: 'Fact-Check this Page',
    contexts: ['page']
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'verify-selection') {
    await chrome.storage.local.set({
      pendingVerification: info.selectionText
    });
    chrome.action.openPopup();
  }

  if (info.menuItemId === 'verify-page') {
    const [result] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        const meta = document.querySelector('meta[name="description"]');
        const title = document.title;
        const description = meta ? meta.content : '';
        const text = document.body.innerText.slice(0, 3000);
        return `Title: ${title}\n\nDescription: ${description}\n\n${text}`;
      }
    });

    await chrome.storage.local.set({
      pendingVerification: result.result
    });
    chrome.action.openPopup();
  }
});

async function getPageText(tabId) {
  const [result] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      const article = document.querySelector('article');
      if (article) return article.innerText.slice(0, 2000);
      const main = document.querySelector('main');
      if (main) return main.innerText.slice(0, 2000);
      return document.body.innerText.slice(0, 2000);
    }
  });
  return result ? result.result : '';
}

function isNewsDomain(url) {
  try {
    const hostname = new URL(url).hostname.replace('www.', '');
    return NEWS_DOMAINS.some(domain => hostname === domain || hostname.endsWith('.' + domain));
  } catch {
    return false;
  }
}

async function autoVerify(tabId, url) {
  if (!isNewsDomain(url)) return;

  const text = await getPageText(tabId);
  if (!text || text.length < 100) return;

  try {
    const settings = await getSettings();
    const response = await fetch(`${settings.apiBase}/quick-check/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text.slice(0, 1000) })
    });

    if (!response.ok) return;

    const data = await response.json();
    const score = data.factly_score;

    let color, title;
    if (score >= 66) {
      color = '#22c55e';
      title = `Factly: Likely Authentic (${score}/100)`;
    } else if (score >= 36) {
      color = '#eab308';
      title = `Factly: Uncertain (${score}/100)`;
    } else {
      color = '#ef4444';
      title = `Factly: Likely Fake (${score}/100)`;
    }

    await chrome.action.setBadgeText({ tabId, text: String(score) });
    await chrome.action.setBadgeBackgroundColor({ tabId, color });
    await chrome.action.setTitle({ tabId, title });

    await chrome.storage.local.set({
      lastAutoResult: { ...data, url, timestamp: new Date().toISOString() }
    });

    chrome.tabs.sendMessage(tabId, {
      type: 'FACTLY_AUTO_RESULT',
      data: { ...data, url }
    }).catch(() => {});
  } catch (err) {
    console.error('Factly auto-verify failed:', err);
  }
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && !tab.url.startsWith('chrome://')) {
    setTimeout(() => autoVerify(tabId, tab.url), 1500);
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'QUICK_CHECK') {
    (async () => {
      try {
        const settings = await getSettings();
        const response = await fetch(`${settings.apiBase}/quick-check/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: message.text })
        });
        const data = await response.json();

        const history = (await chrome.storage.local.get(HISTORY_KEY))[HISTORY_KEY] || [];
        history.unshift({
          text: message.text.slice(0, 100),
          score: data.factly_score,
          classification: data.classification,
          timestamp: new Date().toISOString()
        });
        await chrome.storage.local.set({ [HISTORY_KEY]: history.slice(0, 50) });

        sendResponse({ success: true, data });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (message.type === 'GET_HISTORY') {
    (async () => {
      const history = (await chrome.storage.local.get(HISTORY_KEY))[HISTORY_KEY] || [];
      sendResponse(history);
    })();
    return true;
  }
});

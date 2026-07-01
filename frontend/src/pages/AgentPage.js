import React, { useState, useCallback, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FactlyScoreBadge, FactlyScoreInline, FactlyScoreBar } from '../components/FactlyScoreBadge';
import { API_BASE_URL } from '../utils/constants';
import './AgentPage.css';

const AGENT_API = `${API_BASE_URL}/api/agent`;

function formatTime(d) {
  const date = new Date(d);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scoreColor(score) {
  if (score >= 70) return '#22c55e';
  if (score >= 40) return '#eab308';
  return '#ef4444';
}

const ASK_FACTLY_QUESTIONS = [
  { q: 'Is climate change really caused by humans?', category: 'Science', asked_by: 'Priya M.', answered: true },
  { q: 'Did the government really announce free electricity?', category: 'Politics', asked_by: 'Rahul K.', answered: true },
  { q: 'Can 5G networks spread viruses?', category: 'Technology', asked_by: 'Amina S.', answered: true },
];

function AgentPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [digest, setDigest] = useState(null);
  const [digestLoading, setDigestLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('chat');
  const [askQuestion, setAskQuestion] = useState('');
  const [askLoading, setAskLoading] = useState(false);
  const [askHistory, setAskHistory] = useState([]);
  const chatEnd = useRef(null);

  useEffect(() => {
    fetch(`${AGENT_API}/digest/?hours=24`)
      .then((r) => r.json())
      .then((d) => {
        setDigest(d);
        setDigestLoading(false);
      })
      .catch(() => setDigestLoading(false));
  }, []);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: q }]);
    setLoading(true);
    try {
      const resp = await fetch(`${AGENT_API}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ query: q }),
      });
      const data = await resp.json();
      setMessages((prev) => [
        ...prev,
        { role: 'agent', content: data.answer || 'Sorry, I couldn\'t find anything.', sources: data.sources || [], fact_checks: data.fact_checks || [] },
      ]);
    } catch {
      setMessages((prev) => [...prev, { role: 'agent', content: 'Network error. Please try again.' }]);
    }
    setLoading(false);
  }, [input, loading]);

  const submitAskQuestion = useCallback(async () => {
    const q = askQuestion.trim();
    if (!q || askLoading) return;
    setAskLoading(true);
    try {
      const resp = await fetch(`${AGENT_API}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ query: q }),
      });
      const data = await resp.json();
      setAskHistory((prev) => [
        { question: q, answer: data.answer || 'No answer available', sources: data.sources || [], fact_checks: data.fact_checks || [] },
        ...prev,
      ]);
      setAskQuestion('');
    } catch {
      setAskHistory((prev) => [
        { question: q, answer: 'Network error. Please try again.', sources: [], fact_checks: [] },
        ...prev,
      ]);
    }
    setAskLoading(false);
  }, [askQuestion, askLoading]);

  const quickQuestions = [
    'What\'s happening in tech today?',
    'Verify the latest trending news',
    'What are the top global stories?',
    'Is there any misinformation spreading?',
  ];

  return (
    <div className="agent-page">
      <div className="agent-header">
        <div className="agent-header__icon">
          <span>F</span>
        </div>
        <h1>Factly Agent</h1>
        <p className="agent-subtitle">Your AI news assistant — ask questions, get verified answers</p>
      </div>

      <div className="agent-tabs">
        <button className={`agent-tab ${activeTab === 'chat' ? 'active' : ''}`} onClick={() => setActiveTab('chat')}>Chat</button>
        <button className={`agent-tab ${activeTab === 'digest' ? 'active' : ''}`} onClick={() => setActiveTab('digest')}>Daily Digest</button>
        <button className={`agent-tab ${activeTab === 'ask' ? 'active' : ''}`} onClick={() => setActiveTab('ask')}>Ask Factly</button>
      </div>

      {activeTab === 'chat' && (
        <div className="agent-chat-container">
          <div className="agent-messages">
            {messages.length === 0 && (
              <div className="agent-welcome">
                <div className="agent-welcome-icon">
                  <div className="agent-welcome-icon__inner">F</div>
                </div>
                <h2>Hi, I'm the Factly Agent</h2>
                <p>Ask me about any news topic, and I'll fetch, verify, and summarize information from trusted sources.</p>
                <div className="quick-questions">
                  {quickQuestions.map((qq, i) => (
                    <button key={i} className="quick-q-btn" onClick={() => { setInput(qq); }}>
                      {qq}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                className={`agent-message ${msg.role}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="msg-avatar">
                  {msg.role === 'user' ? (
                    <span className="msg-avatar__user">You</span>
                  ) : (
                    <span className="msg-avatar__agent">F</span>
                  )}
                </div>
                <div className="msg-content">
                  <div className="msg-text">{msg.content}</div>
                  {msg.fact_checks && msg.fact_checks.length > 0 && (
                    <div className="msg-fact-checks">
                      <strong>Fact Check Summary</strong>
                      {msg.fact_checks.map((fc, j) => (
                        <div key={j} className="fact-check-item">
                          <FactlyScoreInline
                            score={fc.score || (fc.verdict === 'true' || fc.verdict === 'mostly_true' ? 85 : 25)}
                            verdict={fc.verdict || fc.label}
                          />
                          <span className="fact-check-claim">{fc.claim}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="msg-sources">
                      <strong>Sources ({msg.sources.length})</strong>
                      {msg.sources.slice(0, 4).map((src, j) => (
                        <div key={j} className="source-card">
                          <div className="source-title">
                            <span>{src.title || 'Untitled'}</span>
                            <FactlyScoreInline
                              score={src.credibility_score}
                              verdict={src.verdict}
                            />
                          </div>
                          <div className="source-meta">
                            <span>{src.source_name || src.source || 'Unknown'}</span>
                            {src.url && <a href={src.url} target="_blank" rel="noreferrer">Read more</a>}
                          </div>
                          <FactlyScoreBar score={src.credibility_score} verdict={src.verdict} showScore={false} />
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="msg-time">{formatTime(new Date().toISOString())}</div>
                </div>
              </motion.div>
            ))}
            {loading && (
              <div className="agent-message agent">
                <div className="msg-avatar">
                  <span className="msg-avatar__agent">F</span>
                </div>
                <div className="msg-content">
                  <div className="typing-indicator"><span /><span /><span /></div>
                </div>
              </div>
            )}
            <div ref={chatEnd} />
          </div>

          <div className="agent-input-bar">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about any news topic..."
              disabled={loading}
            />
            <motion.button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              whileTap={{ scale: 0.95 }}
            >
              {loading ? '...' : 'Send'}
            </motion.button>
          </div>
        </div>
      )}

      {activeTab === 'digest' && (
        <div className="agent-digest">
          {digestLoading ? (
            <div className="loading-container"><div className="loading-spinner" /><p>Loading today's digest...</p></div>
          ) : digest ? (
            <>
              <div className="digest-date">{digest.date}</div>

              {digest.verification_summary && (
                <div className="digest-summary">
                  <div className="summary-card">
                    <span className="summary-num">{digest.verification_summary.total_stories}</span>
                    <span className="summary-label">Stories Analyzed</span>
                  </div>
                  <div className="summary-card">
                    <span className="summary-num" style={{ color: '#22c55e' }}>{digest.verification_summary.verified_true}</span>
                    <span className="summary-label">Verified True</span>
                  </div>
                  <div className="summary-card">
                    <span className="summary-num" style={{ color: '#ef4444' }}>{digest.verification_summary.suspicious}</span>
                    <span className="summary-label">Suspicious</span>
                  </div>
                  <div className="summary-card">
                    <FactlyScoreBadge
                      score={digest.verification_summary.trust_score}
                      size="sm"
                      showLabel={false}
                      animated={true}
                    />
                    <span className="summary-label">Trust Score</span>
                  </div>
                </div>
              )}

              {digest.headline && (
                <div className="digest-headline">
                  <h3>Top Story</h3>
                  <h2>{digest.headline.title}</h2>
                  <div className="digest-headline-meta">
                    <span>{digest.headline.source_name || digest.headline.source}</span>
                    <FactlyScoreInline
                      score={digest.headline.credibility_score}
                      verdict={digest.headline.verdict}
                    />
                  </div>
                </div>
              )}

              {digest.top_stories && digest.top_stories.length > 0 && (
                <div className="digest-stories">
                  <h3>Top Stories</h3>
                  <div className="stories-list">
                    {digest.top_stories.slice(0, 8).map((story, i) => (
                      <div key={i} className="story-card">
                        <div className="story-rank">{i + 1}</div>
                        <div className="story-info">
                          <div className="story-title">{story.title}</div>
                          <div className="story-meta">
                            <span>{story.source_name || story.source || 'Unknown'}</span>
                            <FactlyScoreInline score={story.credibility_score} verdict={story.verdict} />
                          </div>
                          <FactlyScoreBar score={story.credibility_score} verdict={story.verdict} showScore={false} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {digest.categories && Object.keys(digest.categories).length > 0 && (
                <div className="digest-categories">
                  <h3>By Category</h3>
                  <div className="categories-grid">
                    {Object.entries(digest.categories).map(([cat, items]) => (
                      <div key={cat} className="category-card">
                        <h4>{cat.charAt(0).toUpperCase() + cat.slice(1)}</h4>
                        {items.map((item, i) => (
                          <div key={i} className="category-item">
                            <span className="cat-item-title">{item.title}</span>
                            <FactlyScoreInline score={item.credibility_score} verdict={item.verdict} />
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <p className="digest-empty">Could not load digest. Try again later.</p>
          )}
        </div>
      )}

      {activeTab === 'ask' && (
        <div className="ask-factly-section">
          <div className="ask-factly-intro">
            <h2>Ask Factly</h2>
            <p>Submit a question about any claim or news topic. Our AI agent researches and verifies it for you.</p>
          </div>

          <div className="ask-factly-form">
            <input
              type="text"
              value={askQuestion}
              onChange={(e) => setAskQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && submitAskQuestion()}
              placeholder="e.g., Is it true that drinking lemon water cures COVID?"
              disabled={askLoading}
            />
            <motion.button
              onClick={submitAskQuestion}
              disabled={askLoading || !askQuestion.trim()}
              whileTap={{ scale: 0.95 }}
            >
              {askLoading ? 'Researching...' : 'Ask'}
            </motion.button>
          </div>

          <div className="ask-factly-popular">
            <h3>Popular Questions</h3>
            <div className="ask-popular-list">
              {ASK_FACTLY_QUESTIONS.map((item, i) => (
                <div
                  key={i}
                  className="ask-popular-item"
                  onClick={() => setAskQuestion(item.q)}
                  role="button"
                  tabIndex={0}
                >
                  <span className="ask-popular-cat">{item.category}</span>
                  <span className="ask-popular-q">{item.q}</span>
                  <span className="ask-popular-by">by {item.asked_by}</span>
                </div>
              ))}
            </div>
          </div>

          {askHistory.length > 0 && (
            <div className="ask-factly-history">
              <h3>Your Questions</h3>
              <AnimatePresence>
                {askHistory.map((item, i) => (
                  <motion.div
                    key={i}
                    className="ask-history-item"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                  >
                    <div className="ask-history-q">{item.question}</div>
                    <div className="ask-history-a">{item.answer}</div>
                    {item.sources && item.sources.length > 0 && (
                      <div className="ask-history-sources">
                        {item.sources.slice(0, 3).map((src, j) => (
                          <span key={j} className="ask-source-chip">
                            {src.source_name || src.source || 'Source'}
                          </span>
                        ))}
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AgentPage;

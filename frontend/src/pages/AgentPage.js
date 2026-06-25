import React, { useState, useCallback, useEffect, useRef } from "react";
import { API_BASE_URL } from "../utils/constants";
import "./AgentPage.css";

const AGENT_API = `${API_BASE_URL}/api/agent`;

function formatTime(d) {
  const date = new Date(d);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function scoreColor(score) {
  if (score >= 70) return "#22c55e";
  if (score >= 40) return "#eab308";
  return "#ef4444";
}

function AgentPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [digest, setDigest] = useState(null);
  const [digestLoading, setDigestLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("chat");
  const chatEnd = useRef(null);

  // Load digest on mount
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
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);
    try {
      const resp = await fetch(`${AGENT_API}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ query: q }),
      });
      const data = await resp.json();
      setMessages((prev) => [
        ...prev,
        { role: "agent", content: data.answer || "Sorry, I couldn't find anything.", sources: data.sources || [], fact_checks: data.fact_checks || [] },
      ]);
    } catch {
      setMessages((prev) => [...prev, { role: "agent", content: "Network error. Please try again." }]);
    }
    setLoading(false);
  }, [input, loading]);

  const quickQuestions = [
    "What's happening in tech today?",
    "Verify the latest trending news",
    "What are the top global stories?",
    "Is there any misinformation spreading?",
  ];

  return (
    <div className="agent-page">
      <div className="agent-header">
        <h1>Factly Agent</h1>
        <p className="agent-subtitle">Your AI news assistant — ask questions, get verified answers</p>
      </div>

      <div className="agent-tabs">
        <button className={`agent-tab ${activeTab === "chat" ? "active" : ""}`} onClick={() => setActiveTab("chat")}>Chat</button>
        <button className={`agent-tab ${activeTab === "digest" ? "active" : ""}`} onClick={() => setActiveTab("digest")}>Daily Digest</button>
      </div>

      {activeTab === "chat" && (
        <div className="agent-chat-container">
          <div className="agent-messages">
            {messages.length === 0 && (
              <div className="agent-welcome">
                <div className="agent-welcome-icon">🤖</div>
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
              <div key={i} className={`agent-message ${msg.role}`}>
                <div className="msg-avatar">{msg.role === "user" ? "👤" : "🤖"}</div>
                <div className="msg-content">
                  <div className="msg-text">{msg.content}</div>
                  {msg.fact_checks && msg.fact_checks.length > 0 && (
                    <div className="msg-fact-checks">
                      <strong>Fact Check Summary</strong>
                      {msg.fact_checks.map((fc, j) => (
                        <div key={j} className="fact-check-item">
                          <span className="fact-check-label" style={{ background: fc.verdict === "true" || fc.verdict === "mostly_true" ? "#22c55e20" : "#ef444420", color: fc.verdict === "true" || fc.verdict === "mostly_true" ? "#22c55e" : "#ef44444" }}>
                            {fc.label}
                          </span>
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
                            <span>{src.title || "Untitled"}</span>
                            <span className="source-score" style={{ color: scoreColor(src.credibility_score) }}>
                              {src.credibility_score}/100
                            </span>
                          </div>
                          <div className="source-meta">
                            <span>{src.source_name || src.source || "Unknown"}</span>
                            {src.url && <a href={src.url} target="_blank" rel="noreferrer">Read more →</a>}
                          </div>
                          <div className="source-bar">
                            <div className="source-bar-fill" style={{ width: `${src.credibility_score || 50}%`, background: scoreColor(src.credibility_score) }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="msg-time">{formatTime(new Date().toISOString())}</div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="agent-message agent">
                <div className="msg-avatar">🤖</div>
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
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Ask about any news topic..."
              disabled={loading}
            />
            <button onClick={sendMessage} disabled={loading || !input.trim()}>
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      )}

      {activeTab === "digest" && (
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
                    <span className="summary-num" style={{ color: "#22c55e" }}>{digest.verification_summary.verified_true}</span>
                    <span className="summary-label">Verified True</span>
                  </div>
                  <div className="summary-card">
                    <span className="summary-num" style={{ color: "#ef4444" }}>{digest.verification_summary.suspicious}</span>
                    <span className="summary-label">Suspicious</span>
                  </div>
                  <div className="summary-card">
                    <span className="summary-num">{digest.verification_summary.trust_score}%</span>
                    <span className="summary-label">Trust Score</span>
                  </div>
                </div>
              )}

              {digest.headline && (
                <div className="digest-headline">
                  <h3>📰 Top Story</h3>
                  <h2>{digest.headline.title}</h2>
                  <div className="digest-headline-meta">
                    <span>{digest.headline.source_name || digest.headline.source}</span>
                    <span className="headline-score" style={{ color: scoreColor(digest.headline.credibility_score) }}>
                      Score: {digest.headline.credibility_score}/100
                    </span>
                    <span className={`headline-verdict ${digest.headline.verdict}`}>
                      {digest.headline.verdict}
                    </span>
                  </div>
                </div>
              )}

              {digest.top_stories && digest.top_stories.length > 0 && (
                <div className="digest-stories">
                  <h3>📊 Top Stories</h3>
                  <div className="stories-list">
                    {digest.top_stories.slice(0, 8).map((story, i) => (
                      <div key={i} className="story-card">
                        <div className="story-rank">{i + 1}</div>
                        <div className="story-info">
                          <div className="story-title">{story.title}</div>
                          <div className="story-meta">
                            <span>{story.source_name || story.source || "Unknown"}</span>
                            <span className="story-verdict" style={{ color: scoreColor(story.credibility_score) }}>
                              {story.verdict} ({story.credibility_score})
                            </span>
                          </div>
                          <div className="source-bar">
                            <div className="source-bar-fill" style={{ width: `${story.credibility_score || 50}%`, background: scoreColor(story.credibility_score) }} />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {digest.categories && Object.keys(digest.categories).length > 0 && (
                <div className="digest-categories">
                  <h3>📂 By Category</h3>
                  <div className="categories-grid">
                    {Object.entries(digest.categories).map(([cat, items]) => (
                      <div key={cat} className="category-card">
                        <h4>{cat.charAt(0).toUpperCase() + cat.slice(1)}</h4>
                        {items.map((item, i) => (
                          <div key={i} className="category-item">
                            <span className="cat-item-title">{item.title}</span>
                            <span className="cat-item-score" style={{ color: scoreColor(item.credibility_score) }}>
                              {item.credibility_score}
                            </span>
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
    </div>
  );
}

export default AgentPage;

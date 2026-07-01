import React, { useMemo, useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import ArticleCard from '../components/ArticleCard';
import Sidebar from '../components/Sidebar';
import TrendingTopics from '../components/TrendingTopics';
import TrendingClaims from '../components/TrendingClaims';
import { FactlyScoreBadge, FactlyScoreInline, FactlyScoreBar } from '../components/FactlyScoreBadge';
import { RevealOnScroll, StaggerContainer, StaggerItem, CountUp } from '../components/Animations';
import SEOMeta from '../components/SEOMeta';
import { CONTENT_ENDPOINTS } from '../utils/api';
import { API_BASE_URL } from '../utils/constants';
import { ArticleCardSkeleton, SidebarSkeleton } from '../components/Skeleton';
import './HomePage.css';

const HOMEPAGE_POLL_MS = 5 * 60 * 1000;

const formatRelativeTime = (dateString) => {
  if (!dateString) return null;
  const diff = Date.now() - new Date(dateString).getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return new Date(dateString).toLocaleDateString();
};

const CLAIM_COLLECTIONS = [
  {
    id: 'viral-social',
    title: '8 viral social media claims this week',
    category: 'Social Media',
    count: 8,
    avgScore: 34,
    verdict: 'mostly_false',
  },
  {
    id: 'health-myths',
    title: '6 health myths that won\'t go away',
    category: 'Health',
    count: 6,
    avgScore: 28,
    verdict: 'false',
  },
  {
    id: 'election-facts',
    title: '10 claims about the upcoming elections',
    category: 'Politics',
    count: 10,
    avgScore: 52,
    verdict: 'half_true',
  },
  {
    id: 'climate-check',
    title: '5 climate statements fact-checked',
    category: 'Science',
    count: 5,
    avgScore: 61,
    verdict: 'mostly_true',
  },
];

const QUIZ_CLAIMS = [
  { claim: 'Drinking lemon water cures COVID-19', answer: false, explanation: 'No scientific evidence supports this claim. COVID-19 requires medical treatment.' },
  { claim: 'The Great Wall of China is visible from space', answer: false, explanation: 'Astronauts have confirmed it is not visible to the naked eye from orbit.' },
  { claim: 'Honey never spoils', answer: true, explanation: 'Archaeologists found 3000-year-old honey in Egyptian tombs that was still edible.' },
  { claim: 'Humans use only 10% of their brain', answer: false, explanation: 'Brain scans show activity throughout the entire brain, even during sleep.' },
  { claim: 'Vaccines undergo years of safety testing before approval', answer: true, explanation: 'Vaccines go through multiple phases of clinical trials before regulatory approval.' },
  { claim: '5G towers cause COVID-19', answer: false, explanation: 'Viruses cannot travel via radio waves. This has been thoroughly debunked by scientists worldwide.' },
];

function SectionGrid({ section }) {
  if (!section || !section.articles || section.articles.length === 0) return null;
  const { category, articles } = section;

  return (
    <RevealOnScroll>
      <section className="home-section">
        <div className="home-section__header">
          <div>
            <span className="section-label">Desk</span>
            <h2 className="home-section__title">{category.name}</h2>
          </div>
          <Link to={`/category/${category.slug}`} className="home-section__view-all">View all</Link>
        </div>
        <StaggerContainer className="home-section__grid" staggerDelay={0.08}>
          {articles.slice(0, 4).map((article) => (
            <StaggerItem key={article.id}>
              <ArticleCard article={article} compact />
            </StaggerItem>
          ))}
        </StaggerContainer>
      </section>
    </RevealOnScroll>
  );
}

function VerificationWidget() {
  const [claim, setClaim] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const submitClaim = (event) => {
    event.preventDefault();
    const query = claim.trim();
    window.location.href = query ? `/verify?claim=${encodeURIComponent(query)}` : '/verify';
  };

  return (
    <RevealOnScroll>
      <section className="verification-widget" aria-labelledby="verification-widget-title">
        <div className="verification-widget__header">
          <span className="section-label">Fact-check engine</span>
          <h2 id="verification-widget-title">Verify a claim before it travels.</h2>
        </div>
        <form className="verification-widget__form" onSubmit={submitClaim}>
          <label className="sr-only" htmlFor="claim-input">Claim to verify</label>
          <textarea
            id="claim-input"
            value={claim}
            onChange={(event) => setClaim(event.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Paste a headline, claim, post, or quote..."
            rows="4"
          />
          <motion.button
            type="submit"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Verify this claim
          </motion.button>
        </form>
        <div className="verification-widget__signals">
          <span>Source trace</span>
          <span>Evidence score</span>
          <span>Verdict history</span>
        </div>
      </section>
    </RevealOnScroll>
  );
}

function LatestRail({ articles }) {
  if (!articles || articles.length === 0) return null;

  return (
    <aside className="latest-rail" aria-labelledby="latest-rail-title">
      <div className="latest-rail__header">
        <span className="section-label">Live file</span>
        <h2 id="latest-rail-title">Latest</h2>
      </div>
      <div className="latest-rail__list">
        {articles.slice(0, 6).map((article, index) => (
          <Link key={article.id} to={`/article/${article.slug}`} className="latest-rail__item">
            <span className="latest-rail__number">{String(index + 1).padStart(2, '0')}</span>
            <span className="latest-rail__content">
              {article.category && <span className="latest-rail__category">{article.category.name}</span>}
              <strong>{article.title}</strong>
            </span>
          </Link>
        ))}
      </div>
    </aside>
  );
}

function HeroSection({ leadArticle, stats }) {
  return (
    <RevealOnScroll>
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="hero-pulse" />
            Live Fact-Checking
          </div>
          <h1 className="hero-title">
            Don't share it until<br />
            <span className="hero-gradient">you verify it.</span>
          </h1>
          <p className="hero-desc">
            Factly uses AI + real-time source analysis to score any claim for credibility.
            Get instant verdicts backed by evidence.
          </p>
          <div className="hero-cta-row">
            <Link to="/verify" className="hero-cta hero-cta--primary">
              Verify a claim
            </Link>
            <Link to="/digest" className="hero-cta hero-cta--secondary">
              Daily briefing
            </Link>
          </div>
        </div>
        <div className="hero-stats">
          <div className="hero-stat">
            <span className="hero-stat__num"><CountUp target={1247} /></span>
            <span className="hero-stat__label">Claims checked today</span>
          </div>
          <div className="hero-stat">
            <span className="hero-stat__num"><CountUp target={89} suffix="%" /></span>
            <span className="hero-stat__label">Accuracy rate</span>
          </div>
          <div className="hero-stat">
            <span className="hero-stat__num"><CountUp target={340} /></span>
            <span className="hero-stat__label">Sources monitored</span>
          </div>
        </div>
      </section>
    </RevealOnScroll>
  );
}

function ClaimCollectionsSection() {
  return (
    <RevealOnScroll delay={0.1}>
      <section className="collections-section">
        <div className="collections-header">
          <div>
            <span className="section-label">Collections</span>
            <h2 className="collections-title">Grouped fact-checks</h2>
          </div>
          <Link to="/trending" className="home-section__view-all">Browse all</Link>
        </div>
        <div className="collections-grid">
          {CLAIM_COLLECTIONS.map((col) => (
            <motion.div
              key={col.id}
              className="collection-card"
              whileHover={{ y: -4, boxShadow: '0 12px 32px rgba(0,0,0,0.1)' }}
              transition={{ duration: 0.2 }}
            >
              <div className="collection-card__top">
                <span className="collection-card__category">{col.category}</span>
                <span className="collection-card__count">{col.count} claims</span>
              </div>
              <h3 className="collection-card__title">{col.title}</h3>
              <div className="collection-card__bottom">
                <FactlyScoreBar score={col.avgScore} verdict={col.verdict} showScore={false} />
                <FactlyScoreInline score={col.avgScore} verdict={col.verdict} />
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </RevealOnScroll>
  );
}

function FactQuizSection() {
  const [currentQ, setCurrentQ] = useState(0);
  const [score, setScore] = useState(0);
  const [answered, setAnswered] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [quizDone, setQuizDone] = useState(false);
  const [quizStarted, setQuizStarted] = useState(false);

  const claim = QUIZ_CLAIMS[currentQ];

  const handleAnswer = (answer) => {
    if (answered) return;
    setSelectedAnswer(answer);
    setAnswered(true);
    if (answer === claim.answer) setScore((s) => s + 1);
  };

  const nextQuestion = () => {
    if (currentQ + 1 >= QUIZ_CLAIMS.length) {
      setQuizDone(true);
    } else {
      setCurrentQ((q) => q + 1);
      setAnswered(false);
      setSelectedAnswer(null);
    }
  };

  const restart = () => {
    setCurrentQ(0);
    setScore(0);
    setAnswered(false);
    setSelectedAnswer(null);
    setQuizDone(false);
  };

  return (
    <RevealOnScroll delay={0.15}>
      <section className="quiz-section">
        <div className="quiz-header">
          <span className="section-label">Daily Quiz</span>
          <h2 className="quiz-title">Real or Fake?</h2>
          <p className="quiz-subtitle">Test your fact-checking instincts</p>
        </div>

        {!quizStarted ? (
          <div className="quiz-intro">
            <div className="quiz-intro__icon">?</div>
            <p>{QUIZ_CLAIMS.length} questions to test whether you can spot misinformation</p>
            <button className="quiz-start-btn" onClick={() => setQuizStarted(true)}>
              Start the Quiz
            </button>
          </div>
        ) : quizDone ? (
          <div className="quiz-result">
            <div className="quiz-result__score">
              <FactlyScoreBadge
                score={Math.round((score / QUIZ_CLAIMS.length) * 100)}
                verdict={score >= QUIZ_CLAIMS.length * 0.7 ? 'true' : score >= QUIZ_CLAIMS.length * 0.4 ? 'half_true' : 'false'}
                size="lg"
              />
            </div>
            <p className="quiz-result__text">
              You got {score} out of {QUIZ_CLAIMS.length} correct!
            </p>
            <p className="quiz-result__verdict">
              {score >= QUIZ_CLAIMS.length * 0.7
                ? 'Sharp eye! You spot misinformation like a pro.'
                : score >= QUIZ_CLAIMS.length * 0.4
                ? 'Not bad, but some claims slipped past you.'
                : 'Watch out! You might be spreading misinformation.'}
            </p>
            <button className="quiz-start-btn" onClick={restart}>Play again</button>
          </div>
        ) : (
          <div className="quiz-active">
            <div className="quiz-progress">
              <div className="quiz-progress__bar">
                <motion.div
                  className="quiz-progress__fill"
                  animate={{ width: `${((currentQ + (answered ? 1 : 0)) / QUIZ_CLAIMS.length) * 100}%` }}
                />
              </div>
              <span className="quiz-progress__text">{currentQ + 1} / {QUIZ_CLAIMS.length}</span>
            </div>
            <p className="quiz-claim">"{claim.claim}"</p>
            <div className="quiz-buttons">
              <motion.button
                className={`quiz-btn quiz-btn--real ${selectedAnswer === true ? (claim.answer === true ? 'quiz-btn--correct' : 'quiz-btn--wrong') : ''}`}
                onClick={() => handleAnswer(true)}
                whileHover={!answered ? { scale: 1.04 } : {}}
                whileTap={!answered ? { scale: 0.96 } : {}}
                disabled={answered}
              >
                Real
              </motion.button>
              <motion.button
                className={`quiz-btn quiz-btn--fake ${selectedAnswer === false ? (claim.answer === false ? 'quiz-btn--correct' : 'quiz-btn--wrong') : ''}`}
                onClick={() => handleAnswer(false)}
                whileHover={!answered ? { scale: 1.04 } : {}}
                whileTap={!answered ? { scale: 0.96 } : {}}
                disabled={answered}
              >
                Fake
              </motion.button>
            </div>
            <AnimatePresence>
              {answered && (
                <motion.div
                  className="quiz-explanation"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                >
                  <div className={`quiz-verdict-badge ${claim.answer ? 'quiz-verdict--true' : 'quiz-verdict--false'}`}>
                    {claim.answer ? 'TRUE' : 'FALSE'}
                  </div>
                  <p>{claim.explanation}</p>
                  <button className="quiz-next-btn" onClick={nextQuestion}>
                    {currentQ + 1 >= QUIZ_CLAIMS.length ? 'See Results' : 'Next Question'}
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </section>
    </RevealOnScroll>
  );
}

function AlertBanner() {
  const [alerts, setAlerts] = useState([]);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/alerts/?limit=3`)
      .then((r) => r.json())
      .then((data) => {
        const results = data.results || data.alerts || [];
        if (results.length > 0) {
          setAlerts(results.slice(0, 3));
          setVisible(true);
        }
      })
      .catch(() => {});
  }, []);

  if (!visible || alerts.length === 0) return null;

  return (
    <motion.div
      className="alert-banner"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      <div className="alert-banner__inner">
        <span className="alert-banner__icon">!</span>
        <div className="alert-banner__content">
          <strong>Misinformation Alert:</strong>{' '}
          {alerts[0]?.alert_message || alerts[0]?.topic || 'Active misinformation campaigns detected'}
        </div>
        <Link to="/alerts" className="alert-banner__link">View all alerts</Link>
        <button className="alert-banner__close" onClick={() => setVisible(false)} aria-label="Dismiss">
          &times;
        </button>
      </div>
    </motion.div>
  );
}

export default function HomePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const pollRef = useRef(null);
  const mountedRef = useRef(false);

  const handleTopicClick = (topic) => {
    window.location.href = `/verify?topic=${encodeURIComponent(topic)}`;
  };

  const fetchHomeData = useCallback(async () => {
    try {
      const [homeRes, catRes] = await Promise.all([
        fetch(CONTENT_ENDPOINTS.HOMEPAGE),
        fetch(CONTENT_ENDPOINTS.CATEGORIES),
      ]);
      if (!mountedRef.current) return;
      const homeData = await homeRes.json();
      const catData = await catRes.json();
      setData(homeData);
      setCategories(catData);
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      if (!mountedRef.current) return;
      console.error('Failed to load homepage:', err);
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    fetchHomeData();

    pollRef.current = setInterval(fetchHomeData, HOMEPAGE_POLL_MS);

    const handleVisibility = () => {
      if (document.visibilityState === 'visible') fetchHomeData();
    };
    document.addEventListener('visibilitychange', handleVisibility);

    const handleOnline = () => fetchHomeData();
    window.addEventListener('online', handleOnline);

    return () => {
      mountedRef.current = false;
      clearInterval(pollRef.current);
      document.removeEventListener('visibilitychange', handleVisibility);
      window.removeEventListener('online', handleOnline);
    };
  }, [fetchHomeData]);

  const sectionKeys = data?.sections ? Object.keys(data.sections) : [];
  const leadArticle = data?.featured?.[0] || data?.latest?.[0];
  const secondaryArticles = useMemo(() => {
    const seen = new Set(leadArticle ? [leadArticle.id] : []);
    return [...(data?.featured || []), ...(data?.latest || [])]
      .filter((article) => {
        if (!article || seen.has(article.id)) return false;
        seen.add(article.id);
        return true;
      })
      .slice(0, 4);
  }, [data, leadArticle]);

  if (loading) {
    return (
      <div className="home-page">
        <div className="editorial-loader">
          <ArticleCardSkeleton featured />
          <ArticleCardSkeleton />
          <ArticleCardSkeleton />
          <SidebarSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="home-page">
      <SEOMeta />

      <AlertBanner />

      {data?.trending && data.trending.length > 0 && (
        <section className="home-ticker" aria-label="Trending articles">
          <span className="home-ticker__label">Now tracking</span>
          <div className="home-ticker__items">
            {data.trending.slice(0, 5).map((article) => (
              <Link key={article.id} to={`/article/${article.slug}`}>{article.title}</Link>
            ))}
          </div>
        </section>
      )}

      <div className="home-freshness">
        {lastUpdated && (
          <span>
            <span className="freshness-dot" />
            Updated {formatRelativeTime(lastUpdated)}
          </span>
        )}
        <button className="refresh-button" onClick={fetchHomeData}>
          Refresh
        </button>
      </div>

      <HeroSection leadArticle={leadArticle} />

      <section className="editorial-lead" aria-label="Top stories">
        <div className="editorial-lead__main">
          {leadArticle && <ArticleCard article={leadArticle} featured />}
        </div>
        <div className="editorial-lead__side">
          {secondaryArticles.slice(0, 2).map((article) => (
            <ArticleCard key={article.id} article={article} compact />
          ))}
        </div>
        <LatestRail articles={data?.latest} />
      </section>

      <section className="home-toolbelt" aria-label="Verification and trending claims">
        <VerificationWidget />
        <div className="claim-briefing">
          <div className="claim-briefing__header">
            <div>
              <span className="section-label">Claim briefing</span>
              <h2>Signals worth checking today</h2>
              <Link to="/verify">Open verifier</Link>
            </div>
          </div>
          <TrendingClaims />
        </div>
      </section>

      <ClaimCollectionsSection />

      <div className="home-engagement-row">
        <FactQuizSection />
        <div className="home-engagement-sidebar">
          <RevealOnScroll delay={0.2}>
            <div className="ask-factly-card">
              <span className="section-label">Ask Factly</span>
              <h3>Have a question?</h3>
              <p>Submit a claim and our AI agent will research and verify it for you.</p>
              <Link to="/agent" className="ask-factly-btn">Ask the Agent</Link>
            </div>
          </RevealOnScroll>
          <RevealOnScroll delay={0.25}>
            <div className="daily-briefing-card">
              <span className="section-label">Daily Briefing</span>
              <h3>Get the verified summary</h3>
              <p>Top stories, verification status, and trust scores — all in one place.</p>
              <Link to="/digest" className="ask-factly-btn">Read briefing</Link>
            </div>
          </RevealOnScroll>
        </div>
      </div>

      <div className="home-layout">
        <div className="home-layout__main">
          {sectionKeys.map((key) => (
            <SectionGrid key={key} section={data.sections[key]} />
          ))}

          <RevealOnScroll>
            <section className="home-section home-section--topics">
              <div className="home-section__header">
                <div>
                  <span className="section-label">Monitor</span>
                  <h2 className="home-section__title">Trending claims</h2>
                </div>
                <Link to="/trending" className="home-section__view-all">View all trends</Link>
              </div>
              <TrendingTopics onTopicClick={handleTopicClick} />
            </section>
          </RevealOnScroll>
        </div>

        <aside className="home-layout__sidebar">
          <Sidebar categories={categories} recentPosts={data?.latest} />
        </aside>
      </div>
    </div>
  );
}

import React, { useMemo, useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import ArticleCard from '../components/ArticleCard';
import Sidebar from '../components/Sidebar';
import TrendingTopics from '../components/TrendingTopics';
import TrendingClaims from '../components/TrendingClaims';
import { ArticleCardSkeleton, SidebarSkeleton } from '../components/Skeleton';
import SEOMeta from '../components/SEOMeta';
import { CONTENT_ENDPOINTS } from '../utils/api';
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

function SectionGrid({ section }) {
  if (!section || !section.articles || section.articles.length === 0) return null;
  const { category, articles } = section;

  return (
    <section className="home-section">
      <div className="home-section__header">
        <div>
          <span className="section-label">Desk</span>
          <h2 className="home-section__title">{category.name}</h2>
        </div>
        <Link to={`/category/${category.slug}`} className="home-section__view-all">View all</Link>
      </div>
      <div className="home-section__grid">
        {articles.slice(0, 4).map((article) => (
          <ArticleCard key={article.id} article={article} compact />
        ))}
      </div>
    </section>
  );
}

function VerificationWidget() {
  const [claim, setClaim] = useState('');

  const submitClaim = (event) => {
    event.preventDefault();
    const query = claim.trim();
    window.location.href = query ? `/verify?claim=${encodeURIComponent(query)}` : '/verify';
  };

  return (
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
          placeholder="Paste a headline, claim, post, or quote..."
          rows="4"
        />
        <button type="submit">Verify this claim</button>
      </form>
      <div className="verification-widget__signals">
        <span>Source trace</span>
        <span>Evidence score</span>
        <span>Verdict history</span>
      </div>
    </section>
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
            <span className="section-label">Claim briefing</span>
            <h2>Signals worth checking today</h2>
            <Link to="/verify">Open verifier</Link>
          </div>
          <TrendingClaims />
        </div>
      </section>

      <div className="home-layout">
        <div className="home-layout__main">
          {sectionKeys.map((key) => (
            <SectionGrid key={key} section={data.sections[key]} />
          ))}

          <section className="home-section home-section--topics">
            <div className="home-section__header">
              <div>
                <span className="section-label">Monitor</span>
                <h2 className="home-section__title">Trending claims</h2>
              </div>
              <Link to="/verify" className="home-section__view-all">Verify a claim</Link>
            </div>
            <TrendingTopics onTopicClick={handleTopicClick} />
          </section>
        </div>

        <aside className="home-layout__sidebar">
          <Sidebar categories={categories} recentPosts={data?.latest} />
        </aside>
      </div>
    </div>
  );
}

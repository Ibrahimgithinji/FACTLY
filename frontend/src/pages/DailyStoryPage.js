import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import SEOMeta from '../components/SEOMeta';
import { CONTENT_ENDPOINTS } from '../utils/api';
import './DailyStoryPage.css';

const formatDate = (value, options = {}) => {
  if (!value) return 'Date not available';
  return new Date(value).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric', ...options,
  });
};

export default function DailyStoryPage() {
  const { slug } = useParams();
  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();

    async function fetchStory() {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(CONTENT_ENDPOINTS.STORY(slug), { signal: controller.signal });
        if (!response.ok) throw new Error('This story is not available.');
        setStory(await response.json());
      } catch (fetchError) {
        if (fetchError.name !== 'AbortError') setError(fetchError.message || 'Could not load this story.');
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }

    fetchStory();
    return () => controller.abort();
  }, [slug]);

  if (loading) {
    return <main className="daily-story-page"><div className="daily-story-page__loading">Loading the story timeline…</div></main>;
  }

  if (error || !story) {
    return (
      <main className="daily-story-page">
        <div className="daily-story-page__error">
          <h1>Story unavailable</h1>
          <p>{error || 'This story could not be found.'}</p>
          <Link to="/">Return home</Link>
        </div>
      </main>
    );
  }

  return (
    <main className="daily-story-page">
      <SEOMeta title={story.title} description={story.summary} image={story.featured_image} type="article" />
      <header className="daily-story-page__header">
        <Link to="/" className="daily-story-page__back">← Back to today&apos;s news</Link>
        {story.category && <span className="daily-story-page__category">{story.category.name}</span>}
        <span className="daily-story-page__eyebrow">Factly daily story</span>
        <h1>{story.title}</h1>
        <p className="daily-story-page__summary">{story.summary}</p>
        {story.current_status && (
          <div className="daily-story-page__status">
            <strong>Current status</strong>
            <span>{story.current_status}</span>
          </div>
        )}
        {story.started_at && <p className="daily-story-page__started">Story begins {formatDate(story.started_at)}</p>}
      </header>

      <section id="timeline" className="daily-story-page__timeline" aria-labelledby="timeline-heading">
        <div className="daily-story-page__timeline-heading">
          <span>Start from the beginning</span>
          <h2 id="timeline-heading">The story so far</h2>
        </div>
        {story.events?.length ? (
          <ol className="story-timeline">
            {story.events.map((event) => (
              <li key={event.id} className="story-timeline__event">
                <div className="story-timeline__marker" aria-hidden="true">{event.position}</div>
                <article className="story-timeline__card">
                  <div className="story-timeline__meta">
                    <time dateTime={event.occurred_at}>{formatDate(event.occurred_at)}</time>
                    {event.is_verified && <span>Source checked</span>}
                  </div>
                  <h3>{event.title}</h3>
                  <p>{event.summary}</p>
                  <a href={event.source_url} target="_blank" rel="noopener noreferrer" className="story-timeline__source">
                    Read the source: {event.source_name} <span aria-hidden="true">↗</span>
                  </a>
                </article>
              </li>
            ))}
          </ol>
        ) : (
          <p className="daily-story-page__empty">The editorial timeline for this story is being prepared.</p>
        )}
      </section>
    </main>
  );
}

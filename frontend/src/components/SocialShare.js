import React from 'react';
import './SocialShare.css';

export default function SocialShare({ url, title }) {
  const encodedUrl = encodeURIComponent(url);
  const encodedTitle = encodeURIComponent(title);

  return (
    <div className="social-share">
      <span className="social-share__label">Share</span>
      <div className="social-share__buttons">
        <a
          href={`https://www.facebook.com/sharer.php?u=${encodedUrl}`}
          target="_blank" rel="noopener noreferrer"
          className="social-share__btn social-share__btn--facebook"
          aria-label="Share on Facebook"
        >f</a>
        <a
          href={`https://x.com/intent/post?text=${encodedTitle}&url=${encodedUrl}`}
          target="_blank" rel="noopener noreferrer"
          className="social-share__btn social-share__btn--x"
          aria-label="Share on X"
        >𝕏</a>
        <a
          href={`https://www.linkedin.com/shareArticle?mini=true&url=${encodedUrl}&title=${encodedTitle}`}
          target="_blank" rel="noopener noreferrer"
          className="social-share__btn social-share__btn--linkedin"
          aria-label="Share on LinkedIn"
        >in</a>
        <a
          href={`https://api.whatsapp.com/send?text=${encodedTitle}%20${encodedUrl}`}
          target="_blank" rel="noopener noreferrer"
          className="social-share__btn social-share__btn--whatsapp"
          aria-label="Share on WhatsApp"
        >WA</a>
        <a
          href={`https://telegram.me/share/url?url=${encodedUrl}&text=${encodedTitle}`}
          target="_blank" rel="noopener noreferrer"
          className="social-share__btn social-share__btn--telegram"
          aria-label="Share on Telegram"
        >TG</a>
        <a
          href={`mailto:?subject=${encodedTitle}&body=${encodedUrl}`}
          className="social-share__btn social-share__btn--email"
          aria-label="Share via Email"
        >✉</a>
      </div>
    </div>
  );
}

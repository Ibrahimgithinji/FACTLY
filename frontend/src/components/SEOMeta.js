import React from 'react';
import { Helmet } from 'react-helmet-async';

const SITE_NAME = 'FACTLY';
const DEFAULT_DESC = 'Verifying claims, tracking tech, keeping you informed. Fact-checking and tech news with a focus on truth in technology.';
const DEFAULT_IMAGE = '/logo192.png';
const SITE_URL = 'https://factly.tech';

export default function SEOMeta({
  title,
  description,
  image,
  url,
  type = 'website',
  publishedAt,
  author,
  tags,
}) {
  const pageTitle = title ? `${title} | ${SITE_NAME}` : `${SITE_NAME} — Truth in Tech`;
  const pageDesc = description || DEFAULT_DESC;
  const pageImage = image || DEFAULT_IMAGE;
  const pageUrl = url || SITE_URL;

  const jsonLd = type === 'article' && {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: title,
    description: pageDesc,
    image: pageImage,
    url: pageUrl,
    datePublished: publishedAt,
    author: author ? {
      '@type': 'Person',
      name: author,
    } : undefined,
    publisher: {
      '@type': 'Organization',
      name: SITE_NAME,
    },
  };

  return (
    <Helmet>
      <title>{pageTitle}</title>
      <meta name="description" content={pageDesc} />
      <meta name="viewport" content="width=device-width, initial-scale=1" />

      {/* Open Graph */}
      <meta property="og:title" content={pageTitle} />
      <meta property="og:description" content={pageDesc} />
      <meta property="og:image" content={pageImage} />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:type" content={type} />
      <meta property="og:site_name" content={SITE_NAME} />

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={pageTitle} />
      <meta name="twitter:description" content={pageDesc} />
      <meta name="twitter:image" content={pageImage} />

      {/* Canonical */}
      <link rel="canonical" href={pageUrl} />

      {/* JSON-LD */}
      {jsonLd && (
        <script type="application/ld+json">
          {JSON.stringify(jsonLd)}
        </script>
      )}
    </Helmet>
  );
}

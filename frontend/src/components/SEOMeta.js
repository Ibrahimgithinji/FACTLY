import React from 'react';
import { Helmet } from 'react-helmet-async';

const SITE_NAME = 'FACTLY';
const DEFAULT_DESC = 'Verify the credibility of news headlines and articles with FACTLY\'s advanced AI fact-checking. Get instant credibility scores, evidence analysis, and source verification.';
const DEFAULT_IMAGE = '/logo512.png';
const SITE_URL = 'https://factly.app';
const DEFAULT_KEYWORDS = 'fact checking, news verification, fake news detector, credibility score, AI fact checker, misinformation, disinformation, news analysis';

export default function SEOMeta({
  title,
  description,
  image,
  url,
  type = 'website',
  publishedAt,
  author,
  tags,
  keywords,
  noindex = false,
  breadcrumbs,
}) {
  const pageTitle = title ? `${title} | ${SITE_NAME}` : `${SITE_NAME} - AI-Powered Fact Checking & News Verification`;
  const pageDesc = description || DEFAULT_DESC;
  const pageImage = image || DEFAULT_IMAGE;
  const pageUrl = url || SITE_URL;
  const pageKeywords = keywords || DEFAULT_KEYWORDS;

  let jsonLd = null;

  if (type === 'article') {
    jsonLd = {
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: title,
      description: pageDesc,
      image: pageImage,
      url: pageUrl,
      datePublished: publishedAt,
      author: author ? { '@type': 'Person', name: author } : undefined,
      publisher: { '@type': 'Organization', name: SITE_NAME },
    };

    if (breadcrumbs) {
      jsonLd = [jsonLd, {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        itemListElement: breadcrumbs.map((crumb, i) => ({
          '@type': 'ListItem',
          position: i + 1,
          name: crumb.name,
          item: crumb.url,
        })),
      }];
    }
  } else if (type === 'about') {
    jsonLd = {
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: SITE_NAME,
      description: pageDesc,
      url: SITE_URL,
      logo: `${SITE_URL}/logo512.png`,
    };
  } else if (type === 'collection') {
    jsonLd = {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: pageTitle,
      description: pageDesc,
      url: pageUrl,
    };
  }

  return (
    <Helmet>
      <title>{pageTitle}</title>
      <meta name="description" content={pageDesc} />
      <meta name="keywords" content={pageKeywords} />
      <meta name="robots" content={noindex ? 'noindex, nofollow' : 'index, follow'} />

      {/* Open Graph */}
      <meta property="og:title" content={pageTitle} />
      <meta property="og:description" content={pageDesc} />
      <meta property="og:image" content={pageImage} />
      <meta property="og:image:width" content="512" />
      <meta property="og:image:height" content="512" />
      <meta property="og:image:type" content="image/png" />
      <meta property="og:url" content={pageUrl} />
      <meta property="og:type" content={type === 'article' ? 'article' : 'website'} />
      <meta property="og:site_name" content={SITE_NAME} />
      <meta property="og:locale" content="en_US" />

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
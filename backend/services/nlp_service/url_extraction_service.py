"""
URL Extraction Service

Extracts and processes content from URLs, supporting various content types
including news articles, social media posts, and general web pages.
"""

import logging
import requests
import socket
import ipaddress
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException
import re

logger = logging.getLogger(__name__)


def _is_private_hostname(hostname: str) -> bool:
    """Return True if the hostname resolves to a private or loopback IP.
    
    Returns True (block access) if:
    - Any resolved address is private/loopback/reserved
    - DNS resolution fails (conservative approach)
    """
    try:
        # Resolve all addresses for the hostname
        for res in socket.getaddrinfo(hostname, None):
            ip = res[4][0]
            try:
                addr = ipaddress.ip_address(ip)
                if addr.is_private or addr.is_loopback or addr.is_reserved:
                    return True  # Block this address
            except ValueError:
                # IP parsing failed; skip this result
                continue
        # All resolved addresses are public
        return False
    except (socket.gaierror, OSError):
        # DNS resolution or socket error: be conservative and block
        logger.warning(f"DNS resolution failed for {hostname}; blocking as potential SSRF")
        return True


class ExtractedContent:
    """Structured representation of extracted content."""

    def __init__(self, url: str, title: str = "", content: str = "",
                 author: str = "", publish_date: Optional[datetime] = None,
                 summary: str = "", keywords: List[str] = None,
                 language: str = "", source_type: str = "unknown",
                 metadata: Dict[str, Any] = None):
        self.url = url
        self.title = title
        self.content = content
        self.author = author
        self.publish_date = publish_date
        self.summary = summary
        self.keywords = keywords or []
        self.language = language
        self.source_type = source_type
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "summary": self.summary,
            "keywords": self.keywords,
            "language": self.language,
            "source_type": self.source_type,
            "metadata": self.metadata
        }


class URLExtractionService:
    """Service for extracting content from URLs."""

    def __init__(self, timeout: int = 30, user_agent: str = None):
        """
        Initialize the URL extraction service.

        Args:
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
        """
        self.timeout = timeout
        self.user_agent = user_agent or "FACTLY-Bot/1.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is well-formed and not pointing to private/internal hosts (SSRF protection)."""
        try:
            parsed = urlparse(url)
            if not (parsed.scheme and parsed.netloc):
                return False
            if parsed.scheme not in ('http', 'https'):
                return False
            hostname = parsed.hostname
            if not hostname:
                return False
            # Disallow localhost or direct IPs to private ranges
            if hostname in ('localhost', '127.0.0.1', '::1'):
                return False
            # If hostname is an IP address, check if it's private
            try:
                addr = ipaddress.ip_address(hostname)
                if addr.is_private or addr.is_loopback or addr.is_reserved:
                    return False
            except ValueError:
                # Not a direct IP; resolve DNS and check resolved addresses
                if _is_private_hostname(hostname):
                    return False
            return True
        except (ValueError, TypeError) as e:
            logger.warning(f"Error validating URL: {e}")
            return False

    def _detect_source_type(self, url: str) -> str:
        """Detect the type of content source."""
        domain = urlparse(url).netloc.lower()

        # Social media platforms
        if any(platform in domain for platform in ['twitter.com', 'facebook.com', 'instagram.com']):
            return 'social_media'

        # News websites
        if any(news in domain for news in ['news', 'cnn.com', 'bbc.com', 'nytimes.com', 'reuters.com']):
            return 'news'

        # Blog platforms
        if any(blog in domain for blog in ['blogspot.com', 'wordpress.com', 'medium.com']):
            return 'blog'

        # Video platforms
        if any(video in domain for video in ['youtube.com', 'vimeo.com', 'tiktok.com']):
            return 'video'

        return 'website'

    def _extract_with_newspaper(self, url: str) -> Optional[ExtractedContent]:
        """Extract content using newspaper3k library."""
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()

            return ExtractedContent(
                url=url,
                title=article.title or "",
                content=article.text or "",
                author=article.authors[0] if article.authors else "",
                publish_date=article.publish_date,
                summary=article.summary or "",
                keywords=article.keywords or [],
                language=article.meta_lang or "",
                source_type=self._detect_source_type(url),
                metadata={
                    'top_image': article.top_image,
                    'movies': article.movies,
                    'meta_description': article.meta_description,
                    'meta_keywords': article.meta_keywords
                }
            )
        except ArticleException as e:
            logger.warning(f"Newspaper extraction failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in newspaper extraction: {e}")
            return None

    def _extract_with_beautifulsoup(self, url: str, html: str) -> Optional[ExtractedContent]:
        """Fallback extraction using BeautifulSoup."""
        try:
            soup = BeautifulSoup(html, 'lxml')

            # Extract title
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()

            # Try to find main content
            content_selectors = [
                'article', '.article-content', '.post-content', '.entry-content',
                '.content', 'main', '#main', '.main-content'
            ]

            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator=' ', strip=True)
                    break

            if not content:
                # Fallback to body text
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)

            # Extract metadata
            author = ""
            author_meta = soup.find('meta', attrs={'name': 'author'}) or \
                         soup.find('meta', attrs={'property': 'article:author'})
            if author_meta:
                author = author_meta.get('content', '')

            publish_date = None
            date_meta = soup.find('meta', attrs={'property': 'article:published_time'}) or \
                       soup.find('meta', attrs={'name': 'publishdate'})
            if date_meta:
                date_str = date_meta.get('content', '')
                try:
                    publish_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    pass

            return ExtractedContent(
                url=url,
                title=title,
                content=content,
                author=author,
                publish_date=publish_date,
                source_type=self._detect_source_type(url),
                metadata={
                    'extraction_method': 'beautifulsoup_fallback'
                }
            )
        except Exception as e:
            logger.error(f"BeautifulSoup extraction failed: {e}")
            return None

    def extract_content(self, url: str) -> ExtractedContent:
        """
        Extract content from a URL.

        Args:
            url: URL to extract content from

        Returns:
            ExtractedContent object with structured data

        Raises:
            ValueError: If URL is invalid
            requests.RequestException: If request fails
        """
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")

        logger.info(f"Extracting content from: {url}")

        try:
            # First try newspaper3k for structured content
            extracted = self._extract_with_newspaper(url)
            if extracted and extracted.content:
                logger.info(f"Successfully extracted content using newspaper3k")
                return extracted

            # Fallback to requests + BeautifulSoup
            logger.info("Falling back to BeautifulSoup extraction")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            extracted = self._extract_with_beautifulsoup(url, response.text)
            if extracted:
                logger.info("Successfully extracted content using BeautifulSoup")
                return extracted

            # If all else fails, return minimal content
            logger.warning(f"Could not extract meaningful content from {url}")
            return ExtractedContent(
                url=url,
                source_type=self._detect_source_type(url),
                metadata={'extraction_status': 'failed'}
            )

        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting {url}: {e}")
            raise
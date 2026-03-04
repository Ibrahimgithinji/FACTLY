"""
Rate Limiter for API Calls

Implements rate limiting to prevent API quota exhaustion and ensure fair usage.
Supports high-volume requests with concurrent call handling.
"""

import time
import logging
import os
from typing import Callable, Any, Dict
from threading import Lock
from functools import wraps
from collections import deque

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for external API calls with high-volume support."""

    def __init__(self):
        """Initialize rate limiter with configurable settings."""
        # Google Fact Check API: 100 requests per 100 seconds per user
        self.google_last_call = 0
        self.google_min_interval = float(os.getenv('GOOGLE_API_INTERVAL', '1.0'))  # 1 second between calls
        
        # NewsLdr API: Adjust based on actual limits
        self.newsldr_last_call = 0
        self.newsldr_min_interval = float(os.getenv('NEWSLDR_API_INTERVAL', '0.5'))  # 0.5 seconds between calls
        
        # NewsAPI limits
        self.newsapi_last_call = 0
        self.newsapi_min_interval = float(os.getenv('NEWSAPI_INTERVAL', '0.5'))
        
        # Concurrent request tracking
        self._locks = {
            'google': Lock(),
            'newsldr': Lock(),
            'newsapi': Lock(),
        }
        
        # Request tracking for sliding window rate limiting
        self._request_history: Dict[str, deque] = {
            'google': deque(maxlen=100),
            'newsldr': deque(maxlen=100),
            'newsapi': deque(maxlen=100),
        }
        
        # Configure based on environment
        self.max_requests_per_minute = int(os.getenv('MAX_API_REQUESTS_PER_MINUTE', '60'))

    def _wait_if_needed(self, last_call_time: float, min_interval: float) -> float:
        """Wait if needed to respect rate limits."""
        current_time = time.time()
        elapsed = current_time - last_call_time

        if elapsed < min_interval:
            sleep_time = min_interval - elapsed
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
            current_time = time.time()

        return current_time

    def _track_request(self, api_name: str) -> bool:
        """
        Track request using sliding window algorithm.
        Returns True if request is allowed, False if rate limit exceeded.
        """
        now = time.time()
        window_start = now - 60  # 1 minute window
        
        # Clean old entries
        history = self._request_history.get(api_name, deque())
        while history and history[0] < window_start:
            history.popleft()
        
        # Check if we can make more requests
        if len(history) >= self.max_requests_per_minute:
            logger.warning(f"Rate limit exceeded for {api_name}: {len(history)} requests in last minute")
            return False
        
        # Add current request
        history.append(now)
        return True

    def google_api_call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a Google API call with rate limiting.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result from the function call
        """
        with self._locks['google']:
            # Check sliding window rate limit
            if not self._track_request('google'):
                logger.warning("Google API rate limit reached, waiting...")
                time.sleep(1)  # Brief wait before retry
            
            self.google_last_call = self._wait_if_needed(
                self.google_last_call,
                self.google_min_interval
            )

            try:
                result = func(*args, **kwargs)
                self.google_last_call = time.time()
                return result
            except Exception as e:
                logger.error(f"Google API call failed: {e}")
                raise

    def newsldr_api_call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a NewsLdr API call with rate limiting.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result from the function call
        """
        with self._locks['newsldr']:
            # Check sliding window rate limit
            if not self._track_request('newsldr'):
                logger.warning("NewsLdr API rate limit reached, waiting...")
                time.sleep(0.5)
            
            self.newsldr_last_call = self._wait_if_needed(
                self.newsldr_last_call,
                self.newsldr_min_interval
            )

            try:
                result = func(*args, **kwargs)
                self.newsldr_last_call = time.time()
                return result
            except Exception as e:
                logger.error(f"NewsLdr API call failed: {e}")
                raise
    
    def newsapi_call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a NewsAPI call with rate limiting.
        
        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from the function call
        """
        with self._locks['newsapi']:
            if not self._track_request('newsapi'):
                logger.warning("NewsAPI rate limit reached, waiting...")
                time.sleep(1)
            
            self.newsapi_last_call = self._wait_if_needed(
                self.newsapi_last_call,
                self.newsapi_min_interval
            )
            
            try:
                result = func(*args, **kwargs)
                self.newsapi_last_call = time.time()
                return result
            except Exception as e:
                logger.error(f"NewsAPI call failed: {e}")
                raise

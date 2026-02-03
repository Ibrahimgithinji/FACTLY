"""
Rate Limiter for API Calls

Implements rate limiting to prevent API quota exhaustion and ensure fair usage.
"""

import time
import logging
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for external API calls."""

    def __init__(self):
        """Initialize rate limiter with default settings."""
        # Google Fact Check API: 100 requests per 100 seconds per user
        self.google_last_call = 0
        self.google_min_interval = 1.0  # 1 second between calls

        # NewsLdr API: Adjust based on actual limits
        self.newsldr_last_call = 0
        self.newsldr_min_interval = 0.5  # 0.5 seconds between calls

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

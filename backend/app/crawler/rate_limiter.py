import time
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Applies a delay between requests to avoid overloading the target site."""

    def __init__(self, delay_seconds: float = 2.0):
        self.delay_seconds = delay_seconds

    def wait(self):
        """Wait for the configured delay before the next request."""
        logger.info(f"Rate limiting: waiting {self.delay_seconds} seconds")
        time.sleep(self.delay_seconds)

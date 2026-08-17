import time
import logging

import httpx

from app.crawler.rate_limiter import RateLimiter
from app.crawler.robots import can_crawl
from app.crawler.url_validator import is_safe_url


logger = logging.getLogger(__name__)


class CrawlerEngine:
    """Downloads web pages while respecting responsible crawling rules."""

    def __init__(
        self,
        user_agent: str = "osint-crawler",
        request_delay: float = 2.0,
    ):
        self.user_agent = user_agent
        self.rate_limiter = RateLimiter(request_delay)
        self.pages_visited = 0

    def fetch_page(self, url: str, max_retries: int = 3) -> str | None:
        """Download a page's HTML, retrying on temporary failures."""

        # SSRF protection: block localhost, private IPs, unsafe schemes
        if not is_safe_url(url):
            logger.warning("Unsafe URL blocked (SSRF protection): %s", url)
            return None

        if not can_crawl(url, self.user_agent):
            logger.warning("robots.txt does not allow crawling: %s", url)
            return None

        headers = {
            "User-Agent": self.user_agent,
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
        }

        for attempt in range(1, max_retries + 1):
            self.rate_limiter.wait()

            try:
                response = httpx.get(
                    url,
                    headers=headers,
                    timeout=10,
                    follow_redirects=True,
                )
                response.raise_for_status()
                return response.text

            except httpx.HTTPStatusError as error:
                status = error.response.status_code
                # Retry on temporary server errors (5xx) or rate limiting (429)
                if status in (429, 500, 502, 503, 504) and attempt < max_retries:
                    wait_time = attempt * 3
                    logger.warning(
                        "Temporary error %s for %s. Retry %s/%s after %ss",
                        status, url, attempt, max_retries, wait_time,
                    )
                    time.sleep(wait_time)
                    continue
                logger.error("HTTP error %s while requesting %s", status, url)
                return None

            except httpx.TimeoutException:
                if attempt < max_retries:
                    logger.warning("Timeout for %s. Retry %s/%s", url, attempt, max_retries)
                    continue
                logger.error("Request timed out: %s", url)
                return None

            except httpx.RequestError as error:
                if attempt < max_retries:
                    logger.warning("Connection error for %s. Retry %s/%s", url, attempt, max_retries)
                    continue
                logger.error("Request failed for %s: %s", url, error)
                return None

        return None

    def crawl(self, start_url, parser, max_pages: int = 5) -> list[dict]:
        """Crawl starting from start_url using the given parser."""
        visited = set()
        all_results = []
        url = start_url
        page_count = 0

        while url and page_count < max_pages:
            if url in visited:
                logger.info("Already visited: %s", url)
                break
            visited.add(url)

            logger.info("Crawling page %s: %s", page_count + 1, url)

            html = self.fetch_page(url)
            if html is None:
                break

            records = parser.parse(html, url)
            all_results.extend(records)
            logger.info("Extracted %s records", len(records))

            page_count += 1
            self.pages_visited = page_count

            url = parser.get_next_page(html, url)

        logger.info(
            "Crawl finished. Pages: %s, Records: %s",
            page_count,
            len(all_results),
        )
        return all_results

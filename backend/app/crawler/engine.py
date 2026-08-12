import logging

import httpx

from app.crawler.rate_limiter import RateLimiter
from app.crawler.robots import can_crawl


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

    def fetch_page(self, url: str) -> str | None:
        """Download and return the HTML content of a permitted page."""

        if not can_crawl(url, self.user_agent):
            logger.warning("robots.txt does not allow crawling: %s", url)
            return None

        self.rate_limiter.wait()

        headers = {
            "User-Agent": self.user_agent,
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
        }

        try:
            response = httpx.get(
                url,
                headers=headers,
                timeout=10,
                follow_redirects=True,
            )

            response.raise_for_status()
            return response.text

        except httpx.TimeoutException:
            logger.error("Request timed out: %s", url)
            return None

        except httpx.HTTPStatusError as error:
            logger.error(
                "HTTP error %s while requesting %s",
                error.response.status_code,
                url,
            )
            return None

        except httpx.RequestError as error:
            logger.error("Request failed for %s: %s", url, error)
            return None
        
    def crawl(self, start_url, parser, max_pages: int = 5) -> list[dict]:
        """Crawl starting from start_url using the given parser."""
        visited = set()
        all_results = []
        url = start_url
        page_count = 0

        while url and page_count < max_pages:
            # Avoid visiting the same URL twice
            if url in visited:
                logger.info("Already visited: %s", url)
                break
            visited.add(url)

            logger.info("Crawling page %s: %s", page_count + 1, url)

            # Download the page (robots + rate limit + fetch)
            html = self.fetch_page(url)
            if html is None:
                break

            # Parse advisories from the page
            records = parser.parse(html, url)
            all_results.extend(records)
            logger.info("Extracted %s records", len(records))

            page_count += 1
            self.pages_visited = page_count

            # Find the next page
            url = parser.get_next_page(html, url)

        logger.info(
            "Crawl finished. Pages: %s, Records: %s",
            page_count,
            len(all_results),
        )
        return all_results
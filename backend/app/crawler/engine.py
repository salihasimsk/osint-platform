import logging
import time

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

        # Indicates that the target actively denied or blocked crawling.
        self.blocked = False
        self.block_reason: str | None = None

    def fetch_page(
        self,
        url: str,
        max_retries: int = 3,
    ) -> str | None:
        """Download a page while respecting safety and retry rules."""

        # SSRF protection:
        # block localhost, private IPs, unsafe schemes, etc.
        if not is_safe_url(url):
            logger.warning(
                "Unsafe URL blocked (SSRF protection): %s",
                url,
            )
            return None

        # Respect robots.txt before making the actual page request.
        if not can_crawl(url, self.user_agent):
            logger.warning(
                "robots.txt does not allow crawling: %s",
                url,
            )
            return None

        headers = {
            "User-Agent": self.user_agent,
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
        }

        for attempt in range(
            1,
            max_retries + 1,
        ):
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

                # Authentication or access-control response:
                # do not retry or attempt to bypass it.
                if status in (401, 403):
                    self.blocked = True
                    self.block_reason = (
                        f"Access denied with HTTP {status}"
                    )

                    logger.error(
                        "Access denied for %s with HTTP %s. "
                        "Crawler will stop.",
                        url,
                        status,
                    )

                    return None

                # Rate limiting can be temporary.
                # Retry conservatively, then stop if blocking continues.
                if status == 429:
                    if attempt < max_retries:
                        wait_time = attempt * 3

                        logger.warning(
                            "Rate limited (HTTP 429) for %s. "
                            "Retry %s/%s after %ss",
                            url,
                            attempt,
                            max_retries,
                            wait_time,
                        )

                        time.sleep(wait_time)
                        continue

                    self.blocked = True
                    self.block_reason = (
                        "Repeated rate limiting with HTTP 429"
                    )

                    logger.error(
                        "Repeated HTTP 429 responses for %s. "
                        "Crawler will stop.",
                        url,
                    )

                    return None

                # Temporary server failures.
                if status in (
                    500,
                    502,
                    503,
                    504,
                ):
                    if attempt < max_retries:
                        wait_time = attempt * 3

                        logger.warning(
                            "Temporary HTTP %s error for %s. "
                            "Retry %s/%s after %ss",
                            status,
                            url,
                            attempt,
                            max_retries,
                            wait_time,
                        )

                        time.sleep(wait_time)
                        continue

                logger.error(
                    "HTTP error %s while requesting %s",
                    status,
                    url,
                )

                return None

            except httpx.TimeoutException:
                if attempt < max_retries:
                    logger.warning(
                        "Timeout for %s. Retry %s/%s",
                        url,
                        attempt,
                        max_retries,
                    )
                    continue

                logger.error(
                    "Request timed out: %s",
                    url,
                )

                return None

            except httpx.RequestError as error:
                if attempt < max_retries:
                    logger.warning(
                        "Connection error for %s. Retry %s/%s",
                        url,
                        attempt,
                        max_retries,
                    )
                    continue

                logger.error(
                    "Request failed for %s: %s",
                    url,
                    error,
                )

                return None

        return None

    def crawl(
        self,
        start_url,
        parser,
        max_pages: int = 5,
    ) -> list[dict]:
        """Crawl starting from start_url using the given parser."""

        visited = set()
        all_results = []

        url = start_url
        page_count = 0

        while (
            url
            and page_count < max_pages
        ):
            if url in visited:
                logger.info(
                    "Already visited: %s",
                    url,
                )
                break

            visited.add(url)

            logger.info(
                "Crawling page %s: %s",
                page_count + 1,
                url,
            )

            html = self.fetch_page(url)

            if html is None:
                if self.blocked:
                    logger.error(
                        "Crawl stopped because blocking "
                        "or access denial was detected: %s",
                        self.block_reason,
                    )
                else:
                    logger.warning(
                        "Page could not be fetched. "
                        "Crawl will stop: %s",
                        url,
                    )

                break

            records = parser.parse(
                html,
                url,
            )

            all_results.extend(records)

            logger.info(
                "Extracted %s records",
                len(records),
            )

            page_count += 1
            self.pages_visited = page_count

            url = parser.get_next_page(
                html,
                url,
            )

        logger.info(
            "Crawl finished. Pages: %s, Records: %s",
            page_count,
            len(all_results),
        )

        return all_results
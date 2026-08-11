import logging
import httpx
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def can_crawl(url: str, user_agent: str = "osint-crawler") -> bool:
    """Check whether the given URL is allowed to be crawled according to robots.txt."""
    try:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{base}/robots.txt"

        # Download robots.txt ourselves with a timeout
        response = httpx.get(robots_url, timeout=10)
        response.raise_for_status()

        # Feed the downloaded content into the parser
        rp = RobotFileParser()
        rp.parse(response.text.splitlines())

        return rp.can_fetch(user_agent, url)

    except Exception as e:
        logger.warning(f"Could not read robots.txt ({url}): {e}")
        return False
    
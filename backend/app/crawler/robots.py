import logging
import httpx
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; osint-crawler/1.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def can_crawl(url: str, user_agent: str = "osint-crawler") -> bool:
    """Check whether the given URL is allowed by robots.txt."""
    try:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{base}/robots.txt"

        response = httpx.get(
            robots_url,
            headers=HEADERS,
            timeout=10,
            follow_redirects=True,   # redirect'i takip et (Ubuntu sorunu)
        )

        # robots.txt yoksa (404), tarama serbest kabul edilir
        if response.status_code == 404:
            logger.info(f"No robots.txt found for {base}, assuming allowed")
            return True

        # robots.txt'ye erişilemiyorsa (403 gibi), güvenli tarafta kal
        if response.status_code != 200:
            logger.warning(f"robots.txt returned {response.status_code} for {base}")
            return False

        rp = RobotFileParser()
        rp.parse(response.text.splitlines())
        return rp.can_fetch(user_agent, url)

    except Exception as e:
        logger.warning(f"Could not read robots.txt ({url}): {e}")
        return False
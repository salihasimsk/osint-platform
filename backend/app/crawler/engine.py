import httpx

from app.crawler.robots import RobotsChecker
from app.crawler.rate_limiter import RateLimiter


class CrawlerEngine:
    def __init__(
        self,
        user_agent="OSINT-Platform-Crawler/1.0",
        request_delay_seconds=2
    ):
        self.user_agent = user_agent
        self.robots_checker = RobotsChecker(user_agent)
        self.rate_limiter = RateLimiter(request_delay_seconds)

    def fetch_page(self, url):

        if not self.robots_checker.can_fetch(url):
            print(f"robots.txt izin vermiyor: {url}")
            return None

        self.rate_limiter.wait()

        headers = {
            "User-Agent": self.user_agent
        }

        try:
            response = httpx.get(
                url,
                headers=headers,
                timeout=10
            )

            response.raise_for_status()

            return response.text

        except httpx.TimeoutException:
            print(f"Timeout: {url}")
            return None

        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
            return None

        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


class RobotsChecker:
    def __init__(self, user_agent="OSINT-Platform-Crawler/1.0"):
        self.user_agent = user_agent

    def can_fetch(self, url):
        parsed_url = urlparse(url)

        robots_url = (
            f"{parsed_url.scheme}://"
            f"{parsed_url.netloc}/robots.txt"
        )

        rp = RobotFileParser()
        rp.set_url(robots_url)

        try:
            rp.read()
        except Exception:
            return False

        return rp.can_fetch(
            self.user_agent,
            url
        )
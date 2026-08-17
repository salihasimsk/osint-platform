from urllib.parse import urljoin
from bs4 import BeautifulSoup
from app.crawler.parsers.base_parser import BaseParser
from datetime import datetime

class UbuntuParser(BaseParser):
    """Parser for Ubuntu Security Notices."""

    def parse(self, html: str, source_url: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        notices_list = soup.select_one("#notices-list")

        if notices_list is None:
            return results

        notices = notices_list.find_all(
            "section",
            class_="p-section--shallow",
            recursive=False,
        )

        for notice in notices:
            title_link = notice.select_one(
                "h3 a[href^='/security/notices/']"
            )

            if title_link is None:
                continue

            title = title_link.get_text(strip=True)
            detail_url = urljoin(
                source_url,
                title_link.get("href", ""),
            )

            date_tag = notice.select_one(
                "div.col-6 > p.u-text--muted"
            )

            publication_date = None

            if date_tag:
                date_text = date_tag.get_text(strip=True)

            try:
                publication_date = datetime.strptime(
                    date_text,
                    "%d %B %Y",
                )
            except ValueError:
                publication_date = None

            summary_tag = notice.select_one(
                "div.col-6 > "
                "p.u-no-margin--bottom:not(.u-text--muted)"
            )

            summary = (
                summary_tag.get_text(" ", strip=True)
                if summary_tag
                else None
            )

            cve_links = notice.select(
                "a[href^='/security/CVE-']"
            )

            cves = [
                link.get_text(strip=True)
                for link in cve_links
            ]

            results.append({
                "title": title,
                "url": detail_url,
                "publication_date": publication_date,
                "summary": summary,
                "cve": cves[0] if cves else None,
                "organization": "Ubuntu",
                "source_domain": "ubuntu.com",
            })

        return results

    def get_next_page(
        self,
        html: str,
        current_url: str,
    ) -> str | None:
        soup = BeautifulSoup(html, "html.parser")

        next_link = soup.select_one(
            "a.p-pagination__link--next"
        )

        if next_link is None:
            return None

        href = next_link.get("href")

        if not href:
            return None

        return urljoin(current_url, href)

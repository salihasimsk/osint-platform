from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime
from app.crawler.parsers.base_parser import BaseParser


class CertParser(BaseParser):
    """Parser for CERT/CC Vulnerability Notes Database."""

    BASE_URL = "https://www.kb.cert.org"

    def parse(self, html: str, source_url: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Each vulnerability note is a table row
        rows = soup.select("table tbody tr")

        for row in rows:
            cells = row.find_all("td")

            # Skip rows that don't have enough cells
            if len(cells) < 6:
                continue

            # The title and link are in the last cell (inside an <a>)
            link_tag = cells[5].find("a")
            if link_tag is None:
                continue

            title = link_tag.get_text(strip=True)
            detail_url = urljoin(self.BASE_URL, link_tag.get("href", ""))

            # The VU# id is in the 4th cell (index 3)
            vu_id = cells[3].get_text(strip=True)

            publication_date_text = cells[1].get_text(strip=True)
            publication_date = None

            if publication_date_text:
                try:
                    publication_date = datetime.strptime(
                    publication_date_text,
                    "%Y-%m-%d",
                )
                except ValueError:
                    publication_date = None

            results.append({
                "title": f"{vu_id}: {title}" if vu_id else title,
                "url": detail_url,
                "publication_date": publication_date,
                "summary": None,
                "cve": None,
                "organization": "CERT/CC",
                "source_domain": "kb.cert.org",
            })

        return results

    def get_next_page(self, html: str, current_url: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        # Look for a "next" pagination link
        next_link = soup.select_one("a[rel='next']")
        if next_link is None:
            return None
        href = next_link.get("href")
        if not href:
            return None
        return urljoin(current_url, href)

    def parse_detail(self, html: str) -> dict:
        """Extract extra fields (CVE) from a detail page."""
        soup = BeautifulSoup(html, "html.parser")

        # CVEs appear as links to cve.org / cve.mitre.org
        cve_links = soup.find_all("a", href=lambda h: h and "CVE-" in h)

        cves = []
        for link in cve_links:
            text = link.get_text(strip=True)
            # Only keep things that look like a CVE id
            if text.startswith("CVE-") and text not in cves:
                cves.append(text)

        # Join multiple CVEs with commas
        cve = ", ".join(cves) if cves else None

        return {"cve": cve}

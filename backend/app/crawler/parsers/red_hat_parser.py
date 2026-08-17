import json
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from app.crawler.parsers.base_parser import BaseParser


class RedHatParser(BaseParser):
    """Parser for the Red Hat Security Data API."""

    def parse(self, html: str, source_url: str) -> list[dict]:
        results = []

        data = json.loads(html)

        # Red Hat API response should be a JSON list.
        if not isinstance(data, list):
            return results

        for vulnerability in data:
            cve = vulnerability.get("CVE")
            description = vulnerability.get("bugzilla_description")
            severity = vulnerability.get("severity")
            publication_date_text = vulnerability.get("public_date")

            publication_date = None

            if publication_date_text:
                try:
                    publication_date = datetime.fromisoformat(
                        publication_date_text.replace("Z", "")
                    )
                except ValueError:
                    publication_date = None

            if not cve:
                continue

            if description:
                description = description.strip()

            if severity:
                severity = severity.strip().lower()

            product = None
            affected_packages = vulnerability.get(
                "affected_packages",
                [],
            )

            for package in affected_packages:
                if isinstance(package, str) and package.strip():
                    product = package.strip()
                    break
            if (
                product is None
                and description
                and ":" in description
            ):
                product_candidate = description.split(
                    ":",
                    1,
                )[0].strip()

                if product_candidate:
                    product = product_candidate

            detail_url = (
                "https://access.redhat.com/security/cve/"
                f"{cve.lower()}"
            )

            title = (
                f"{cve}: {description}"
                if description
                else cve
            )

            results.append({
                "title": title,
                "url": detail_url,
                "publication_date": publication_date,
                "summary": description,
                "cve": cve,
                "product": product,
                "severity": severity,
                "organization": "Red Hat",
                "source_domain": "access.redhat.com",
            })
        return results

    def get_next_page(
        self,
        html: str,
        current_url: str,
    ) -> str | None:
        data = json.loads(html)

        if not isinstance(data, list) or not data:
            return None

        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)

        current_page = int(
            query_params.get("page", ["1"])[0]
        )
        per_page = int(
            query_params.get("per_page", ["1000"])[0]
        )

        if len(data) < per_page:
            return None

        query_params["page"] = [str(current_page + 1)]

        new_query = urlencode(
            query_params,
            doseq=True,
        )

        return urlunparse(
            parsed_url._replace(query=new_query)
        )

import json
from datetime import datetime
from app.crawler.parsers.base_parser import BaseParser



class CisaKevParser(BaseParser):
    def parse(self,html: str, source_url: str) -> list[dict]:
        results = []

        data = json.loads(html) #JSON metnini Python sözlüğüne dönüştürür
        vulnerabilities = data.get("vulnerabilities", []) #cisa kayıt listesini alır

        for vulnerability in vulnerabilities:
            cve = vulnerability.get("cveID")
            title = vulnerability.get("vulnerabilityName")
            product_text = vulnerability.get("product")
            product = product_text.strip() if product_text else None
            summary = vulnerability.get("shortDescription")
            publication_date_text = vulnerability.get("dateAdded")

            publication_date = None  #sqlite a uygun

            if publication_date_text:
                try:
                    publication_date = datetime.strptime(
                    publication_date_text,
                    "%Y-%m-%d",
                )
                except ValueError:
                    publication_date = None

            detail_url = (
                "https://www.cisa.gov/"
                "known-exploited-vulnerabilities-catalog"
                f"?search_api_fulltext={cve}"
            )

            results.append({
                "title": title,
                "url": detail_url,
                "publication_date": publication_date,
                "summary": summary,
                "cve": cve,
                "product": product,
                "severity": None,
                "organization": "CISA",
                "source_domain": "cisa.gov",
            })

            def get_next_page(
                self,
                html: str,
                current_url: str,
            ) -> str | None:
                return None




        return results

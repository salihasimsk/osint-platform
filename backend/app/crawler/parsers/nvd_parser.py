import json
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from app.crawler.parsers.base_parser import BaseParser

class NvdParser(BaseParser):
    def parse(self,html:str,source_url:str) -> list[dict]:
        results = []

        data = json.loads(html)
        vulnerabilities = data.get("vulnerabilities",[]) #json metnini python sözlüğüne dönüştürür

        for vulnerability in vulnerabilities:
            cve_data = vulnerability.get("cve",{})
            cve_id = cve_data.get("id")

            if not cve_id:
                continue

            descriptions = cve_data.get("descriptions",[])
            summary = None

            for description in descriptions:
                if description.get("lang") == "en":
                    summary = description.get("value")
                    break

            publication_date_text = cve_data.get("published")
            publication_date = None

            if publication_date_text:
                try:
                    publication_date = datetime.fromisoformat(
                        publication_date_text.replace("Z","")
                    )
                except ValueError:
                    publication_date=None


            metrics = cve_data.get("metrics",{})
            severity = None
            metric_names =(
                "cvssMetricV40",
                "cvssMetricV31",
                "cvssMetricV30",
                "cvssMetricV2",
            )

            for metric_name in metric_names:
                metric_list = metrics.get(metric_name,[])

                if not metric_list:
                    continue

                metric = metric_list[0]
                cvss_data = metric.get("cvssData",{})

                severity = (
                    cvss_data.get("baseSeverity")
                    or metric.get("baseSeverity")
                )

                if severity:
                    severity = severity.lower()
                    break

            product = None
            affected_groups = cve_data.get("affected",[])

            for affected_group in affected_groups:
                affected_data = affected_group.get(
                    "affectedData",
                    [],
                )

                for affected_item in affected_data:
                    product_value = affected_item.get("product")

                    if(
                        product_value
                        and product_value.lower() != "n/a"
                    ):
                        product = product_value.strip()
                        break
                if product:
                    break

            title = cve_id
            detail_url = (
                "https://nvd.nist.gov/vuln/detail/"
                f"{cve_id}"
            )

            results.append({
                "title":title,
                "url": detail_url,
                "publication_date": publication_date,
                "summary" : summary,
                "cve" : cve_id,
                "product" : product,
                "severity":severity,
                "organization" : "NVD",
                "source_domain":"nvd.nist.gov",
            })


        return results


    def get_next_page(
        self,
        html:str,
        current_url : str,
    ) -> str | None:
        data = json.loads(html)

        start_index = data.get("startIndex",0)
        results_per_page = data.get("resultsPerPage",0)
        total_results = data.get("totalResults",0)

        next_index = start_index + results_per_page

        if results_per_page <= 0 or next_index >= total_results:
            return None

        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)

        query_params["startIndex"] = [str(next_index)]

        new_query = urlencode(
            query_params,
            doseq = True,
        )

        return urlunparse(
            parsed_url._replace(query=new_query)
        )

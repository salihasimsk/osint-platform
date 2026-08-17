import json
from datetime import datetime

from app.crawler.parsers.nvd_parser import NvdParser

SAMPLE_DATA = {
    "resultsPerPage": 1,
    "startIndex": 0,
    "totalResults": 2,
    "vulnerabilities": [
        {
            "cve": {
                "id": "CVE-2026-1234",
                "published": "2026-08-15T10:30:00.000",
                "descriptions": [
                    {
                        "lang": "en",
                        "value": "Example vulnerability description.",
                    },
                    {
                        "lang": "es",
                        "value": "Descripcion de vulnerabilidad.",
                    },
                ],
                "affected": [
                    {
                        "affectedData": [
                            {
                                "product": "Example Product",
                            }
                        ]
                    }
                ],
                "metrics": {
                    "cvssMetricV31": [
                        {
                            "cvssData": {
                                "baseSeverity": "HIGH",
                            }
                        }
                    ]
                },
            }
        }
    ],
}

def test_parse():
    parser = NvdParser()

    results = parser.parse(
        json.dumps(SAMPLE_DATA),
        "https://services.nvd.nist.gov/rest/json/cves/2.0",
    )

    assert len(results) == 1

    advisory = results[0]

    assert advisory["title"] == "CVE-2026-1234"
    assert advisory["cve"] == "CVE-2026-1234"
    assert advisory["summary"] == (
        "Example vulnerability description."
    )
    assert advisory["publication_date"] == datetime(
        2026,
        8,
        15,
        10,
        30,
    )
    assert advisory["product"] == "Example Product"
    assert advisory["severity"] == "high"
    assert advisory["organization"] == "NVD"
    assert advisory["source_domain"] == "nvd.nist.gov"

def test_get_next_page():
      parser = NvdParser()

      next_page = parser.get_next_page(
          json.dumps(SAMPLE_DATA),
          (
              "https://services.nvd.nist.gov/"
              "rest/json/cves/2.0?resultsPerPage=1"
          ),
      )

      assert next_page == (
          "https://services.nvd.nist.gov/"
          "rest/json/cves/2.0?resultsPerPage=1&startIndex=1"
      )

def test_get_next_page_returns_none_on_last_page():
     parser = NvdParser()

     last_page_data = {
         **SAMPLE_DATA,
         "startIndex": 1,
     }

     next_page = parser.get_next_page(
         json.dumps(last_page_data),
         (
             "https://services.nvd.nist.gov/"
             "rest/json/cves/2.0"
             "?resultsPerPage=1&startIndex=1"
         ),
     )

     assert next_page is None

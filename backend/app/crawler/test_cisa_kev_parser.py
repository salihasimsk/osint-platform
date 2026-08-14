import json
from datetime import datetime

from app.crawler.parsers.cisa_kev_parser import CisaKevParser


def test_parse():
    sample_data = {
        "vulnerabilities": [
            {
                "cveID": "CVE-2026-12345",
                "vendorProject": "Example Vendor",
                "product": "Example Product",
                "vulnerabilityName": "Example Product Vulnerability",
                "dateAdded": "2026-08-11",
                "shortDescription": (
                    "Example vulnerability description."
                ),
            }
        ]
    }

    parser = CisaKevParser()

    results = parser.parse(
        json.dumps(sample_data),
        "https://example.com/catalog.json",
    )

    assert len(results) == 1
    assert results[0]["title"] == "Example Product Vulnerability"
    assert results[0]["cve"] == "CVE-2026-12345"
    assert results[0]["product"] == "Example Product"
    assert results[0]["summary"] == (
        "Example vulnerability description."
    )
    assert results[0]["organization"] == "CISA"
    assert results[0]["source_domain"] == "cisa.gov"
    assert results[0]["publication_date"] == datetime(
        2026,
        8,
        11,
    )


def test_get_next_page():
    parser = CisaKevParser()

    result = parser.get_next_page(
        "{}",
        "https://example.com/catalog.json",
    )

    assert result is None
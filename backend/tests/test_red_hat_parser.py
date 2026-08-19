import json
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from app.crawler.parsers.red_hat_parser import RedHatParser


SAMPLE_DATA = [
    {
        "CVE": "CVE-2026-66807",
        "severity": "low",
        "public_date": "2026-08-14T17:00:00Z",
        "bugzilla_description": "console: potential XSS vulnerability",
        "affected_packages": ["console"],
    }
]


def test_parse():
    parser = RedHatParser()

    results = parser.parse(
        json.dumps(SAMPLE_DATA),
        "https://access.redhat.com/hydra/rest/securitydata/cve.json",
    )

    assert len(results) == 1

    advisory = results[0]

    assert advisory["cve"] == "CVE-2026-66807"
    assert advisory["severity"] == "low"
    assert advisory["product"] == "console"
    assert advisory["organization"] == "Red Hat"
    assert advisory["publication_date"] == datetime(
        2026,
        8,
        14,
        17,
        0,
    )


def test_get_next_page():
    parser = RedHatParser()
    html = json.dumps([{}, {}])

    next_url = parser.get_next_page(
        html,
        (
            "https://access.redhat.com/hydra/rest/securitydata/"
            "cve.json?per_page=2&page=1"
        ),
    )

    query_params = parse_qs(
        urlparse(next_url).query
    )

    assert query_params["page"] == ["2"]
    assert query_params["per_page"] == ["2"]


def test_get_next_page_returns_none_on_last_page():
    parser = RedHatParser()
    html = json.dumps([{}])

    next_url = parser.get_next_page(
        html,
        (
            "https://access.redhat.com/hydra/rest/securitydata/"
            "cve.json?per_page=2&page=1"
        ),
    )

    assert next_url is None

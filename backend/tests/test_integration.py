from app.models.source import Source
from app.services import crawl_job_service
from app.crawler.engine import CrawlerEngine
from app.database import database as database_module


SAMPLE_UBUNTU_HTML = """
<html>
    <body>
        <div id="notices-list">
            <section class="p-section--shallow">
                <div class="row">
                    <div class="col-6">
                        <h3>
                            <a href="/security/notices/USN-9999-1">
                                USN-9999-1: Integration Test Vulnerability
                            </a>
                        </h3>

                        <p class="u-text--muted">
                            18 August 2026
                        </p>

                        <p class="u-no-margin--bottom">
                            A local integration test security issue.
                        </p>

                        <a href="/security/CVE-2026-9999">
                            CVE-2026-9999
                        </a>
                    </div>
                </div>
            </section>
        </div>
    </body>
</html>
"""


def test_full_crawl_integration(
    client,
    db,
    monkeypatch,
):
    """
    Full integration flow:

    REST API
        -> crawl job
        -> crawler
        -> Ubuntu parser
        -> database
        -> advisory API
    """

    # -------------------------------------------------
    # 1. Create an approved test source in the test DB
    # -------------------------------------------------
    source = Source(
        name="Ubuntu Integration Test",
        base_url=(
            "https://ubuntu.com/security/notices"
        ),
        enabled_status=True,
        request_delay=1,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    # -------------------------------------------------
    # 2. Ensure the background worker uses
    #    the same temporary test database.
    # -------------------------------------------------
    # Background worker may obtain SessionLocal either
    # from crawl_job_service or directly from database.py.
    # Patch both so the whole integration flow uses
    # the same temporary test database.

    monkeypatch.setattr(
        database_module,
        "SessionLocal",
        lambda: db,
    )

    monkeypatch.setattr(
        crawl_job_service,
        "SessionLocal",
        lambda: db,
        raising=False,
    )

    # -------------------------------------------------
    # 3. Replace real HTTP crawling with a local
    #    HTML fixture.
    #
    #    We still use the real parser selected by
    #    crawl_job_service.
    # -------------------------------------------------
    def fake_crawl(
        self,
        start_url,
        parser,
        max_pages=5,
    ):
        self.pages_visited = 1

        return parser.parse(
            SAMPLE_UBUNTU_HTML,
            start_url,
        )

    monkeypatch.setattr(
        CrawlerEngine,
        "crawl",
        fake_crawl,
    )

    # -------------------------------------------------
    # 4. Start crawl through the REST API
    # -------------------------------------------------
    response = client.post(
        "/api/crawls",
        json={
            "source_ids": [
                source.id,
            ],
            "maximum_pages": 1,
        },
    )

    assert response.status_code == 200

    crawl_data = response.json()

    assert crawl_data["job_id"].startswith(
        "crawl_"
    )

    job_id = crawl_data["job_id"]

    # -------------------------------------------------
    # 5. Retrieve crawl status through REST API
    # -------------------------------------------------
    status_response = client.get(
        f"/api/crawls/{job_id}"
    )

    assert status_response.status_code == 200

    status_data = status_response.json()

    assert status_data["job_id"] == job_id

    assert status_data["status"] == "completed"

    assert status_data["pages_visited"] == 1

    assert status_data["records_extracted"] == 1

    assert status_data["error_count"] == 0

    # -------------------------------------------------
    # 6. Retrieve extracted record through REST API
    # -------------------------------------------------
    advisories_response = client.get(
        "/api/advisories"
        "?keyword=CVE-2026-9999"
    )

    assert (
        advisories_response.status_code
        == 200
    )

    advisories = (
        advisories_response.json()
    )

    assert len(advisories) == 1

    advisory = advisories[0]

    # -------------------------------------------------
    # 7. Verify parsed + stored data
    # -------------------------------------------------
    assert advisory["title"] == (
        "USN-9999-1: "
        "Integration Test Vulnerability"
    )

    assert advisory["organization"] == (
        "Ubuntu"
    )

    assert advisory["cve"] == (
        "CVE-2026-9999"
    )

    assert advisory["source_domain"] == (
        "ubuntu.com"
    )

    assert advisory["summary"] == (
        "A local integration test "
        "security issue."
    )

    assert advisory["url"] == (
        "https://ubuntu.com/security/"
        "notices/USN-9999-1"
    )
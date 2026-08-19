from app.models.source import Source
from app.models.advisory import Advisory


def create_test_source(db):
    source = Source(
        name="Ubuntu Test",
        base_url=(
            "https://ubuntu.com/"
            "security/notices"
        ),
        enabled_status=True,
        request_delay=2,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


def test_health_endpoint(client):
    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert "database" in data
    assert "crawler" in data


def test_source_creation(client):
    response = client.post(
        "/api/sources",
        json={
            "name": "Ubuntu Test Source",
            "base_url": (
                "https://ubuntu.com/"
                "security/notices?test=1"
            ),
            "enabled_status": False,
            "request_delay": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["name"]
        == "Ubuntu Test Source"
    )

    assert (
        data["enabled_status"]
        is False
    )


def test_source_validation_rejects_localhost(
    client,
):
    response = client.post(
        "/api/sources",
        json={
            "name": "Unsafe Source",
            "base_url": (
                "http://127.0.0.1:8000"
            ),
            "enabled_status": False,
            "request_delay": 2,
        },
    )

    assert response.status_code == 400


def test_source_validation_rejects_unsupported(
    client,
):
    response = client.post(
        "/api/sources",
        json={
            "name": "Unsupported Source",
            "base_url": (
                "https://example.com"
            ),
            "enabled_status": False,
            "request_delay": 2,
        },
    )

    assert response.status_code == 400


def test_duplicate_source_rejected(
    client,
):
    payload = {
        "name": "Ubuntu Duplicate",
        "base_url": (
            "https://ubuntu.com/"
            "security/notices?duplicate=1"
        ),
        "enabled_status": False,
        "request_delay": 2,
    }

    first = client.post(
        "/api/sources",
        json=payload,
    )

    assert first.status_code == 200

    second = client.post(
        "/api/sources",
        json=payload,
    )

    assert second.status_code == 409


def test_source_not_found(client):
    response = client.put(
        "/api/sources/999999",
        json={
            "name": "Missing",
            "base_url": (
                "https://ubuntu.com/"
                "security/notices"
            ),
            "enabled_status": False,
            "request_delay": 2,
        },
    )

    assert response.status_code == 404


def test_crawl_job_creation(
    client,
    db,
    monkeypatch,
):
    source = create_test_source(db)

    # We only want to test job creation here,
    # not perform a real network crawl.
    monkeypatch.setattr(
        "app.services.crawl_job_service."
        "execute_crawl_job",
        lambda *args, **kwargs: None,
    )

    response = client.post(
        "/api/crawls",
        json={
            "source_ids": [
                source.id,
            ],
            "maximum_pages": 1,
            "keywords": [
                "test",
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"].startswith(
        "crawl_"
    )

    assert data["status"] == "queued"


def test_crawl_job_status(
    client,
    db,
    monkeypatch,
):
    source = create_test_source(db)

    monkeypatch.setattr(
        "app.services.crawl_job_service."
        "execute_crawl_job",
        lambda *args, **kwargs: None,
    )

    create_response = client.post(
        "/api/crawls",
        json={
            "source_ids": [
                source.id,
            ],
            "maximum_pages": 1,
        },
    )

    assert (
        create_response.status_code
        == 200
    )

    job_id = (
        create_response.json()["job_id"]
    )

    status_response = client.get(
        f"/api/crawls/{job_id}"
    )

    assert (
        status_response.status_code
        == 200
    )

    data = status_response.json()

    assert data["job_id"] == job_id

    assert data["status"] in {
        "queued",
        "running",
        "completed",
        "failed",
        "stopping",
        "stopped",
    }


def test_crawl_job_not_found(client):
    response = client.get(
        "/api/crawls/"
        "crawl_does_not_exist"
    )

    assert response.status_code == 404


def test_advisory_filtering(
    client,
    db,
):
    db.add_all(
        [
            Advisory(
                title=(
                    "Critical Kernel Issue"
                ),
                organization="Ubuntu",
                url=(
                    "https://example.test/1"
                ),
                source_domain="ubuntu.com",
                cve="CVE-2026-0001",
                product="Linux Kernel",
                severity="critical",
                summary=(
                    "Critical kernel test"
                ),
            ),
            Advisory(
                title=(
                    "Low Severity Package"
                ),
                organization="Test Vendor",
                url=(
                    "https://example.test/2"
                ),
                source_domain=(
                    "vendor.test"
                ),
                cve="CVE-2026-0002",
                product="Package",
                severity="low",
                summary="Low severity test",
            ),
        ]
    )

    db.commit()

    response = client.get(
        "/api/advisories"
        "?severity=critical"
        "&organization=Ubuntu"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert (
        data[0]["severity"]
        == "critical"
    )

    assert (
        data[0]["organization"]
        == "Ubuntu"
    )


def test_advisory_keyword_filter(
    client,
    db,
):
    db.add_all(
        [
            Advisory(
                title="Kernel Security Update",
                organization="Ubuntu",
                url=(
                    "https://example.test/3"
                ),
                source_domain="ubuntu.com",
                cve="CVE-2026-1000",
                product="Kernel",
                severity="high",
                summary=(
                    "Linux kernel vulnerability"
                ),
            ),
            Advisory(
                title="Browser Update",
                organization="Vendor",
                url=(
                    "https://example.test/4"
                ),
                source_domain=(
                    "vendor.test"
                ),
                cve="CVE-2026-2000",
                product="Browser",
                severity="medium",
                summary="Browser issue",
            ),
        ]
    )

    db.commit()

    response = client.get(
        "/api/advisories"
        "?keyword=kernel"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert (
        "Kernel"
        in data[0]["title"]
    )


def test_advisory_pagination(
    client,
    db,
):
    for index in range(5):
        db.add(
            Advisory(
                title=(
                    f"Test Advisory {index}"
                ),
                organization="Test",
                url=(
                    "https://example.test/"
                    f"{100 + index}"
                ),
                source_domain=(
                    "example.test"
                ),
                cve=(
                    f"CVE-2026-{3000 + index}"
                ),
                product="Test",
                severity="medium",
                summary="Pagination test",
            )
        )

    db.commit()

    first_page = client.get(
        "/api/advisories"
        "?page=1&page_size=2"
    )

    second_page = client.get(
        "/api/advisories"
        "?page=2&page_size=2"
    )

    assert (
        first_page.status_code
        == 200
    )

    assert (
        second_page.status_code
        == 200
    )

    assert len(
        first_page.json()
    ) == 2

    assert len(
        second_page.json()
    ) == 2

    first_ids = {
        item["id"]
        for item in first_page.json()
    }

    second_ids = {
        item["id"]
        for item in second_page.json()
    }

    assert first_ids.isdisjoint(
        second_ids
    )
from datetime import date, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.models.advisory import Advisory
from app.models.crawl_job import CrawlJob
from app.models.crawl_log import CrawlLog
from app.models.source import Source
from app.repositories import advisory_repository


@pytest.fixture
def db():
    test_engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(
        bind=test_engine
    )

    testing_session = sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
    )

    session = testing_session()

    session.add_all([
        Advisory(
            title="Linux kernel vulnerability",
            organization="NVD",
            publication_date=datetime(
                2026, 8, 10
            ),
            url="https://example.com/nvd-test",
            source_domain="nvd.nist.gov",
            cve="CVE-TEST-0001",
            product="Linux kernel",
            severity="high",
            summary="Kernel security issue",
        ),
        Advisory(
            title="Quay authentication vulnerability",
            organization="Red Hat",
            publication_date=datetime(
                2026, 8, 14
            ),
            url="https://example.com/redhat-test",
            source_domain="access.redhat.com",
            cve="CVE-TEST-0002",
            product="quay",
            severity="moderate",
            summary="Quay authentication issue",
        ),
        Advisory(
            title="OpenSSL vulnerability",
            organization="Ubuntu",
            publication_date=datetime(
                2026, 8, 1
            ),
            url="https://example.com/ubuntu-test",
            source_domain="ubuntu.com",
            cve="CVE-TEST-0003",
            product="OpenSSL",
            severity="high",
            summary="OpenSSL security issue",
        ),
    ])

    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(
        bind=test_engine
    )


def test_filters_by_keyword_and_source(db):
    results = advisory_repository.get_advisories(
        db,
        keyword="quay",
        source_domain="access.redhat.com",
    )

    assert len(results) == 1
    assert results[0].product == "quay"


def test_filters_by_severity_and_date(db):
    results = advisory_repository.get_advisories(
        db,
        severity="HIGH",
        date_from=date(2026, 8, 1),
        date_to=date(2026, 8, 10),
    )

    assert len(results) == 2
    assert all(
        result.severity == "high"
        for result in results
    )


def test_pagination_and_sorting(db):
    first_page = advisory_repository.get_advisories(
        db,
        sort_by="publication_date",
        sort_order="desc",
        page=1,
        page_size=2,
    )

    second_page = advisory_repository.get_advisories(
        db,
        sort_by="publication_date",
        sort_order="desc",
        page=2,
        page_size=2,
    )

    assert len(first_page) == 2
    assert len(second_page) == 1
    assert first_page[0].organization == "Red Hat"
    assert second_page[0].organization == "Ubuntu"

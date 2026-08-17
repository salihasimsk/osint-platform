from types import SimpleNamespace

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.services import crawl_job_service


client = TestClient(app)


def make_job(
    status="queued",
    progress=0,
):
    return SimpleNamespace(
        job_id="crawl_test_001",
        status=status,
        progress=progress,
        pages_visited=0,
        records_extracted=0,
        error_count=0,
        started_date=None,
        completed_date=None,
    )


def test_start_crawl(monkeypatch):
    executed_tasks = []

    monkeypatch.setattr(
        crawl_job_service,
        "start_crawl",
        lambda db, crawl: make_job(),
    )

    def fake_execute(
        job_id,
        source_ids,
        maximum_pages,
    ):
        executed_tasks.append({
            "job_id": job_id,
            "source_ids": source_ids,
            "maximum_pages": maximum_pages,
        })

    monkeypatch.setattr(
        crawl_job_service,
        "execute_crawl_job",
        fake_execute,
    )

    response = client.post(
        "/api/crawls",
        json={
            "source_ids": [1, 5],
            "maximum_pages": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    assert executed_tasks[0]["source_ids"] == [1, 5]


def test_get_crawl_status(monkeypatch):
    monkeypatch.setattr(
        crawl_job_service,
        "get_crawl",
        lambda db, job_id: make_job(
            status="completed",
            progress=100,
        ),
    )

    response = client.get(
        "/api/crawls/crawl_test_001"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["progress"] == 100


def test_get_missing_crawl(monkeypatch):
    def fake_get_crawl(db, job_id):
        raise HTTPException(
            status_code=404,
            detail="Crawl job not found",
        )

    monkeypatch.setattr(
        crawl_job_service,
        "get_crawl",
        fake_get_crawl,
    )

    response = client.get(
        "/api/crawls/not-found"
    )

    assert response.status_code == 404

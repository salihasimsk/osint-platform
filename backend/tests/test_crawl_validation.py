import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.mark.parametrize(
    "payload",
    [
        {
            "source_ids": [],
            "maximum_pages": 2,
        },
        {
            "source_ids": [0],
            "maximum_pages": 2,
        },
        {
            "source_ids": [1, 1],
            "maximum_pages": 2,
        },
        {
            "source_ids": [1],
            "maximum_pages": 0,
        },
        {
            "source_ids": [1],
            "maximum_pages": 101,
        },
        {
            "source_ids": [1, 2, 3, 4, 5, 6],
            "maximum_pages": 2,
        },
        {
            "source_ids": [1],
            "maximum_pages": 2,
            "keywords": ["security"] * 21,
        },
    ],
)
def test_rejects_invalid_crawl_requests(payload):
    response = client.post(
        "/api/crawls",
        json=payload,
    )

    assert response.status_code == 422

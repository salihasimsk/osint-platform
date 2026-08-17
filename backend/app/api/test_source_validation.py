from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_rejects_private_source_url():
    response = client.post(
        "/api/sources",
        json={
            "name": "Unsafe Local Test",
            "base_url": "http://127.0.0.1:9000",
            "enabled_status": True,
            "request_delay": 2,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "Source URL must be a public "
            "HTTP or HTTPS address"
        )
    }


def test_rejects_zero_request_delay():
    response = client.post(
        "/api/sources",
        json={
            "name": "Invalid Delay Test",
            "base_url": "https://example.com",
            "enabled_status": True,
            "request_delay": 0,
        },
    )

    assert response.status_code == 422


def test_rejects_blank_source_name():
    response = client.post(
        "/api/sources",
        json={
            "name": "   ",
            "base_url": "https://example.com",
            "enabled_status": True,
            "request_delay": 2,
        },
    )

    assert response.status_code == 422

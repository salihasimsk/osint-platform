from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_statistics_summary():
    response = client.get("/api/statistics/summary")

    assert response.status_code == 200

    data = response.json()

    assert "total_advisories" in data
    assert "unknown_severity" in data
    assert "by_organization" in data
    assert "active_sources" in data
    assert "completed_crawls" in data

    organization_total = sum(
        data["by_organization"].values()
    )

    assert organization_total == data["total_advisories"]

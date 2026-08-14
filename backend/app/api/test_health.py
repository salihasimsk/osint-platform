from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    
def test_health():
    response = client.get("/api/health")

    def test_health():
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "database": "connected",
            "crawler": "available",
        }

    assert response.status_code == 200
    
def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "OSINT Web Crawler API is running."
    }
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_fixtures_rejects_invalid_date_range():
    response = client.get(
        "/fixtures",
        params={
            "date_from": "2024-12-31",
            "date_to": "2024-01-01",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Baslangic tarihi bitis tarihinden sonra olamaz"
    )

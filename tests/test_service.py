from fastapi.testclient import TestClient
from backend.service import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_item():
    payload = {"id": 1, "name": "Orbital Core", "description": "Test item"}
    response = client.post("/items", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Item created"
    assert data["item"] == payload

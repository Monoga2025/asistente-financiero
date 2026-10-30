from fastapi.testclient import TestClient

from app.main import create_app


def test_rejects_requests_without_private_token(monkeypatch):
    monkeypatch.setenv("APP_TOKEN", "test-token")
    app = create_app()
    client = TestClient(app)

    response = client.get("/mobile/bootstrap")

    assert response.status_code == 401
    assert response.json()["detail"] == "Token privado invalido."


def test_accepts_requests_with_private_token(monkeypatch):
    monkeypatch.setenv("APP_TOKEN", "test-token")
    app = create_app()
    client = TestClient(app)

    response = client.get("/health", headers={"X-App-Token": "test-token"})

    assert response.status_code == 200
    assert response.json() == {"ok": True, "service": "cuentas-claras-api"}

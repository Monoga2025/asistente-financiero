import pytest
from fastapi.testclient import TestClient

import app.main as main

HEADERS = {"X-App-Token": "test-token"}


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("APP_TOKEN", "test-token")
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    return TestClient(main.create_app())


def test_new_endpoints_require_token(client):
    assert client.get("/api/goals").status_code == 401
    assert client.post("/api/autocategorize", json={"description": "pan"}).status_code == 401


def test_categories_endpoint(client):
    body = client.get("/api/categories", headers=HEADERS).json()
    assert "Otros" in body["categories"]


def test_autocategorize_uses_rules_without_ai_key(client):
    response = client.post("/api/autocategorize", json={"description": "Uber centro", "amount": 12000}, headers=HEADERS)
    assert response.json() == {"ok": True, "category": "Transporte", "source": "rules"}


def test_parse_text_endpoint(client):
    response = client.post("/api/expenses/parse-text", json={"text": "pan 5000, cafe 3 mil"}, headers=HEADERS)
    assert response.json()["items"] == [
        {"description": "pan", "amount": 5000, "category": "Alimentacion"},
        {"description": "cafe", "amount": 3000, "category": "Alimentacion"},
    ]


def test_parse_text_requires_text(client):
    assert client.post("/api/expenses/parse-text", json={"text": " "}, headers=HEADERS).status_code == 400


def test_create_goal_validates_and_persists(client, monkeypatch):
    saved = {}
    monkeypatch.setattr(main, "create_goal", lambda payload: saved.update(payload) or {"id": 1, **payload})

    ok = client.post("/api/goals", json={"name": "Viaje", "target_amount": 1_000_000}, headers=HEADERS)
    bad = client.post("/api/goals", json={"name": "", "target_amount": 10}, headers=HEADERS)

    assert ok.status_code == 200 and ok.json()["goal"]["id"] == 1
    assert saved["name"] == "Viaje"
    assert bad.status_code == 400


def test_goal_projection_404_and_ok(client, monkeypatch):
    monkeypatch.setattr(main, "get_goal", lambda goal_id: None)
    assert client.get("/api/goals/9/projection", headers=HEADERS).status_code == 404

    monkeypatch.setattr(
        main,
        "get_goal",
        lambda goal_id: {"id": goal_id, "name": "Viaje", "target_amount": 300_000, "current_saved": 0, "deadline": None},
    )
    body = client.get("/api/goals/1/projection?monthly_saving=100000", headers=HEADERS).json()
    assert body["projection"]["estimated_months"] == 3


def test_month_close_endpoint(client, monkeypatch):
    rows = {(2026, 7): [{"title": "Pago arriendo", "total_amount": 700_000, "share_ana": 350_000, "share_daniel": 350_000}]}
    monkeypatch.setattr(main, "get_expenses_for_month", lambda year, month: rows.get((year, month), []))

    body = client.get("/api/month-close?year=2026&month=7", headers=HEADERS).json()

    assert body["summary"]["total"] == 700_000
    assert body["summary"]["top_category"] == "Vivienda"
    assert client.get("/api/month-close?year=2026&month=13", headers=HEADERS).status_code == 422

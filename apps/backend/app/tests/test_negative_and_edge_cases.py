from fastapi.testclient import TestClient

from app.main import app
import app.api.endpoints as endpoints


client = TestClient(app)


def test_missing_email_returns_404():
    res = client.get("/emails/not_found_id")
    assert res.status_code == 404


def test_local_explanation_missing_email_returns_404():
    res = client.get("/emails/not_found_id/local-explanation")
    assert res.status_code == 404


def test_scan_batch_malformed_payload_returns_400():
    res = client.post("/scan-batch", json={"emails": {"bad": "shape"}})
    assert res.status_code == 400


def test_scan_email_fallback_when_ml_unavailable(monkeypatch):
    monkeypatch.setattr(endpoints, "ML_AVAILABLE", False)
    res = client.post("/scan-email", json={"subject": "x"})
    assert res.status_code == 200
    body = res.json()
    assert "local_explanation_available" in body
    assert body["prediction"] in {"phishing", "legitimate"}


def test_risk_mapping_edges():
    low = client.post("/scan-email", json={"subject": "hello", "body": "normal text", "urls": [], "attachments": []})
    assert low.status_code == 200
    assert low.json()["risk_level"] in {"low", "medium", "high", "critical"}

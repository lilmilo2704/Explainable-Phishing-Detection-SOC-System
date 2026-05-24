from fastapi.testclient import TestClient

from app.main import app
from services.ml_service import preprocessor


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


def test_scan_email_is_not_trusted_when_training_pipeline_is_unavailable(monkeypatch):
    missing_path = preprocessor.PREPROCESSOR_PATH.with_name("missing_preprocessor_for_negative_test.pkl")
    monkeypatch.setattr(preprocessor, "PREPROCESSOR_PATH", missing_path)
    res = client.post("/scan-email", json={"subject": "x"})
    assert res.status_code == 200
    body = res.json()
    assert "local_explanation_available" in body
    assert body["prediction"] == "needs_review"
    assert body["trusted_prediction"] is False
    assert body["pipeline_status"] == "unsafe_incomplete_features"


def test_risk_mapping_edges():
    low = client.post("/scan-email", json={"subject": "hello", "body": "normal text", "urls": [], "attachments": []})
    assert low.status_code == 200
    assert low.json()["risk_level"] in {"low", "medium", "high", "critical", "unknown"}

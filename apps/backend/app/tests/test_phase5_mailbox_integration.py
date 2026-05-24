from fastapi.testclient import TestClient

from app.main import app
from app.api import endpoints


client = TestClient(app)


def test_mailbox_providers_endpoint():
    res = client.get("/mailbox/providers")
    assert res.status_code == 200
    items = res.json()["items"]
    names = {item["name"] for item in items}
    assert "mock" in names
    assert "gmail" in names
    gmail = next(item for item in items if item["name"] == "gmail")
    assert set(gmail) == {"name", "status", "configuration_source", "missing"}


def test_mock_mailbox_sync_ingests_and_scores():
    res = client.post("/mailbox/sync", json={"provider": "mock", "limit": 3, "force_rescan": True})
    assert res.status_code == 200
    body = res.json()
    assert body["provider"] == "mock"
    assert body["imported"] >= 1
    assert body["scanned"] == body["imported"]
    assert len(body["items"]) == body["imported"]
    first = body["items"][0]
    assert "email_id" in first
    assert "prediction" in first
    assert "model_version" in first
    assert first["trusted_prediction"] is True

    emails = client.get("/emails?source=mock")
    assert emails.status_code == 200
    assert emails.json()["total"] >= body["imported"]

    repeated = client.post("/mailbox/sync", json={"provider": "mock", "limit": 3})
    assert repeated.status_code == 200
    assert repeated.json()["skipped"] >= 1


def test_default_live_queue_hides_mock_records_when_gmail_is_selected(monkeypatch):
    monkeypatch.setattr(endpoints, "get_default_mailbox_provider_name", lambda: "gmail")
    response = client.get("/emails")
    assert response.status_code == 200
    assert response.json()["mailbox_source"] == "gmail"
    assert all(item["mailbox_source"] == "gmail" for item in response.json()["items"])

    mock_response = client.get("/emails?source=mock")
    assert mock_response.status_code == 200
    assert mock_response.json()["items"]

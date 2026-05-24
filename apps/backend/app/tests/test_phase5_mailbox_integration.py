from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_mailbox_providers_endpoint():
    res = client.get("/mailbox/providers")
    assert res.status_code == 200
    items = res.json()["items"]
    names = {item["name"] for item in items}
    assert "mock" in names
    assert "gmail" in names


def test_mock_mailbox_sync_ingests_and_scores():
    res = client.post("/mailbox/sync", json={"provider": "mock", "limit": 3})
    assert res.status_code == 200
    body = res.json()
    assert body["provider"] == "mock"
    assert body["imported"] >= 1
    assert len(body["items"]) == body["imported"]
    first = body["items"][0]
    assert "email_id" in first
    assert "prediction" in first
    assert "model_version" in first

    emails = client.get("/emails")
    assert emails.status_code == 200
    assert emails.json()["total"] >= body["imported"]

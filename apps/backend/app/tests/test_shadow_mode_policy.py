from fastapi.testclient import TestClient

from app.main import app
from app.api import endpoints
from app.services import mailbox_sync_service


client = TestClient(app)


class _AutomaticQuarantineProvider:
    def __init__(self, provider_name: str, message_id: str):
        self.provider_name = provider_name
        self.message_id = message_id
        self.quarantine_calls: list[str] = []
        self.release_calls: list[str] = []

    def fetch_messages(self, limit=25):
        return [
            {
                "id": self.message_id,
                "mailbox_message_id": self.message_id,
                "subject": "High risk message",
                "sender": "alert@example.com",
                "reply_to": "other@example.com",
                "body": "Review requested.",
                "urls": [],
                "attachments": [],
            }
        ]

    def quarantine_message(self, mailbox_message_id):
        self.quarantine_calls.append(mailbox_message_id)
        return True

    def release_message(self, mailbox_message_id):
        self.release_calls.append(mailbox_message_id)
        return True


def _trusted_quarantine_prediction(payload):
    explanation = {
        "top_reasons": ["Indicators increased phishing risk; analyst review is required."],
        "raw_feature_contributions": [],
    }
    return {
        "prediction": "phishing",
        "confidence": 0.98,
        "risk_level": "high",
        "recommended_action": "quarantine",
        "model_name": "Random Forest v1",
        "model_version": "random_forest_v1",
        "teacher_model_id": "random_forest_v1",
        "surrogate_model_id": "ebm_random_forest_v1",
        "surrogate_model_name": "EBM for Random Forest v1",
        "explanation_version": "ebm_random_forest_v1",
        "feature_extractor_version": "test",
        "trusted_prediction": True,
        "pipeline_status": "ready",
        "explanation": explanation,
        "explanation_snapshot": explanation,
    }


def _sync_with_provider(monkeypatch, provider):
    monkeypatch.setattr(mailbox_sync_service, "get_mailbox_provider", lambda name: provider)
    monkeypatch.setattr(
        mailbox_sync_service.model_manager, "predict_email", _trusted_quarantine_prediction
    )
    return client.post(
        "/mailbox/sync",
        json={"provider": provider.provider_name, "limit": 1, "force_rescan": True},
    )


def test_gmail_sync_does_not_mutate_mailbox_by_default(monkeypatch):
    provider = _AutomaticQuarantineProvider("gmail", "gmail-shadow-default")
    monkeypatch.delenv("ALLOW_LIVE_GMAIL_ACTIONS", raising=False)
    monkeypatch.delenv("SHADOW_MODE", raising=False)

    response = _sync_with_provider(monkeypatch, provider)

    assert response.status_code == 200
    assert response.json()["quarantined"] == 0
    assert response.json()["items"][0]["recommended_action"] == "quarantine"
    assert provider.quarantine_calls == []
    detail = client.get("/emails/gmail-shadow-default").json()
    assert detail["quarantine_status"] != "quarantined"
    assert detail["review_status"] == "in_review"


def test_gmail_sync_does_not_mutate_mailbox_in_shadow_mode(monkeypatch):
    provider = _AutomaticQuarantineProvider("gmail", "gmail-shadow-enabled")
    monkeypatch.setenv("ALLOW_LIVE_GMAIL_ACTIONS", "true")
    monkeypatch.setenv("SHADOW_MODE", "true")

    response = _sync_with_provider(monkeypatch, provider)

    assert response.status_code == 200
    assert response.json()["quarantined"] == 0
    assert provider.quarantine_calls == []
    assert client.get("/emails/gmail-shadow-enabled").json()["review_status"] == "in_review"


def test_gmail_sync_mutates_only_when_live_actions_enabled_and_shadow_off(monkeypatch):
    provider = _AutomaticQuarantineProvider("gmail", "gmail-live-enabled")
    monkeypatch.setenv("ALLOW_LIVE_GMAIL_ACTIONS", "true")
    monkeypatch.setenv("SHADOW_MODE", "false")

    response = _sync_with_provider(monkeypatch, provider)

    assert response.status_code == 200
    assert response.json()["quarantined"] == 1
    assert provider.quarantine_calls == ["gmail-live-enabled"]
    detail = client.get("/emails/gmail-live-enabled").json()
    assert detail["quarantine_status"] == "quarantined"
    assert detail["review_status"] == "in_review"


def test_mock_sync_still_simulates_quarantine_in_shadow_mode(monkeypatch):
    provider = _AutomaticQuarantineProvider("mock", "mock-shadow-simulation")
    monkeypatch.setenv("SHADOW_MODE", "true")
    monkeypatch.delenv("ALLOW_LIVE_GMAIL_ACTIONS", raising=False)

    response = _sync_with_provider(monkeypatch, provider)

    assert response.status_code == 200
    assert response.json()["quarantined"] == 1
    assert provider.quarantine_calls == ["mock-shadow-simulation"]


def test_released_gmail_message_is_not_automatically_requarantined_on_rescan(monkeypatch):
    provider = _AutomaticQuarantineProvider("gmail", "gmail-analyst-released")
    monkeypatch.setattr(mailbox_sync_service, "get_mailbox_provider", lambda name: provider)
    monkeypatch.setattr(endpoints, "get_mailbox_provider", lambda name: provider)
    monkeypatch.setattr(mailbox_sync_service.model_manager, "predict_email", _trusted_quarantine_prediction)
    monkeypatch.setenv("ALLOW_LIVE_GMAIL_ACTIONS", "true")
    monkeypatch.setenv("SHADOW_MODE", "false")

    assert _sync_with_provider(monkeypatch, provider).status_code == 200
    assert provider.quarantine_calls == ["gmail-analyst-released"]
    assert client.post("/emails/gmail-analyst-released/release").status_code == 200

    response = _sync_with_provider(monkeypatch, provider)
    assert response.status_code == 200
    assert response.json()["quarantined"] == 0
    assert provider.quarantine_calls == ["gmail-analyst-released"]
    assert client.get("/emails/gmail-analyst-released").json()["quarantine_status"] == "released"


def test_confirmed_legitimate_feedback_suppresses_automatic_requarantine(monkeypatch):
    provider = _AutomaticQuarantineProvider("gmail", "gmail-analyst-legitimate")
    monkeypatch.setattr(mailbox_sync_service, "get_mailbox_provider", lambda name: provider)
    monkeypatch.setattr(mailbox_sync_service.model_manager, "predict_email", _trusted_quarantine_prediction)
    monkeypatch.setenv("ALLOW_LIVE_GMAIL_ACTIONS", "true")
    monkeypatch.setenv("SHADOW_MODE", "false")

    assert _sync_with_provider(monkeypatch, provider).status_code == 200
    created = client.post(
        "/emails/gmail-analyst-legitimate/feedback",
        json={"feedback_type": "wrong_detection", "user_comment": "Confirmed legitimate"},
    )
    assert created.status_code == 200
    reviewed = client.patch(
        f"/feedback/{created.json()['feedback_id']}/review",
        json={"analyst_label": "legitimate", "review_status": "confirmed", "actor": "analyst"},
    )
    assert reviewed.status_code == 200

    response = _sync_with_provider(monkeypatch, provider)
    assert response.status_code == 200
    assert response.json()["quarantined"] == 0
    assert provider.quarantine_calls == ["gmail-analyst-legitimate"]

from fastapi.testclient import TestClient

from app.main import app
from app.api import endpoints
from app.services import mailbox_sync_service


client = TestClient(app)


class _Provider:
    provider_name = "gmail"

    def fetch_messages(self, limit=25):
        return [
            {
                "id": "gmail_url_test",
                "mailbox_message_id": "gmail-message-url-test",
                "subject": "Verify",
                "sender": "alert@example.com",
                "reply_to": "reply@example.com",
                "body": "Review https://example.com/verify",
                "body_preview": "Review link",
                "urls": ["https://example.com/verify"],
                "attachments": [],
            }
        ]

    def quarantine_message(self, mailbox_message_id):
        return True

    def release_message(self, mailbox_message_id):
        return True


def _needs_review_prediction(payload):
    return {
        "prediction": "needs_review",
        "confidence": 0.0,
        "risk_level": "unknown",
        "recommended_action": "review",
        "model_name": "Random Forest v1",
        "model_version": "random_forest_v1",
        "teacher_model_id": "random_forest_v1",
        "surrogate_model_id": "ebm_random_forest_v1",
        "surrogate_model_name": "EBM for Random Forest v1",
        "explanation_version": "ebm_random_forest_v1",
        "feature_extractor_version": "test",
        "trusted_prediction": False,
        "pipeline_status": "unsafe_incomplete_features",
        "explanation": {"top_reasons": ["Needs review"], "raw_feature_contributions": []},
        "explanation_snapshot": {"top_reasons": ["Needs review"]},
    }


def test_sync_preserves_urls_in_inference_and_storage(monkeypatch):
    captured = {}

    def predict(payload):
        captured["urls"] = payload["urls"]
        return _needs_review_prediction(payload)

    monkeypatch.setattr(mailbox_sync_service, "get_mailbox_provider", lambda name: _Provider())
    monkeypatch.setattr(mailbox_sync_service.model_manager, "predict_email", predict)
    sync = client.post("/mailbox/sync", json={"provider": "gmail", "limit": 1, "force_rescan": True})
    assert sync.status_code == 200
    assert captured["urls"] == ["https://example.com/verify"]

    detail = client.get("/emails/gmail_url_test")
    assert detail.status_code == 200
    assert detail.json()["urls"] == ["https://example.com/verify"]


def test_sync_model_failure_is_marked_needs_review(monkeypatch):
    monkeypatch.setattr(mailbox_sync_service, "get_mailbox_provider", lambda name: _Provider())
    monkeypatch.setattr(
        mailbox_sync_service.model_manager,
        "predict_email",
        lambda payload: (_ for _ in ()).throw(RuntimeError("test failure")),
    )
    sync = client.post("/mailbox/sync", json={"provider": "gmail", "limit": 1, "force_rescan": True})
    assert sync.status_code == 200
    assert sync.json()["failed"] == 1
    assert sync.json()["items"][0]["prediction"] == "model_error"
    detail = client.get("/emails/gmail_url_test").json()
    assert detail["prediction_status"] == "model_error"
    assert detail["review_status"] == "in_review"


def test_force_rescan_preserves_analyst_workflow_statuses(monkeypatch):
    monkeypatch.setattr(mailbox_sync_service, "get_mailbox_provider", lambda name: _Provider())
    monkeypatch.setattr(endpoints, "get_mailbox_provider", lambda name: _Provider())
    monkeypatch.setattr(mailbox_sync_service.model_manager, "predict_email", _needs_review_prediction)
    monkeypatch.setenv("ALLOW_LIVE_GMAIL_ACTIONS", "true")
    monkeypatch.setenv("SHADOW_MODE", "false")

    initial = client.post("/mailbox/sync", json={"provider": "gmail", "limit": 1, "force_rescan": True})
    assert initial.status_code == 200
    assert client.post("/emails/gmail_url_test/quarantine").status_code == 200

    rescan_quarantined = client.post(
        "/mailbox/sync", json={"provider": "gmail", "limit": 1, "force_rescan": True}
    )
    assert rescan_quarantined.status_code == 200
    quarantined_detail = client.get("/emails/gmail_url_test").json()
    assert quarantined_detail["quarantine_status"] == "quarantined"
    assert quarantined_detail["review_status"] == "in_review"

    assert client.post("/emails/gmail_url_test/release").status_code == 200
    rescan_released = client.post(
        "/mailbox/sync", json={"provider": "gmail", "limit": 1, "force_rescan": True}
    )
    assert rescan_released.status_code == 200
    released_detail = client.get("/emails/gmail_url_test").json()
    assert released_detail["quarantine_status"] == "released"
    assert released_detail["review_status"] == "in_review"


def test_live_gmail_mailbox_actions_are_disabled_without_explicit_enablement(monkeypatch):
    monkeypatch.setattr(mailbox_sync_service, "get_mailbox_provider", lambda name: _Provider())
    monkeypatch.setattr(mailbox_sync_service.model_manager, "predict_email", _needs_review_prediction)
    monkeypatch.delenv("ALLOW_LIVE_GMAIL_ACTIONS", raising=False)
    monkeypatch.setenv("SHADOW_MODE", "true")
    sync = client.post("/mailbox/sync", json={"provider": "gmail", "limit": 1, "force_rescan": True})
    assert sync.status_code == 200

    def must_not_get_provider(name):
        raise AssertionError("Disabled Gmail action must not reach the provider.")

    monkeypatch.setattr(endpoints, "get_mailbox_provider", must_not_get_provider)
    quarantine = client.post("/emails/gmail_url_test/quarantine")
    release = client.post("/emails/gmail_url_test/release")
    uppercase_gmail = client.post("/emails/gmail_url_test/quarantine", json={"provider": "GMAIL"})
    provider_override = client.post("/emails/gmail_url_test/quarantine", json={"provider": "mock"})
    assert quarantine.status_code == 403
    assert release.status_code == 403
    assert uppercase_gmail.status_code == 403
    assert provider_override.status_code == 400


def test_shadow_mode_blocks_manual_gmail_actions_even_if_live_actions_are_enabled(monkeypatch):
    monkeypatch.setattr(mailbox_sync_service, "get_mailbox_provider", lambda name: _Provider())
    monkeypatch.setattr(mailbox_sync_service.model_manager, "predict_email", _needs_review_prediction)
    monkeypatch.setenv("ALLOW_LIVE_GMAIL_ACTIONS", "true")
    monkeypatch.setenv("SHADOW_MODE", "true")
    assert client.post("/mailbox/sync", json={"provider": "gmail", "limit": 1, "force_rescan": True}).status_code == 200

    def must_not_get_provider(name):
        raise AssertionError("Shadow mode Gmail action must not reach the provider.")

    monkeypatch.setattr(endpoints, "get_mailbox_provider", must_not_get_provider)
    assert client.post("/emails/gmail_url_test/quarantine").status_code == 403
    assert client.post("/emails/gmail_url_test/release").status_code == 403

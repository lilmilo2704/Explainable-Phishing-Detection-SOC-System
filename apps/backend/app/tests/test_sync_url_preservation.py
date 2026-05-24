from fastapi.testclient import TestClient

from app.main import app
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


def test_sync_preserves_urls_in_inference_and_storage(monkeypatch):
    captured = {}

    def predict(payload):
        captured["urls"] = payload["urls"]
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

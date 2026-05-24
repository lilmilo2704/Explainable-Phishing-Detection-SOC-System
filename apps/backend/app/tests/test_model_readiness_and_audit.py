from fastapi.testclient import TestClient

from app.main import app
from services.ml_service import preprocessor


client = TestClient(app)


def test_model_readiness_blocks_trusted_live_prediction_without_training_preprocessor(monkeypatch):
    missing_path = preprocessor.PREPROCESSOR_PATH.with_name("missing_preprocessor_for_safety_test.pkl")
    monkeypatch.setattr(preprocessor, "PREPROCESSOR_PATH", missing_path)
    readiness = client.get("/monitoring/model-readiness")
    assert readiness.status_code == 200
    payload = readiness.json()
    assert payload["default_teacher"] == "random_forest_v1"
    assert payload["default_surrogate"] == "ebm_random_forest_v1"
    assert payload["feature_schema_loaded"] is True
    assert payload["processed_feature_order_loaded"] is True
    assert payload["feature_order_match"] is True
    assert payload["feature_order_source"] == "fitted_surrogate_feature_names_in_"
    assert payload["preprocessor_loaded"] is False
    assert payload["safe_for_live_prediction"] is False

    scan = client.post(
        "/scan-email",
        json={"subject": "Verify account", "body": "Use https://example.com/login", "urls": ["https://example.com/login"]},
    )
    assert scan.status_code == 200
    assert scan.json()["recommended_action"] == "review"
    assert scan.json()["trusted_prediction"] is False


def test_quarantine_release_and_feedback_are_audited():
    emails = client.get("/emails?source=mock&page_size=10").json()["items"]
    assert emails
    email_id = emails[0]["id"]

    client.post(f"/emails/{email_id}/quarantine", json={"actor": "analyst", "reason": "test"})
    release = client.post(f"/emails/{email_id}/release", json={"actor": "analyst", "reason": "test"})
    repeated_release = client.post(f"/emails/{email_id}/release", json={"actor": "analyst", "reason": "test"})
    assert release.status_code == 200
    assert repeated_release.json()["changed"] is False
    feedback = client.post(
        f"/emails/{email_id}/feedback",
        json={"feedback_type": "wrong_detection", "user_comment": "check", "submitted_by": "user"},
    )
    assert feedback.status_code == 200
    review = client.patch(
        f"/feedback/{feedback.json()['feedback_id']}/review",
        json={"analyst_label": "legitimate", "review_status": "confirmed", "actor": "analyst"},
    )
    assert review.status_code == 200

    audit = client.get("/audit").json()["items"]
    actions = {item["action_type"] for item in audit}
    assert "user_feedback_submitted" in actions
    assert "analyst_feedback_review" in actions

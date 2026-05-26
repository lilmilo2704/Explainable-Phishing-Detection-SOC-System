from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def _create_feedback_for_email(email_id: str):
    res = client.post(
        f"/emails/{email_id}/feedback",
        json={
            "feedback_type": "wrong_detection",
            "user_comment": "Needs analyst review",
            "submitted_by": "analyst@company.com",
        },
    )
    assert res.status_code == 200
    return res.json()["feedback_id"]


def test_phase4_review_derives_error_type_and_updates_monitoring():
    emails = client.get("/emails?source=mock").json()["items"]
    target = next((e for e in emails if e.get("prediction") == "phishing"), emails[0])
    fb_id = _create_feedback_for_email(target["id"])

    review = client.patch(
        f"/feedback/{fb_id}/review",
        json={
            "analyst_label": "legitimate",
            "error_type": "false_negative",
            "reason_category": "legitimate_business_email",
            "review_status": "confirmed",
            "added_to_improvement_dataset": True,
            "actor": "analyst",
        },
    )
    assert review.status_code == 200

    all_feedback = client.get("/feedback?source=mock").json()
    updated = next((f for f in all_feedback if f["id"] == fb_id), None)
    assert updated is not None
    assert updated["error_type"] == "false_positive"
    assert updated["review_status"] == "confirmed"
    assert updated["added_to_improvement_dataset"] is False

    health = client.get("/monitoring/model-health?source=mock")
    assert health.status_code == 200
    body = health.json()
    assert body["confirmed_feedback"] >= 1
    assert body["false_positives"] >= 1


def test_feedback_preserves_original_explanation_snapshot_reference():
    explanation = client.get("/emails/email_001/local-explanation")
    assert explanation.status_code == 200
    snapshot_id = explanation.json()["snapshot_id"]
    prediction_id = explanation.json()["prediction_id"]
    assert snapshot_id

    created = client.post(
        "/emails/email_001/feedback",
        json={"feedback_type": "wrong_detection", "user_comment": "Review original evidence"},
    )
    assert created.status_code == 200
    assert created.json()["prediction_id"] == prediction_id
    assert created.json()["explanation_snapshot_id"] == snapshot_id

    stored = next(
        row for row in client.get("/feedback?source=mock").json()
        if row["id"] == created.json()["feedback_id"]
    )
    assert stored["prediction_id"] == prediction_id
    assert stored["explanation_snapshot_id"] == snapshot_id


def test_rejected_feedback_has_no_validated_classification():
    fb_id = _create_feedback_for_email("email_001")
    review = client.patch(
        f"/feedback/{fb_id}/review",
        json={
            "analyst_label": "legitimate",
            "error_type": "false_positive",
            "review_status": "rejected",
            "actor": "analyst",
        },
    )
    assert review.status_code == 200
    stored = next(
        row for row in client.get("/feedback?source=mock").json() if row["id"] == fb_id
    )
    assert stored["review_status"] == "rejected"
    assert stored["analyst_label"] is None
    assert stored["error_type"] is None
    assert stored["added_to_improvement_dataset"] is False


def test_phase4_export_is_disabled_for_prototype():
    res = client.post("/feedback/export-confirmed")
    assert res.status_code == 409

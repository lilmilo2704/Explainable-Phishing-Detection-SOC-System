from fastapi.testclient import TestClient
import os

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
    emails = client.get("/emails").json()["items"]
    target = next((e for e in emails if e.get("prediction") == "phishing"), emails[0])
    fb_id = _create_feedback_for_email(target["id"])

    review = client.patch(
        f"/feedback/{fb_id}/review",
        json={
            "analyst_label": "legitimate",
            "reason_category": "legitimate_business_email",
            "review_status": "confirmed",
            "added_to_improvement_dataset": True,
        },
    )
    assert review.status_code == 200

    all_feedback = client.get("/feedback").json()
    updated = next((f for f in all_feedback if f["id"] == fb_id), None)
    assert updated is not None
    assert updated["error_type"] == "false_positive"
    assert updated["review_status"] == "confirmed"
    assert updated["added_to_improvement_dataset"] is True

    health = client.get("/monitoring/model-health")
    assert health.status_code == 200
    body = health.json()
    assert body["confirmed_feedback"] >= 1
    assert body["false_positives"] >= 1


def test_phase4_export_confirmed_feedback():
    res = client.post("/feedback/export-confirmed")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["format"] == "json"
    assert os.path.exists(data["export_path"])

from fastapi.testclient import TestClient

from app.main import app
import init_db as db_init


db_init.init_db()
client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_emails_and_local_explanation_flow():
    emails = client.get("/emails?source=mock")
    assert emails.status_code == 200
    items = emails.json()["items"]
    assert len(items) > 0
    email_id = items[0]["id"]

    detail = client.get(f"/emails/{email_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == email_id

    exp = client.get(f"/emails/{email_id}/local-explanation")
    assert exp.status_code == 200
    assert "human_summary" in exp.json()


def test_scan_email_and_scan_batch():
    payload = {
        "subject": "Urgent action required",
        "body": "Please verify now",
        "sender": "test@example.com",
        "reply_to": "test@example.com",
        "urls": ["https://example.com/login"],
        "attachments": [],
        "has_links": True,
    }
    res = client.post("/scan-email", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "prediction" in body
    assert "model_version" in body

    batch = client.post("/scan-batch", json={"emails": [payload, payload]})
    assert batch.status_code == 200
    assert batch.json()["total"] == 2


def test_feedback_and_quarantine_release_flow():
    emails = client.get("/emails?source=mock")
    email_id = emails.json()["items"][0]["id"]

    create_fb = client.post(
        f"/emails/{email_id}/feedback",
        json={
            "feedback_type": "wrong_detection",
            "user_comment": "Please review this case",
            "submitted_by": "analyst@company.com",
        },
    )
    assert create_fb.status_code == 200
    feedback_id = create_fb.json()["feedback_id"]

    review_fb = client.patch(
        f"/feedback/{feedback_id}/review",
        json={
            "analyst_label": "legitimate",
            "error_type": "false_positive",
            "reason_category": "business_email",
            "review_status": "confirmed",
            "added_to_improvement_dataset": False,
        },
    )
    assert review_fb.status_code == 200

    q = client.post(f"/emails/{email_id}/quarantine")
    assert q.status_code == 200
    r = client.post(f"/emails/{email_id}/release")
    assert r.status_code == 200

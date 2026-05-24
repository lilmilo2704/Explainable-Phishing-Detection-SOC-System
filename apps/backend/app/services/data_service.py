from sqlalchemy.orm import Session
from app.models import Email, Prediction, Explanation, Feedback
from typing import List, Optional
from datetime import datetime, UTC
import json
from pathlib import Path
from uuid import uuid4
from sqlalchemy import desc

def get_emails(db: Session) -> List[Email]:
    # Keep operational views focused on real mailbox data only.
    # Current real mailbox integration uses ids prefixed with "gmail_".
    return (
        db.query(Email)
        .filter(Email.id.like("gmail_%"))
        .order_by(desc(Email.received_at), desc(Email.id))
        .all()
    )

def get_email_by_id(db: Session, email_id: str) -> Email:
    return db.query(Email).filter(Email.id == email_id).first()

def get_predictions(db: Session) -> List[Prediction]:
    return db.query(Prediction).all()

def get_prediction_by_email_id(db: Session, email_id: str) -> Prediction:
    return (
        db.query(Prediction)
        .filter(Prediction.email_id == email_id)
        .order_by(desc(Prediction.created_at), desc(Prediction.id))
        .first()
    )

def get_local_explanations(db: Session) -> List[Explanation]:
    return db.query(Explanation).all()

def get_local_explanation_by_email_id(db: Session, email_id: str) -> Explanation:
    return db.query(Explanation).filter(Explanation.email_id == email_id).first()

def get_feedback_cases(db: Session) -> List[Feedback]:
    return db.query(Feedback).all()


def get_feedback_by_id(db: Session, feedback_id: str) -> Optional[Feedback]:
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


def create_feedback_case(
    db: Session,
    *,
    email_id: str,
    feedback_type: str,
    user_comment: Optional[str],
    submitted_by: Optional[str],
) -> Feedback:
    pred = get_prediction_by_email_id(db, email_id)
    feedback_id = f"feedback_{uuid4().hex}"
    feedback = Feedback(
        id=feedback_id,
        email_id=email_id,
        prediction_id=pred.id if pred else None,
        feedback_type=feedback_type,
        original_prediction=pred.prediction if pred else None,
        original_confidence=pred.confidence if pred else None,
        user_feedback=user_comment,
        comments=user_comment,
        analyst_id=submitted_by,
        review_status="pending",
        status="pending",
        created_at=datetime.now(UTC),
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def review_feedback_case(
    db: Session,
    *,
    feedback_id: str,
    analyst_label: Optional[str],
    error_type: Optional[str],
    reason_category: Optional[str],
    review_status: str,
    added_to_improvement_dataset: bool,
):
    fb = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not fb:
        return None
    fb.analyst_label = analyst_label
    fb.error_type = error_type
    fb.reason_category = reason_category
    fb.review_status = review_status
    fb.added_to_improvement_dataset = added_to_improvement_dataset
    fb.status = "reviewed"
    fb.reviewed_at = datetime.now(UTC)
    db.commit()
    db.refresh(fb)
    return fb


def get_feedback_monitoring_counts(db: Session) -> dict:
    feedback = db.query(Feedback).all()
    confirmed = [f for f in feedback if f.review_status == "confirmed"]
    counts = {
        "total_feedback": len(feedback),
        "confirmed_feedback": len(confirmed),
        "pending_feedback": sum(1 for f in feedback if f.review_status == "pending"),
        "false_positives": sum(1 for f in confirmed if f.error_type == "false_positive"),
        "false_negatives": sum(1 for f in confirmed if f.error_type == "false_negative"),
        "true_positives": sum(1 for f in confirmed if f.error_type == "true_positive"),
        "true_negatives": sum(1 for f in confirmed if f.error_type == "true_negative"),
        "improvement_dataset_candidates": sum(1 for f in confirmed if f.added_to_improvement_dataset),
    }
    return counts


def export_confirmed_feedback_for_improvement(db: Session, export_dir: Path) -> Path:
    export_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    export_path = export_dir / f"confirmed_feedback_{timestamp}.json"
    rows = db.query(Feedback).filter(Feedback.review_status == "confirmed").all()
    payload = [
        {
            "feedback_id": r.id,
            "email_id": r.email_id,
            "prediction_id": r.prediction_id,
            "original_prediction": r.original_prediction,
            "original_confidence": r.original_confidence,
            "analyst_label": r.analyst_label,
            "error_type": r.error_type,
            "reason_category": r.reason_category,
            "user_feedback": r.user_feedback,
            "added_to_improvement_dataset": r.added_to_improvement_dataset,
            "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else None,
            "model_version_snapshot": "rf_v1",
        }
        for r in rows
    ]
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return export_path


def upsert_email_from_mailbox(db: Session, email_data: dict) -> Email:
    email_id = email_data.get("id")
    if not email_id:
        raise ValueError("Email payload must include id")
    email = get_email_by_id(db, email_id)
    fields = {
        "mailbox_message_id": email_data.get("mailbox_message_id"),
        "subject": email_data.get("subject"),
        "sender": email_data.get("sender"),
        "sender_domain": email_data.get("sender_domain"),
        "recipient": email_data.get("recipient"),
        "reply_to": email_data.get("reply_to"),
        "received_at": email_data.get("received_at"),
        "body_preview": email_data.get("body_preview"),
        "url_count": email_data.get("url_count", 0),
        "attachment_count": email_data.get("attachment_count", 0),
        "has_links": email_data.get("has_links", False),
        "has_attachment": email_data.get("has_attachment", False),
        "quarantine_status": email_data.get("quarantine_status", "allowed"),
        "review_status": email_data.get("review_status", "none"),
    }
    if email is None:
        email = Email(id=email_id, **fields)
        db.add(email)
    else:
        for k, v in fields.items():
            setattr(email, k, v)
    db.commit()
    db.refresh(email)
    return email


def create_prediction_snapshot(db: Session, email_id: str, result: dict) -> Prediction:
    pred = Prediction(
        id=f"pred_{uuid4().hex}",
        email_id=email_id,
        prediction=result.get("prediction", "legitimate"),
        confidence=float(result.get("confidence", 0.0)),
        risk_level=result.get("risk_level", "low"),
        recommended_action=result.get("recommended_action", "allow"),
        model_name=result.get("model_name", "Random Forest"),
        model_version=result.get("model_version", "rf_v1"),
        teacher_model_id=result.get("teacher_model_id"),
        surrogate_model_id=result.get("surrogate_model_id"),
        feature_extractor_version=result.get("feature_extractor_version"),
        explanation_snapshot=result.get("explanation_snapshot"),
        created_at=datetime.now(UTC),
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred


def create_explanation_snapshot(
    db: Session, email_id: str, prediction_id: str, explanation: dict, model_version: str
) -> Explanation:
    exp = Explanation(
        id=f"exp_{uuid4().hex}",
        email_id=email_id,
        prediction_id=prediction_id,
        explainer_type=explanation.get("explainer_type", "EBM (surrogate of Random Forest)"),
        model_version=model_version,
        human_summary=explanation.get("human_summary"),
        top_features=explanation.get("top_features", []),
        created_at=datetime.now(UTC),
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp

def update_email_status(db: Session, email_id: str, new_status: str, status_type: str = "quarantine_status"):
    email = get_email_by_id(db, email_id)
    if email:
        if status_type == "quarantine_status":
            email.quarantine_status = new_status
        elif status_type == "review_status":
            email.review_status = new_status
        db.commit()
        db.refresh(email)
    return email

def get_global_explanations():
    # Global explanations are usually static or periodically updated JSON/metrics
    # fallback to mock for now
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data" / "sample"
    
    filepath = DATA_DIR / "sample_global_explanations.json"
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

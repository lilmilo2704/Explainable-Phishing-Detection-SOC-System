from datetime import UTC, datetime
from typing import Any, List, Optional
from uuid import uuid4

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import AuditLog, Email, Explanation, Feedback, MailboxSyncRun, Prediction


def _filter_source(query: Any, source: Optional[str]) -> Any:
    return query.filter(Email.mailbox_source == source) if source and source != "all" else query


def get_emails(
    db: Session, *, source: Optional[str] = None, offset: int = 0, limit: Optional[int] = None
) -> List[Email]:
    query = db.query(Email).order_by(desc(Email.received_at), desc(Email.id))
    query = _filter_source(query, source)
    if offset:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


def count_emails(db: Session, *, source: Optional[str] = None) -> int:
    return _filter_source(db.query(Email), source).count()


def get_email_by_id(db: Session, email_id: str) -> Optional[Email]:
    return db.query(Email).filter(Email.id == email_id).first()


def get_email_by_mailbox_message_id(db: Session, source: str, message_id: str) -> Optional[Email]:
    return (
        db.query(Email)
        .filter(Email.mailbox_source == source, Email.mailbox_message_id == message_id)
        .first()
    )


def get_predictions(db: Session, *, source: Optional[str] = None) -> List[Prediction]:
    query = db.query(Prediction).join(Email).filter(Prediction.is_latest.is_(True))
    query = _filter_source(query, source)
    return query.all()


def get_prediction_by_email_id(db: Session, email_id: str) -> Optional[Prediction]:
    return (
        db.query(Prediction)
        .filter(Prediction.email_id == email_id, Prediction.is_latest.is_(True))
        .order_by(desc(Prediction.created_at), desc(Prediction.id))
        .first()
        or db.query(Prediction)
        .filter(Prediction.email_id == email_id)
        .order_by(desc(Prediction.created_at), desc(Prediction.id))
        .first()
    )


def get_local_explanations(db: Session) -> List[Explanation]:
    return db.query(Explanation).all()


def get_local_explanation_by_email_id(db: Session, email_id: str) -> Optional[Explanation]:
    return (
        db.query(Explanation)
        .filter(Explanation.email_id == email_id)
        .order_by(desc(Explanation.created_at), desc(Explanation.id))
        .first()
    )


def get_feedback_cases(db: Session, *, source: Optional[str] = None) -> List[Feedback]:
    query = db.query(Feedback).join(Email).order_by(desc(Feedback.created_at))
    query = _filter_source(query, source)
    return query.all()


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
    feedback = Feedback(
        id=f"feedback_{uuid4().hex}",
        email_id=email_id,
        prediction_id=pred.id if pred else None,
        feedback_type=feedback_type,
        original_prediction=pred.prediction if pred else None,
        original_confidence=pred.confidence if pred else None,
        user_feedback=user_comment,
        comments=user_comment,
        submitted_by=submitted_by or "user",
        feedback_source="user",
        review_status="pending_review",
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
    actor: str,
) -> Optional[Feedback]:
    feedback = get_feedback_by_id(db, feedback_id)
    if not feedback:
        return None
    feedback.analyst_label = analyst_label
    feedback.error_type = error_type
    feedback.reason_category = reason_category
    feedback.review_status = review_status
    feedback.added_to_improvement_dataset = False
    feedback.status = "reviewed"
    feedback.analyst_id = actor
    feedback.reviewed_at = datetime.now(UTC)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_feedback_monitoring_counts(db: Session, *, source: Optional[str] = None) -> dict[str, int]:
    query = db.query(Feedback).join(Email)
    feedback = _filter_source(query, source).all()
    confirmed = [row for row in feedback if row.review_status == "confirmed"]
    return {
        "total_feedback": len(feedback),
        "confirmed_feedback": len(confirmed),
        "pending_feedback": sum(1 for row in feedback if row.review_status in {"pending", "pending_review"}),
        "false_positives": sum(1 for row in confirmed if row.error_type == "false_positive"),
        "false_negatives": sum(1 for row in confirmed if row.error_type == "false_negative"),
        "true_positives": sum(1 for row in confirmed if row.error_type == "true_positive"),
        "true_negatives": sum(1 for row in confirmed if row.error_type == "true_negative"),
    }


def upsert_email_from_mailbox(db: Session, email_data: dict[str, Any]) -> Email:
    email_id = email_data.get("id")
    source = email_data.get("mailbox_source", "mock")
    message_id = email_data.get("mailbox_message_id")
    if not email_id:
        raise ValueError("Email payload must include id")
    email = (
        get_email_by_mailbox_message_id(db, source, message_id)
        if message_id
        else get_email_by_id(db, email_id)
    )
    fields = {
        "mailbox_source": source,
        "mailbox_message_id": message_id,
        "subject": email_data.get("subject"),
        "sender": email_data.get("sender"),
        "sender_domain": email_data.get("sender_domain"),
        "recipient": email_data.get("recipient"),
        "reply_to": email_data.get("reply_to"),
        "received_at": email_data.get("received_at"),
        "body_preview": email_data.get("body_preview"),
        "body": email_data.get("body"),
        "urls": email_data.get("urls", []),
        "attachments": email_data.get("attachments", []),
        "feature_snapshot": email_data.get("feature_snapshot"),
        "content_fingerprint": email_data.get("content_fingerprint"),
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
        for key, value in fields.items():
            setattr(email, key, value)
    db.commit()
    db.refresh(email)
    return email


def create_prediction_snapshot(db: Session, email_id: str, result: dict[str, Any]) -> Prediction:
    db.query(Prediction).filter(
        Prediction.email_id == email_id, Prediction.is_latest.is_(True)
    ).update({"is_latest": False}, synchronize_session=False)
    pred = Prediction(
        id=f"pred_{uuid4().hex}",
        email_id=email_id,
        prediction=result.get("prediction", "needs_review"),
        confidence=float(result.get("confidence", 0.0) or 0.0),
        risk_level=result.get("risk_level", "unknown"),
        recommended_action=result.get("recommended_action", "review"),
        model_name=result.get("model_name", "Random Forest"),
        model_version=result.get("model_version", "unknown"),
        teacher_model_id=result.get("teacher_model_id"),
        surrogate_model_id=result.get("surrogate_model_id"),
        feature_extractor_version=result.get("feature_extractor_version"),
        explanation_snapshot=result.get("explanation_snapshot"),
        explanation_version=result.get("explanation_version", result.get("surrogate_model_id")),
        content_fingerprint=result.get("content_fingerprint"),
        is_latest=True,
        trusted_prediction=bool(result.get("trusted_prediction", False)),
        pipeline_status=result.get("pipeline_status", "unknown"),
        created_at=datetime.now(UTC),
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred


def create_explanation_snapshot(
    db: Session, email_id: str, prediction_id: str, explanation: dict[str, Any], model_version: str
) -> Explanation:
    exp = Explanation(
        id=f"exp_{uuid4().hex}",
        snapshot_id=f"snapshot_{uuid4().hex}",
        email_id=email_id,
        prediction_id=prediction_id,
        explainer_type=explanation.get("explainer_type", "EBM surrogate"),
        model_version=model_version,
        human_summary=explanation.get("human_summary"),
        top_features=explanation.get("top_features", []),
        pipeline_status=explanation.get("pipeline_status"),
        created_at=datetime.now(UTC),
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


def update_email_status(
    db: Session,
    email_id: str,
    new_status: str,
    status_type: str = "quarantine_status",
    *,
    model_error: Optional[str] = None,
) -> Optional[Email]:
    email = get_email_by_id(db, email_id)
    if email:
        if status_type == "quarantine_status":
            email.quarantine_status = new_status
        elif status_type == "review_status":
            email.review_status = new_status
        elif status_type == "prediction_status":
            email.prediction_status = new_status
        if model_error is not None:
            email.model_error = model_error
        db.commit()
        db.refresh(email)
    return email


def mark_email_scan_result(
    db: Session, email: Email, *, status: str, model_error: Optional[str] = None
) -> None:
    email.prediction_status = status
    email.model_error = model_error
    email.last_scanned_at = datetime.now(UTC)
    if status in {"needs_review", "model_error"} and email.review_status == "none":
        email.review_status = "in_review"
    db.commit()


def create_audit_event(
    db: Session,
    *,
    action_type: str,
    actor: str,
    email_id: Optional[str] = None,
    previous_state: Optional[dict[str, Any]] = None,
    new_state: Optional[dict[str, Any]] = None,
    reason: Optional[str] = None,
    model_version: Optional[str] = None,
    explanation_version: Optional[str] = None,
    explanation_snapshot_id: Optional[str] = None,
) -> AuditLog:
    event = AuditLog(
        id=f"audit_{uuid4().hex}",
        email_id=email_id,
        actor=actor,
        action_type=action_type,
        previous_state=previous_state,
        new_state=new_state,
        reason=reason,
        model_version=model_version,
        explanation_version=explanation_version,
        explanation_snapshot_id=explanation_snapshot_id,
        created_at=datetime.now(UTC),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_audit_events(db: Session, limit: int = 100) -> List[AuditLog]:
    return db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()


def start_sync_run(db: Session, provider: str, actor: str) -> MailboxSyncRun:
    run = MailboxSyncRun(
        id=f"sync_{uuid4().hex}",
        provider=provider,
        actor=actor,
        status="running",
        started_at=datetime.now(UTC),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def finish_sync_run(db: Session, run: MailboxSyncRun, **values: Any) -> MailboxSyncRun:
    for key, value in values.items():
        setattr(run, key, value)
    run.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(run)
    return run


def get_last_sync_run(db: Session, *, provider: Optional[str] = None) -> Optional[MailboxSyncRun]:
    query = db.query(MailboxSyncRun)
    if provider and provider != "all":
        query = query.filter(MailboxSyncRun.provider == provider)
    return query.order_by(desc(MailboxSyncRun.started_at)).first()


def get_live_metrics(db: Session, *, source: Optional[str] = None) -> dict[str, Any]:
    emails = get_emails(db, source=source)
    predictions = [get_prediction_by_email_id(db, row.id) for row in emails]
    predictions = [row for row in predictions if row is not None]
    feedback = get_feedback_monitoring_counts(db, source=source)
    confidences = [row.confidence for row in predictions if row.confidence is not None]
    last_sync = get_last_sync_run(db, provider=source)
    return {
        "total_scanned": len(predictions),
        "prediction_distribution": {
            "phishing": sum(1 for row in predictions if row.prediction == "phishing"),
            "legitimate": sum(1 for row in predictions if row.prediction == "legitimate"),
            "needs_review": sum(1 for row in predictions if row.prediction not in {"phishing", "legitimate"}),
        },
        "quarantine_count": sum(1 for row in emails if row.quarantine_status == "quarantined"),
        "average_confidence": round(sum(confidences) / len(confidences), 4) if confidences else None,
        "review_backlog": sum(1 for row in emails if row.review_status in {"new", "in_review"}),
        "model_errors": sum(1 for row in emails if row.prediction_status == "model_error"),
        "sync_failures": last_sync.failed if last_sync else 0,
        **feedback,
    }

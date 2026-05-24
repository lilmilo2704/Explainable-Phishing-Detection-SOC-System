import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ActiveModelConfigRequestSchema,
    EmailDetailSchema,
    FeedbackCreateSchema,
    FeedbackReviewSchema,
    FeedbackSchema,
    MailboxActionSchema,
    MailboxSyncRequestSchema,
    MailboxSyncResponseSchema,
)
from app.services import data_service
from app.services.mailbox_integration import (
    GmailMailboxProvider,
    get_default_mailbox_provider_name,
    get_mailbox_provider,
)
from app.services.mailbox_sync_service import perform_mailbox_sync
from app.services.model_manager import ModelManagerError, model_manager

logger = logging.getLogger(__name__)
router = APIRouter()


def _live_source(requested_source: str | None) -> str:
    return requested_source or get_default_mailbox_provider_name()


def _serialize_list_email(email: Any, prediction: Any) -> dict[str, Any]:
    return {
        "id": email.id,
        "mailbox_source": email.mailbox_source,
        "mailbox_message_id": email.mailbox_message_id,
        "subject": email.subject,
        "sender": email.sender,
        "sender_domain": email.sender_domain,
        "recipient": email.recipient,
        "reply_to": email.reply_to,
        "received_at": email.received_at,
        "body_preview": email.body_preview,
        "url_count": email.url_count,
        "attachment_count": email.attachment_count,
        "has_links": email.has_links,
        "has_attachment": email.has_attachment,
        "quarantine_status": email.quarantine_status,
        "review_status": email.review_status,
        "prediction_status": email.prediction_status,
        "model_error": email.model_error,
        "prediction": prediction.prediction if prediction else None,
        "confidence": prediction.confidence if prediction else None,
        "risk_level": prediction.risk_level if prediction else None,
        "teacher_model_id": prediction.teacher_model_id if prediction else None,
        "surrogate_model_id": prediction.surrogate_model_id if prediction else None,
        "model_version": prediction.model_version if prediction else None,
        "trusted_prediction": prediction.trusted_prediction if prediction else False,
        "pipeline_status": prediction.pipeline_status if prediction else None,
    }


def _scan_email_with_manager(payload: Dict[Any, Any]) -> Dict[str, Any]:
    result = model_manager.predict_email(payload)
    result["email_id"] = payload.get("email_id", "scan_new")
    result["local_explanation_available"] = bool(result.get("explanation"))
    return result


@router.get("/dashboard/summary")
def get_dashboard_summary(
    source: str | None = Query(None, pattern="^(gmail|mock|all)$"),
    db: Session = Depends(get_db),
):
    selected_source = _live_source(source)
    metrics = data_service.get_live_metrics(db, source=selected_source)
    active = model_manager.get_active_model_config()
    readiness = model_manager.get_readiness()
    return {
        "metric_source": "live_operational_database",
        "emails_scanned": metrics["total_scanned"],
        "phishing_detected": metrics["prediction_distribution"]["phishing"],
        "quarantined": metrics["quarantine_count"],
        "pending_review": metrics["review_backlog"],
        "false_positive_reports": metrics["false_positives"],
        "false_negative_reports": metrics["false_negatives"],
        "average_confidence": metrics["average_confidence"],
        "high_risk_cases": sum(
            1
            for prediction in data_service.get_predictions(db, source=selected_source)
            if prediction.risk_level in {"high", "critical"}
        ),
        "model_errors": metrics["model_errors"],
        "pipeline_safe": readiness["safe_for_live_prediction"],
        "mailbox_source": selected_source,
        "current_model": {"name": active["teacher_model_name"], "version": active["teacher_model_id"]},
        "current_surrogate": {"name": active["surrogate_model_name"], "version": active["surrogate_model_id"]},
    }


@router.get("/emails", response_model=Dict[str, Any])
def list_emails(
    source: str | None = Query(None, pattern="^(gmail|mock|all)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    selected_source = _live_source(source)
    offset = (page - 1) * page_size
    emails = data_service.get_emails(db, source=selected_source, offset=offset, limit=page_size)
    items = [_serialize_list_email(email, data_service.get_prediction_by_email_id(db, email.id)) for email in emails]
    return {
        "items": items,
        "mailbox_source": selected_source,
        "page": page,
        "page_size": page_size,
        "total": data_service.count_emails(db, source=selected_source),
    }


@router.get("/emails/{email_id}", response_model=EmailDetailSchema)
def get_email_detail(email_id: str, db: Session = Depends(get_db)):
    email = data_service.get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    result = email.__dict__.copy()
    result["prediction_details"] = data_service.get_prediction_by_email_id(db, email_id)
    return result


@router.post("/scan-email")
def scan_email(payload: Dict[Any, Any], db: Session = Depends(get_db)):
    try:
        result = _scan_email_with_manager(payload)
        email_id = payload.get("email_id")
        email = data_service.get_email_by_id(db, email_id) if email_id else None
        if email:
            prediction = data_service.create_prediction_snapshot(db, email_id, result)
            explanation = result.get("explanation", {})
            data_service.create_explanation_snapshot(
                db,
                email_id=email_id,
                prediction_id=prediction.id,
                explanation={
                    "explainer_type": result.get("surrogate_model_name", "EBM surrogate"),
                    "human_summary": " ".join(explanation.get("top_reasons", [])),
                    "top_features": explanation.get("raw_feature_contributions", []),
                    "pipeline_status": result.get("pipeline_status"),
                },
                model_version=result.get("explanation_version", result.get("model_version", "unknown")),
            )
        return result
    except ModelManagerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Prediction request failed without logging message contents.")
        raise HTTPException(status_code=500, detail="Prediction failed. Review model readiness and server logs.") from None


@router.post("/api/scan-email")
def scan_email_api(payload: Dict[Any, Any], db: Session = Depends(get_db)):
    return scan_email(payload, db)


@router.post("/scan-batch")
def scan_batch(payload: Dict[Any, Any], db: Session = Depends(get_db)):
    emails = payload.get("emails", [])
    if not isinstance(emails, list):
        raise HTTPException(status_code=400, detail="emails must be a list")
    return {"items": [scan_email(item, db) for item in emails], "total": len(emails)}


@router.get("/api/models")
def get_models_registry():
    return model_manager.get_registry_payload()


@router.get("/api/models/active")
def get_active_models():
    return model_manager.get_active_model_config()


@router.post("/api/models/active")
def set_active_models(payload: ActiveModelConfigRequestSchema, db: Session = Depends(get_db)):
    before = model_manager.get_active_model_config()
    try:
        result = model_manager.set_active_model_config(payload.teacher_model_id, payload.surrogate_model_id)
    except ModelManagerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    data_service.create_audit_event(
        db,
        actor=payload.actor,
        action_type="model_switch",
        previous_state=before,
        new_state=result,
        model_version=result["teacher_model_id"],
        explanation_version=result["surrogate_model_id"],
    )
    return result


@router.get("/monitoring/model-readiness")
def get_model_readiness():
    return model_manager.get_readiness()


@router.get("/mailbox/providers")
def get_mailbox_providers():
    gmail_status = GmailMailboxProvider().configuration_status()
    return {
        "default_provider": get_default_mailbox_provider_name(),
        "items": [
            {"name": "mock", "status": "ready"},
            {
                "name": "gmail",
                "status": "configured" if gmail_status["configured"] else "configuration_required",
                "configuration_source": gmail_status["configuration_source"],
                "missing": gmail_status["missing"],
            },
        ],
    }


@router.post("/mailbox/sync", response_model=MailboxSyncResponseSchema)
def sync_mailbox(payload: MailboxSyncRequestSchema, db: Session = Depends(get_db)):
    try:
        return perform_mailbox_sync(
            db,
            provider_name=payload.provider,
            limit=payload.limit,
            force_rescan=payload.force_rescan,
            actor=payload.actor,
        )
    except Exception:
        logger.exception("Mailbox sync failed without logging message bodies or credentials.")
        raise HTTPException(
            status_code=400,
            detail="Mailbox sync failed. Check Gmail configuration and last sync status.",
        ) from None


@router.get("/mailbox/sync-status")
def get_mailbox_sync_status(
    source: str | None = Query(None, pattern="^(gmail|mock|all)$"),
    db: Session = Depends(get_db),
):
    selected_source = _live_source(source)
    run = data_service.get_last_sync_run(db, provider=selected_source)
    if not run:
        return {"status": "not_run", "provider": selected_source}
    return {
        "id": run.id,
        "provider": run.provider,
        "status": run.status,
        "last_sync_time": run.completed_at or run.started_at,
        "scanned": run.scanned,
        "skipped": run.skipped,
        "failed": run.failed,
        "quarantined": run.quarantined,
        "failures": run.failure_details or [],
        "last_error": run.last_error,
    }


@router.get("/emails/{email_id}/local-explanation")
def get_local_explanation(email_id: str, db: Session = Depends(get_db)):
    explanation = data_service.get_local_explanation_by_email_id(db, email_id)
    if explanation:
        return {
            "id": explanation.id,
            "email_id": explanation.email_id,
            "prediction_id": explanation.prediction_id,
            "explainer_type": explanation.explainer_type,
            "model_version": explanation.model_version,
            "human_summary": explanation.human_summary,
            "top_features": explanation.top_features,
            "pipeline_status": explanation.pipeline_status,
            "created_at": explanation.created_at,
        }
    email = data_service.get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    result = model_manager.predict_email(
        {
            "subject": email.subject,
            "body": email.body or email.body_preview or "",
            "sender": email.sender,
            "reply_to": email.reply_to,
            "urls": email.urls or [],
            "attachments": email.attachments or [],
            "url_count": email.url_count,
            "has_links": email.has_links,
            "has_attachment": email.has_attachment,
            "attachment_count": email.attachment_count,
        }
    )
    details = result.get("explanation", {})
    return {
        "email_id": email_id,
        "explainer_type": result.get("surrogate_model_name", "EBM surrogate"),
        "model_version": result.get("explanation_version"),
        "human_summary": " ".join(details.get("top_reasons", [])),
        "top_features": details.get("raw_feature_contributions", []),
        "pipeline_status": result.get("pipeline_status"),
        "uncertainty_notice": details.get("uncertainty_notice"),
    }


@router.get("/global-explanation")
@router.get("/api/global-explanation")
def get_global_explanation():
    return model_manager.get_global_explanation()


@router.get("/feedback", response_model=List[FeedbackSchema])
def get_feedback(
    source: str | None = Query(None, pattern="^(gmail|mock|all)$"),
    db: Session = Depends(get_db),
):
    return data_service.get_feedback_cases(db, source=_live_source(source))


@router.post("/emails/{email_id}/feedback")
def submit_feedback(email_id: str, payload: FeedbackCreateSchema, db: Session = Depends(get_db)):
    if not data_service.get_email_by_id(db, email_id):
        raise HTTPException(status_code=404, detail="Email not found")
    feedback = data_service.create_feedback_case(
        db,
        email_id=email_id,
        feedback_type=payload.feedback_type,
        user_comment=payload.user_comment,
        submitted_by=payload.submitted_by,
    )
    data_service.create_audit_event(
        db,
        actor=payload.submitted_by or "user",
        action_type="user_feedback_submitted",
        email_id=email_id,
        new_state={"feedback_id": feedback.id, "review_status": feedback.review_status},
    )
    return {"feedback_id": feedback.id, "email_id": feedback.email_id, "review_status": feedback.review_status}


@router.patch("/feedback/{feedback_id}/review")
def review_feedback(feedback_id: str, payload: FeedbackReviewSchema, db: Session = Depends(get_db)):
    feedback = data_service.get_feedback_by_id(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    previous_review_status = feedback.review_status
    if payload.review_status not in {"confirmed", "rejected"}:
        raise HTTPException(status_code=400, detail="Analyst review status must be confirmed or rejected.")
    derived = payload.error_type
    if not derived and payload.analyst_label and feedback.original_prediction:
        labels = {
            ("phishing", "legitimate"): "false_positive",
            ("legitimate", "phishing"): "false_negative",
            ("phishing", "phishing"): "true_positive",
            ("legitimate", "legitimate"): "true_negative",
        }
        derived = labels.get((feedback.original_prediction, payload.analyst_label))
    reviewed = data_service.review_feedback_case(
        db,
        feedback_id=feedback_id,
        analyst_label=payload.analyst_label,
        error_type=derived,
        reason_category=payload.reason_category,
        review_status=payload.review_status,
        actor=payload.actor,
    )
    data_service.create_audit_event(
        db,
        actor=payload.actor,
        action_type="analyst_feedback_review",
        email_id=feedback.email_id,
        previous_state={"review_status": previous_review_status},
        new_state={"review_status": reviewed.review_status, "error_type": reviewed.error_type},
    )
    return {"status": "success", "feedback_id": feedback_id, "updated": reviewed.id}


def _mailbox_action(
    db: Session, email_id: str, payload: MailboxActionSchema | None, action: str
) -> dict[str, Any]:
    email = data_service.get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    desired = "quarantined" if action == "quarantine" else "released"
    if email.quarantine_status == desired:
        return {"status": "success", "action": desired, "email_id": email_id, "changed": False}
    request = payload or MailboxActionSchema()
    provider = get_mailbox_provider(request.provider or email.mailbox_source)
    operation = provider.quarantine_message if action == "quarantine" else provider.release_message
    if email.mailbox_message_id and not operation(email.mailbox_message_id):
        raise HTTPException(status_code=409, detail=f"Mailbox {action} action could not be completed.")
    previous = {"quarantine_status": email.quarantine_status}
    updated = data_service.update_email_status(db, email_id, desired, "quarantine_status")
    prediction = data_service.get_prediction_by_email_id(db, email_id)
    explanation = data_service.get_local_explanation_by_email_id(db, email_id)
    data_service.create_audit_event(
        db,
        actor=request.actor,
        action_type=action,
        email_id=email_id,
        previous_state=previous,
        new_state={"quarantine_status": desired},
        reason=request.reason,
        model_version=prediction.model_version if prediction else None,
        explanation_version=explanation.model_version if explanation else None,
        explanation_snapshot_id=explanation.snapshot_id if explanation else None,
    )
    return {"status": "success", "action": desired, "email_id": updated.id, "changed": True}


@router.post("/emails/{email_id}/quarantine")
def quarantine_email(
    email_id: str, payload: MailboxActionSchema | None = None, db: Session = Depends(get_db)
):
    return _mailbox_action(db, email_id, payload, "quarantine")


@router.post("/emails/{email_id}/release")
def release_email(
    email_id: str, payload: MailboxActionSchema | None = None, db: Session = Depends(get_db)
):
    return _mailbox_action(db, email_id, payload, "release")


@router.get("/audit")
def get_audit_log(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    rows = data_service.get_audit_events(db, limit=limit)
    return {
        "items": [
            {
                "id": row.id,
                "email_id": row.email_id,
                "actor": row.actor,
                "action_type": row.action_type,
                "previous_state": row.previous_state,
                "new_state": row.new_state,
                "reason": row.reason,
                "model_version": row.model_version,
                "explanation_version": row.explanation_version,
                "explanation_snapshot_id": row.explanation_snapshot_id,
                "timestamp": row.created_at,
            }
            for row in rows
        ]
    }


@router.get("/monitoring/model-health")
def get_model_health(
    source: str | None = Query(None, pattern="^(gmail|mock|all)$"),
    db: Session = Depends(get_db),
):
    selected_source = _live_source(source)
    active = model_manager.get_active_model_config()
    live = data_service.get_live_metrics(db, source=selected_source)
    confirmed = live["confirmed_feedback"]
    validation_message = (
        "Not enough confirmed feedback yet."
        if confirmed < 10
        else "Live validation is based only on analyst-confirmed feedback."
    )
    benchmark = {
        "label": "Research Benchmark Metrics",
        "accuracy_fidelity": 0.926,
        "f1_fidelity": 0.928,
        "error_fidelity": 0.7673,
        "notice": "These fixed fidelity results are benchmark metrics, not live Gmail accuracy.",
    }
    return {
        "model_name": active["teacher_model_name"],
        "model_version": active["teacher_model_id"],
        "surrogate_name": active["surrogate_model_name"],
        "surrogate_version": active["surrogate_model_id"],
        "mailbox_source": selected_source,
        "research_benchmark": benchmark,
        "live_operational": {**live, "validation_message": validation_message},
        "model_readiness": model_manager.get_readiness(),
        **live,
        "accuracy_fidelity": benchmark["accuracy_fidelity"],
        "f1_fidelity": benchmark["f1_fidelity"],
        "error_fidelity": benchmark["error_fidelity"],
        "validation_message": validation_message,
    }


@router.get("/monitoring/model-versions")
def get_model_versions():
    registry = model_manager.get_registry_payload()
    active = model_manager.get_active_model_config()
    items = []
    for config in registry["teachers"] + registry["surrogates"]:
        kind = config["type"]
        items.append(
            {
                "id": config["id"],
                "name": config["display_name"],
                "version": config["id"],
                "type": kind,
                "is_active": config["id"]
                == active["teacher_model_id" if kind == "teacher" else "surrogate_model_id"],
            }
        )
    return {"items": items}


@router.get("/monitoring/fidelity")
def get_monitoring_fidelity():
    return {
        "metric_source": "research_benchmark",
        "notice": "Benchmark surrogate fidelity metrics; not live Gmail performance.",
        "accuracy_fidelity": 0.926,
        "f1_fidelity": 0.928,
        "error_fidelity": 0.7673,
    }


@router.post("/feedback/export-confirmed")
def export_confirmed_feedback():
    raise HTTPException(
        status_code=409,
        detail="Retraining-data export is disabled in this prototype. Confirmed feedback remains visible in monitoring.",
    )

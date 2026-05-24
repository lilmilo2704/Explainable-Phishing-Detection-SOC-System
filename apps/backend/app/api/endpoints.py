from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.services import data_service
from app.database import get_db
from app.schemas import (
    EmailListSchema,
    EmailDetailSchema,
    ExplanationSchema,
    FeedbackSchema,
    FeedbackCreateSchema,
    FeedbackReviewSchema,
    MailboxSyncRequestSchema,
    MailboxSyncResponseSchema,
    ActiveModelConfigRequestSchema,
)
import logging
from pathlib import Path
from app.services.mailbox_integration import get_mailbox_provider
from app.services.mailbox_sync_service import perform_mailbox_sync
from app.services.model_manager import ModelManagerError, model_manager

logger = logging.getLogger(__name__)

# ML service availability flag
ML_AVAILABLE = True

router = APIRouter()


def _scan_email_with_manager(payload: Dict[Any, Any]) -> Dict[str, Any]:
    result = model_manager.predict_email(payload)
    result["email_id"] = payload.get("email_id", "scan_new")
    result["local_explanation_available"] = not result.get("explanation", {}).get("model_failed", False)
    return result

@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    emails = data_service.get_emails(db)
    active = model_manager.get_active_model_config()

    total_scanned = len(emails)
    quarantined = sum(1 for e in emails if e.quarantine_status == "quarantined")
    pending_review = sum(1 for e in emails if e.review_status in ["new", "in_review"])

    # Use latest prediction snapshot per email to avoid double-counting historical scans.
    latest_predictions = [
        data_service.get_prediction_by_email_id(db, email.id) for email in emails
    ]
    latest_predictions = [p for p in latest_predictions if p is not None]
    phishing_detected = sum(1 for p in latest_predictions if p.prediction == "phishing")

    feedback_counts = data_service.get_feedback_monitoring_counts(db)
    return {
        "time_range": "24h",
        "emails_scanned": total_scanned,
        "phishing_detected": phishing_detected,
        "quarantined": quarantined,
        "pending_review": pending_review,
        "false_positive_reports": feedback_counts["false_positives"],
        "false_negative_reports": feedback_counts["false_negatives"],
        "average_confidence": 0.94,
        "high_risk_cases": sum(
            1 for p in latest_predictions if p.risk_level in ["high", "critical"]
        ),
        "current_model": {"name": active["teacher_model_name"], "version": active["teacher_model_id"]},
        "current_surrogate": {"name": active["surrogate_model_name"], "version": active["surrogate_model_id"]},
    }

@router.get("/emails", response_model=Dict[str, Any])
def list_emails(db: Session = Depends(get_db)):
    emails = data_service.get_emails(db)
    
    result = []
    for email in emails:
        pred = data_service.get_prediction_by_email_id(db, email.id)
        email_data = {
            "id": email.id,
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
            "prediction": pred.prediction if pred else None,
            "confidence": pred.confidence if pred else None,
            "risk_level": pred.risk_level if pred else None,
            "teacher_model_id": pred.teacher_model_id if pred else None,
            "surrogate_model_id": pred.surrogate_model_id if pred else None,
            "model_version": pred.model_version if pred else None,
        }
        result.append(email_data)
        
    return {"items": result, "page": 1, "page_size": 25, "total": len(result)}

@router.get("/emails/{email_id}", response_model=EmailDetailSchema)
def get_email_detail(email_id: str, db: Session = Depends(get_db)):
    email = data_service.get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
        
    pred = data_service.get_prediction_by_email_id(db, email_id)
    
    result = email.__dict__.copy()
    if pred:
        result["prediction_details"] = pred
    return result

@router.post("/scan-email")
def scan_email(payload: Dict[Any, Any], db: Session = Depends(get_db)):
    try:
        result = _scan_email_with_manager(payload)
        email_id = payload.get("email_id")
        if email_id and data_service.get_email_by_id(db, email_id):
            pred = data_service.create_prediction_snapshot(db, email_id, result)
            explanation = result.get("explanation", {})
            data_service.create_explanation_snapshot(
                db,
                email_id=email_id,
                prediction_id=pred.id,
                explanation={
                    "explainer_type": result.get("surrogate_model_name", "Surrogate"),
                    "human_summary": "; ".join(explanation.get("top_reasons", [])[:3]) if explanation.get("top_reasons") else "model failed",
                    "top_features": explanation.get("raw_feature_contributions", []),
                },
                model_version=result.get("surrogate_model_id", result.get("model_version", "unknown")),
            )
        return result
    except ModelManagerError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"/scan-email error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/api/scan-email")
def scan_email_api(payload: Dict[Any, Any], db: Session = Depends(get_db)):
    return scan_email(payload, db)


@router.get("/api/models")
def get_models_registry():
    return model_manager.get_registry_payload()


@router.get("/api/models/active")
def get_active_models():
    return model_manager.get_active_model_config()


@router.post("/api/models/active")
def set_active_models(payload: ActiveModelConfigRequestSchema):
    try:
        return model_manager.set_active_model_config(
            teacher_model_id=payload.teacher_model_id,
            surrogate_model_id=payload.surrogate_model_id,
        )
    except ModelManagerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/mailbox/providers")
def get_mailbox_providers():
    return {
        "items": [
            {"name": "mock", "status": "ready"},
            {"name": "gmail", "status": "scaffolded_waiting_credentials"},
        ]
    }


@router.post("/mailbox/sync", response_model=MailboxSyncResponseSchema)
def sync_mailbox(payload: MailboxSyncRequestSchema, db: Session = Depends(get_db)):
    try:
        result = perform_mailbox_sync(db, provider_name=payload.provider, limit=payload.limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Mailbox sync failed: {e}")
    return result


@router.post("/scan-batch")
def scan_batch(payload: Dict[Any, Any], db: Session = Depends(get_db)):
    emails = payload.get("emails", [])
    if not isinstance(emails, list):
        raise HTTPException(status_code=400, detail="emails must be a list")
    items = []
    for item in emails:
        try:
            items.append(scan_email(item, db))
        except Exception as e:
            items.append({"error": str(e), "email_id": item.get("email_id")})
    return {"items": items, "total": len(items)}

@router.get("/emails/{email_id}/local-explanation")
def get_local_explanation(email_id: str, db: Session = Depends(get_db)):
    # Try DB first (for seeded/scanned emails with stored explanations)
    exp = data_service.get_local_explanation_by_email_id(db, email_id)
    if exp:
        return {
            "id": exp.id,
            "email_id": exp.email_id,
            "prediction_id": exp.prediction_id,
            "explainer_type": exp.explainer_type,
            "model_version": exp.model_version,
            "human_summary": exp.human_summary,
            "top_features": exp.top_features,
            "created_at": exp.created_at,
        }

    # Fall back to generating dynamically from ML service
    if ML_AVAILABLE:
        email = data_service.get_email_by_id(db, email_id)
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        email_dict = {
            "subject": email.subject,
            "body": "",  # body_preview only; full body not stored
            "sender_email": email.sender,
            "reply_to": email.reply_to,
            "urls": [],
            "attachments": [],
            "url_count": email.url_count,
            "has_links": email.has_links,
            "has_attachment": email.has_attachment,
            "attachment_count": email.attachment_count,
        }
        try:
            scan_result = model_manager.predict_email(email_dict)
            explanation = scan_result.get("explanation", {})
            return {
                "email_id": email_id,
                "explainer_type": scan_result.get("surrogate_model_name", "Surrogate"),
                "model_version": scan_result.get("surrogate_model_id"),
                "human_summary": "; ".join(explanation.get("top_reasons", [])[:3]) if explanation.get("top_reasons") else "model failed",
                "top_features": explanation.get("raw_feature_contributions", []),
                "model_failed": explanation.get("model_failed", False),
            }
        except Exception as e:
            logger.error(f"Dynamic explanation failed for {email_id}: {e}")

    raise HTTPException(status_code=404, detail="Local explanation not found")

@router.get("/global-explanation")
def get_global_explanation():
    try:
        return model_manager.get_global_explanation()
    except Exception as e:
        logger.error(f"Global explanation error: {e}")
        active = model_manager.get_active_model_config()
        return {
            "model_failed": True,
            "message": "model failed",
            "model_name": active["teacher_model_name"],
            "model_version": active["teacher_model_id"],
            "surrogate_name": active["surrogate_model_name"],
            "surrogate_version": active["surrogate_model_id"],
            "accuracy_fidelity": 0.0,
            "f1_fidelity": 0.0,
            "error_fidelity": 0.0,
            "top_features": [],
            "failure_patterns": {
                "false_positives": ["model failed"],
                "false_negatives": ["model failed"],
            },
            "generated_at": "2026-05-19T00:00:00Z",
        }


@router.get("/api/global-explanation")
def get_global_explanation_api():
    return get_global_explanation()

@router.get("/feedback", response_model=List[FeedbackSchema])
def get_feedback(db: Session = Depends(get_db)):
    return data_service.get_feedback_cases(db)

@router.post("/emails/{email_id}/feedback")
def submit_feedback(email_id: str, payload: FeedbackCreateSchema, db: Session = Depends(get_db)):
    email = data_service.get_email_by_id(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    feedback = data_service.create_feedback_case(
        db,
        email_id=email_id,
        feedback_type=payload.feedback_type,
        user_comment=payload.user_comment,
        submitted_by=payload.submitted_by,
    )
    return {
        "feedback_id": feedback.id,
        "email_id": feedback.email_id,
        "review_status": feedback.review_status,
    }


@router.patch("/feedback/{feedback_id}/review")
def review_feedback(feedback_id: str, payload: FeedbackReviewSchema, db: Session = Depends(get_db)):
    feedback = data_service.get_feedback_by_id(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    original_pred = feedback.original_prediction
    derived_error_type = payload.error_type
    if not derived_error_type and payload.analyst_label and original_pred:
        if original_pred == "phishing" and payload.analyst_label == "legitimate":
            derived_error_type = "false_positive"
        elif original_pred == "legitimate" and payload.analyst_label == "phishing":
            derived_error_type = "false_negative"
        elif original_pred == "phishing" and payload.analyst_label == "phishing":
            derived_error_type = "true_positive"
        elif original_pred == "legitimate" and payload.analyst_label == "legitimate":
            derived_error_type = "true_negative"

    reviewed = data_service.review_feedback_case(
        db,
        feedback_id=feedback_id,
        analyst_label=payload.analyst_label,
        error_type=derived_error_type,
        reason_category=payload.reason_category,
        review_status=payload.review_status,
        added_to_improvement_dataset=payload.added_to_improvement_dataset,
    )
    return {"status": "success", "feedback_id": feedback_id, "updated": reviewed.id}

@router.post("/emails/{email_id}/quarantine")
def quarantine_email(email_id: str, payload: Dict[Any, Any] | None = None, db: Session = Depends(get_db)):
    updated_email = data_service.update_email_status(db, email_id, "quarantined", "quarantine_status")
    if not updated_email:
        raise HTTPException(status_code=404, detail="Email not found")
    provider_name = (payload or {}).get("provider", "mock")
    if updated_email.mailbox_message_id:
        try:
            provider = get_mailbox_provider(provider_name)
            provider.quarantine_message(updated_email.mailbox_message_id)
        except Exception:
            logger.warning("Mailbox provider quarantine action failed for %s", updated_email.mailbox_message_id)
    return {"status": "success", "action": "quarantined", "email_id": email_id}

@router.post("/emails/{email_id}/release")
def release_email(email_id: str, payload: Dict[Any, Any] | None = None, db: Session = Depends(get_db)):
    updated_email = data_service.update_email_status(db, email_id, "released", "quarantine_status")
    if not updated_email:
        raise HTTPException(status_code=404, detail="Email not found")
    provider_name = (payload or {}).get("provider", "mock")
    if updated_email.mailbox_message_id:
        try:
            provider = get_mailbox_provider(provider_name)
            provider.release_message(updated_email.mailbox_message_id)
        except Exception:
            logger.warning("Mailbox provider release action failed for %s", updated_email.mailbox_message_id)
    return {"status": "success", "action": "released", "email_id": email_id}

@router.get("/monitoring/model-health")
def get_model_health(db: Session = Depends(get_db)):
    feedback_counts = data_service.get_feedback_monitoring_counts(db)
    return {
        "accuracy": 0.95,
        "precision": 0.92,
        "recall": 0.94,
        "f1_score": 0.93,
        "accuracy_fidelity": 0.926,
        "f1_fidelity": 0.928,
        "error_fidelity": 0.7673,
        **feedback_counts,
    }


@router.get("/monitoring/model-versions")
def get_model_versions():
    registry = model_manager.get_registry_payload()
    active = model_manager.get_active_model_config()
    items = []
    for t in registry["teachers"]:
        items.append(
            {
                "id": t["id"],
                "name": t["display_name"],
                "version": t["id"],
                "type": "teacher",
                "is_active": t["id"] == active["teacher_model_id"],
            }
        )
    for s in registry["surrogates"]:
        items.append(
            {
                "id": s["id"],
                "name": s["display_name"],
                "version": s["id"],
                "type": "surrogate",
                "is_active": s["id"] == active["surrogate_model_id"],
            }
        )
    return {
        "items": items
    }


@router.get("/monitoring/fidelity")
def get_monitoring_fidelity():
    return {
        "accuracy_fidelity": 0.926,
        "f1_fidelity": 0.928,
        "error_fidelity": 0.7673,
    }


@router.post("/feedback/export-confirmed")
def export_confirmed_feedback(db: Session = Depends(get_db)):
    root = Path(__file__).resolve().parents[4]
    export_dir = root / "data" / "exports"
    export_path = data_service.export_confirmed_feedback_for_improvement(db, export_dir=export_dir)
    return {
        "status": "success",
        "export_path": str(export_path),
        "format": "json",
    }

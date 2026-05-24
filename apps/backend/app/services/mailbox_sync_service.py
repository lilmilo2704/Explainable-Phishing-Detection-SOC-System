from __future__ import annotations

from datetime import datetime
from typing import Any
from email.utils import parsedate_to_datetime

from sqlalchemy.orm import Session

from app.services import data_service
from app.services.mailbox_integration import get_mailbox_provider
from app.services.model_manager import ModelManagerError, model_manager


def _normalize_mailbox_email(raw: dict[str, Any]) -> dict[str, Any]:
    received_at = raw.get("received_at")
    if isinstance(received_at, str):
        try:
            received_at = datetime.fromisoformat(received_at.replace("Z", "+00:00"))
        except Exception:
            try:
                received_at = parsedate_to_datetime(received_at)
            except Exception:
                received_at = None
    return {
        "id": raw.get("id"),
        "mailbox_message_id": raw.get("mailbox_message_id"),
        "subject": raw.get("subject"),
        "sender": raw.get("sender"),
        "sender_domain": raw.get("sender_domain"),
        "recipient": raw.get("recipient"),
        "reply_to": raw.get("reply_to"),
        "received_at": received_at,
        "body_preview": raw.get("body_preview"),
        "url_count": raw.get("url_count", 0),
        "attachment_count": raw.get("attachment_count", 0),
        "has_links": raw.get("has_links", False),
        "has_attachment": raw.get("has_attachment", False),
        "quarantine_status": raw.get("quarantine_status", "allowed"),
        "review_status": raw.get("review_status", "none"),
    }


def perform_mailbox_sync(db: Session, provider_name: str, limit: int = 25) -> dict[str, Any]:
    provider = get_mailbox_provider(provider_name)
    mailbox_messages = provider.fetch_messages(limit=limit)

    items = []
    quarantined = 0
    for raw in mailbox_messages:
        email_db = data_service.upsert_email_from_mailbox(db, _normalize_mailbox_email(raw))
        scan_payload = {
            "email_id": email_db.id,
            "subject": email_db.subject or "",
            "body": email_db.body_preview or "",
            "sender": email_db.sender or "",
            "reply_to": email_db.reply_to or "",
            "urls": [],
            "attachments": [],
            "url_count": email_db.url_count,
            "attachment_count": email_db.attachment_count,
            "has_links": email_db.has_links,
            "has_attachment": email_db.has_attachment,
        }
        try:
            result = model_manager.predict_email(scan_payload)
        except (ModelManagerError, Exception):
            result = {
                "prediction": "legitimate",
                "confidence": 0.5,
                "risk_level": "low",
                "recommended_action": "allow",
                "model_name": "Random Forest",
                "model_version": "rf_v1",
                "teacher_model_id": "random_forest_v1",
                "surrogate_model_id": "ebm_random_forest_v1",
                "feature_extractor_version": "v1_292f",
                "explanation_snapshot": {"top_reasons": ["model failed"], "raw_feature_contributions": [], "model_failed": True},
            }

        pred = data_service.create_prediction_snapshot(db, email_db.id, result)
        explanation_payload = result.get("explanation", {})
        top_features = explanation_payload.get("raw_feature_contributions", [])
        summary = "; ".join(explanation_payload.get("top_reasons", [])[:3]) if explanation_payload.get("top_reasons") else "model failed"
        explanation = {
            "explainer_type": result.get("surrogate_model_name", "Surrogate"),
            "human_summary": summary,
            "top_features": top_features,
        }
        data_service.create_explanation_snapshot(
            db,
            email_id=email_db.id,
            prediction_id=pred.id,
            explanation=explanation,
            model_version=result.get("surrogate_model_id", pred.model_version),
        )

        if result.get("recommended_action") == "quarantine":
            data_service.update_email_status(db, email_db.id, "quarantined", "quarantine_status")
            if email_db.mailbox_message_id:
                try:
                    provider.quarantine_message(email_db.mailbox_message_id)
                except Exception:
                    pass
            quarantined += 1

        items.append(
            {
                "email_id": email_db.id,
                "mailbox_message_id": email_db.mailbox_message_id,
                "prediction": pred.prediction,
                "confidence": pred.confidence,
                "risk_level": pred.risk_level,
                "recommended_action": pred.recommended_action,
                "model_version": pred.model_version,
            }
        )

    return {
        "provider": provider.provider_name,
        "imported": len(items),
        "quarantined": quarantined,
        "items": items,
    }

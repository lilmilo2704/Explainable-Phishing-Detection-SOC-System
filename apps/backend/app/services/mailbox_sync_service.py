from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

from sqlalchemy.orm import Session

from app.services import data_service
from app.services.mailbox_integration import get_mailbox_provider
from app.services.model_manager import model_manager


_TRUE_ENV_VALUES = {"1", "true", "yes", "on"}
_FALSE_ENV_VALUES = {"0", "false", "no", "off"}


def _automatic_quarantine_allowed(provider_name: str) -> bool:
    if provider_name != "gmail":
        return True
    live_actions_enabled = (
        os.getenv("ALLOW_LIVE_GMAIL_ACTIONS", "false").strip().lower()
        in _TRUE_ENV_VALUES
    )
    shadow_mode_explicitly_disabled = (
        os.getenv("SHADOW_MODE", "true").strip().lower()
        in _FALSE_ENV_VALUES
    )
    return live_actions_enabled and shadow_mode_explicitly_disabled


def _normalize_mailbox_email(raw: dict[str, Any], provider_name: str) -> dict[str, Any]:
    received_at = raw.get("received_at")
    if isinstance(received_at, str):
        try:
            received_at = datetime.fromisoformat(received_at.replace("Z", "+00:00"))
        except ValueError:
            try:
                received_at = parsedate_to_datetime(received_at)
            except (TypeError, ValueError):
                received_at = None
    body = raw.get("body") or raw.get("body_preview") or ""
    urls = raw.get("urls") or []
    attachments = raw.get("attachments") or []
    fingerprint = raw.get("content_fingerprint") or hashlib.sha256(
        json.dumps(
            {
                "subject": raw.get("subject"),
                "sender": raw.get("sender"),
                "reply_to": raw.get("reply_to"),
                "body": body,
                "urls": urls,
            },
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    return {
        "id": raw.get("id"),
        "mailbox_source": provider_name,
        "mailbox_message_id": raw.get("mailbox_message_id") or raw.get("id"),
        "subject": raw.get("subject"),
        "sender": raw.get("sender"),
        "sender_domain": raw.get("sender_domain"),
        "recipient": raw.get("recipient"),
        "reply_to": raw.get("reply_to"),
        "received_at": received_at,
        "body_preview": raw.get("body_preview") or body[:400],
        "body": body,
        "urls": urls,
        "attachments": attachments,
        "content_fingerprint": fingerprint,
        "url_count": raw.get("url_count", len(urls)),
        "attachment_count": raw.get("attachment_count", len(attachments)),
        "has_links": raw.get("has_links", bool(urls)),
        "has_attachment": raw.get("has_attachment", bool(attachments)),
        "quarantine_status": raw.get("quarantine_status", "allowed"),
        "review_status": raw.get("review_status", "none"),
    }


def _scan_payload(email: Any) -> dict[str, Any]:
    attachment_names = [
        item.get("filename", "") if isinstance(item, dict) else str(item)
        for item in (email.attachments or [])
    ]
    return {
        "email_id": email.id,
        "subject": email.subject or "",
        "body": email.body or email.body_preview or "",
        "sender": email.sender or "",
        "reply_to": email.reply_to or "",
        "urls": email.urls or [],
        "attachments": attachment_names,
        "url_count": email.url_count,
        "attachment_count": email.attachment_count,
        "has_links": email.has_links,
        "has_attachment": email.has_attachment,
    }


def _failure_result(message: str, content_fingerprint: str | None) -> dict[str, Any]:
    active = model_manager.get_active_model_config()
    explanation = {
        "top_reasons": ["The model failed during mailbox sync. This email requires analyst review."],
        "raw_feature_contributions": [],
        "model_failed": True,
        "pipeline_warning": message,
    }
    return {
        "prediction": "model_error",
        "confidence": 0.0,
        "risk_level": "unknown",
        "recommended_action": "review",
        "model_name": active["teacher_model_name"],
        "model_version": active["teacher_model_id"],
        "teacher_model_id": active["teacher_model_id"],
        "surrogate_model_id": active["surrogate_model_id"],
        "feature_extractor_version": "model_sync_failure",
        "explanation_version": active["surrogate_model_id"],
        "trusted_prediction": False,
        "pipeline_status": "model_error",
        "content_fingerprint": content_fingerprint,
        "explanation": explanation,
        "explanation_snapshot": explanation,
    }


def perform_mailbox_sync(
    db: Session,
    provider_name: str | None,
    limit: int = 25,
    *,
    force_rescan: bool = False,
    actor: str = "analyst",
) -> dict[str, Any]:
    provider = get_mailbox_provider(provider_name)
    sync_run = data_service.start_sync_run(db, provider.provider_name, actor)
    try:
        mailbox_messages = provider.fetch_messages(limit=limit)
    except Exception as exc:
        data_service.finish_sync_run(
            db, sync_run, status="failed", failed=1, last_error=str(exc), failure_details=[]
        )
        raise

    active = model_manager.get_active_model_config()
    items: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    skipped = 0
    quarantined = 0

    for raw in mailbox_messages:
        normalized = _normalize_mailbox_email(raw, provider.provider_name)
        existing = data_service.get_email_by_mailbox_message_id(
            db, provider.provider_name, normalized["mailbox_message_id"]
        )
        previous_prediction = data_service.get_prediction_by_email_id(db, existing.id) if existing else None
        unchanged = existing and existing.content_fingerprint == normalized["content_fingerprint"]
        same_model = (
            previous_prediction
            and previous_prediction.teacher_model_id == active["teacher_model_id"]
            and previous_prediction.surrogate_model_id == active["surrogate_model_id"]
        )
        if unchanged and same_model and not force_rescan:
            skipped += 1
            continue

        email = data_service.upsert_email_from_mailbox(db, normalized)
        try:
            result = model_manager.predict_email(_scan_payload(email))
            result["content_fingerprint"] = normalized["content_fingerprint"]
        except Exception as exc:
            reason = "Model failed during mailbox sync; analyst review is required."
            result = _failure_result(reason, normalized["content_fingerprint"])
            failures.append({"email_id": email.id, "subject": (email.subject or "")[:120], "error": reason})
            data_service.mark_email_scan_result(db, email, status="model_error", model_error=str(exc)[:250])
        else:
            status = "scanned" if result.get("trusted_prediction") else "needs_review"
            data_service.mark_email_scan_result(db, email, status=status)

        prediction = data_service.create_prediction_snapshot(db, email.id, result)
        explanation_data = result.get("explanation", {})
        explanation = data_service.create_explanation_snapshot(
            db,
            email_id=email.id,
            prediction_id=prediction.id,
            explanation={
                "explainer_type": result.get("surrogate_model_name", "EBM surrogate"),
                "human_summary": " ".join(explanation_data.get("top_reasons", [])),
                "top_features": explanation_data.get("raw_feature_contributions", []),
                "pipeline_status": result.get("pipeline_status"),
            },
            model_version=result.get("explanation_version", prediction.model_version),
        )

        if result.get("trusted_prediction") and result.get("recommended_action") == "quarantine":
            if email.review_status in {"none", "new"}:
                data_service.update_email_status(db, email.id, "in_review", "review_status")
            previous_state = {"quarantine_status": email.quarantine_status}
            analyst_override = (
                email.quarantine_status == "released"
                or data_service.has_confirmed_legitimate_feedback(db, email.id)
            )
            if analyst_override:
                data_service.create_audit_event(
                    db,
                    email_id=email.id,
                    actor="system",
                    action_type="automatic_quarantine_suppressed",
                    previous_state=previous_state,
                    new_state={"quarantine_status": email.quarantine_status},
                    reason="Existing analyst release or confirmed legitimate classification.",
                    model_version=prediction.model_version,
                    explanation_version=explanation.model_version,
                    explanation_snapshot_id=explanation.snapshot_id,
                )
                provider_changed = False
            else:
                provider_changed = (
                    provider.quarantine_message(email.mailbox_message_id)
                    if _automatic_quarantine_allowed(provider.provider_name)
                    else False
                )
            if provider_changed:
                data_service.update_email_status(db, email.id, "quarantined", "quarantine_status")
                data_service.create_audit_event(
                    db,
                    email_id=email.id,
                    actor="system",
                    action_type="automatic_quarantine",
                    previous_state=previous_state,
                    new_state={"quarantine_status": "quarantined"},
                    reason="Trusted high-risk model policy.",
                    model_version=prediction.model_version,
                    explanation_version=explanation.model_version,
                    explanation_snapshot_id=explanation.snapshot_id,
                )
                quarantined += 1

        items.append(
            {
                "email_id": email.id,
                "mailbox_message_id": email.mailbox_message_id,
                "prediction": prediction.prediction,
                "confidence": prediction.confidence,
                "risk_level": prediction.risk_level,
                "recommended_action": prediction.recommended_action,
                "model_version": prediction.model_version,
                "trusted_prediction": prediction.trusted_prediction,
                "pipeline_status": prediction.pipeline_status,
            }
        )

    status = "partial_failure" if failures else "success"
    completed = data_service.finish_sync_run(
        db,
        sync_run,
        status=status,
        scanned=len(items),
        skipped=skipped,
        failed=len(failures),
        quarantined=quarantined,
        failure_details=failures,
        last_error=failures[0]["error"] if failures else None,
    )
    return {
        "provider": provider.provider_name,
        "status": status,
        "imported": len(items),
        "scanned": len(items),
        "skipped": skipped,
        "failed": len(failures),
        "quarantined": quarantined,
        "failures": failures,
        "last_sync_time": completed.completed_at,
        "items": items,
    }

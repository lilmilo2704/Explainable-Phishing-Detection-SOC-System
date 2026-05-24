# API Contracts

## Purpose

This document defines the API contract between the frontend dashboard, backend API, mailbox service, and model integration service.

The API should support a SOC-friendly phishing detection dashboard that can:

- display scanned emails
- show phishing/legitimate predictions
- show confidence and risk level
- show quarantine/release status
- show local explanations for individual emails
- show global explanations of model behaviour
- support analyst feedback review
- support model monitoring and governance

For the live Gmail prototype, these APIs store local operational state after manually initiated Gmail sync. Mock/sample data remains available for testing.

---

## API Design Principles

1. Keep API responses dashboard-ready.
2. Every prediction must include model name and model version.
3. Every explanation must include an explanation snapshot ID or timestamp.
4. Do not expose full raw email bodies unless explicitly needed.
5. Do not expose mailbox credentials, OAuth tokens, or secrets.
6. Quarantine actions must be reversible.
7. User feedback must not trigger automatic model retraining.
8. Local explanations must include human-readable text, not only raw numerical values.
9. Global explanations must include fidelity and error-fidelity metrics where available.

---

## Core Entities

### Email

Represents an email scanned by the system.

```json
{
  "id": "email_001",
  "mailbox_message_id": "msg_abc123",
  "subject": "Urgent invoice payment required",
  "sender": "billing-support@example-security.com",
  "sender_domain": "example-security.com",
  "recipient": "employee@company.com",
  "reply_to": "accounts.payments@gmail.com",
  "received_at": "2026-05-19T10:42:00Z",
  "body_preview": "Please review and pay the attached invoice...",
  "url_count": 3,
  "attachment_count": 1,
  "has_links": true,
  "has_attachment": true,
  "quarantine_status": "quarantined",
  "review_status": "new"
}
```

### Prediction

Represents the phishing detection model output for an email.

```json
{
  "id": "pred_001",
  "email_id": "email_001",
  "prediction": "phishing",
  "confidence": 0.94,
  "risk_level": "high",
  "recommended_action": "quarantine",
  "model_name": "Random Forest",
  "model_version": "rf_v1",
  "created_at": "2026-05-19T10:42:05Z"
}
```

### Local Explanation

Represents why a specific email was classified in a certain way.

```json
{
  "id": "exp_local_001",
  "email_id": "email_001",
  "prediction_id": "pred_001",
  "explainer_type": "SHAP",
  "model_version": "rf_v1",
  "human_summary": "This email was classified as phishing mainly because the reply-to address does not match the sender, the sender domain appears suspicious, and the email contains an unusually long URL.",
  "top_features": [
    {
      "feature": "sender_replyto_mismatch",
      "value": true,
      "contribution": 0.24,
      "direction": "increases_phishing_risk",
      "human_reason": "The reply-to address does not match the sender address."
    },
    {
      "feature": "max_url_length",
      "value": 148,
      "contribution": 0.18,
      "direction": "increases_phishing_risk",
      "human_reason": "The email contains an unusually long URL."
    }
  ],
  "created_at": "2026-05-19T10:42:06Z"
}
```

### Global Explanation

Represents model-level behaviour using global surrogate explanations.

```json
{
  "model_name": "Random Forest",
  "model_version": "rf_v1",
  "surrogate_name": "EBM",
  "surrogate_version": "ebm_rf_v1",
  "accuracy_fidelity": 0.926,
  "f1_fidelity": 0.928,
  "error_fidelity": 0.7673,
  "top_features": [
    {
      "feature": "max_url_length",
      "importance": 0.31,
      "human_summary": "Longer URLs generally increase phishing likelihood."
    },
    {
      "feature": "sender_replyto_mismatch",
      "importance": 0.24,
      "human_summary": "Reply-to mismatch is a strong phishing indicator."
    }
  ],
  "effect_plots": [
    {
      "feature": "max_url_length",
      "plot_path": "/static/explanations/ebm/max_url_length.png"
    }
  ]
}
```

### Feedback Case

Represents human-in-the-loop review of a prediction.

```json
{
  "id": "feedback_001",
  "email_id": "email_001",
  "prediction_id": "pred_001",
  "original_prediction": "phishing",
  "original_confidence": 0.94,
  "user_feedback": "This is a legitimate supplier invoice.",
  "analyst_label": "legitimate",
  "error_type": "false_positive",
  "reason_category": "legitimate business email with urgent wording",
  "review_status": "confirmed",
  "added_to_improvement_dataset": false,
  "created_at": "2026-05-19T11:10:00Z",
  "reviewed_at": "2026-05-19T11:25:00Z"
}
```

---

## Endpoint List

### Dashboard Summary

```http
GET /dashboard/summary
```

Returns overview metrics for the dashboard home page.

Response:

```json
{
  "time_range": "24h",
  "emails_scanned": 1248,
  "phishing_detected": 86,
  "quarantined": 42,
  "pending_review": 17,
  "false_positive_reports": 5,
  "false_negative_reports": 2,
  "average_confidence": 0.91,
  "high_risk_cases": 23,
  "current_model": {
    "name": "Random Forest",
    "version": "rf_v1"
  },
  "current_surrogate": {
    "name": "EBM",
    "version": "ebm_rf_v1"
  }
}
```

---

### List Emails

```http
GET /emails
```

For the live Gmail prototype, this endpoint defaults to the configured mailbox provider. When Gmail is configured, demo/mock records are hidden from the ordinary Detection Queue. Use `?source=mock` only for local fixture testing, or `?source=all` for administrative inspection.

Query parameters:

```text
prediction
risk_level
quarantine_status
review_status
sender_domain
has_links
has_attachment
date_from
date_to
search
page
page_size
```

Response:

```json
{
  "items": [
    {
      "id": "email_001",
      "subject": "Urgent invoice payment required",
      "sender": "billing-support@example-security.com",
      "received_at": "2026-05-19T10:42:00Z",
      "prediction": "phishing",
      "confidence": 0.94,
      "risk_level": "high",
      "quarantine_status": "quarantined",
      "review_status": "new",
      "explanation_summary": "Reply-to mismatch, suspicious sender domain, long URL"
    }
  ],
  "page": 1,
  "page_size": 25,
  "total": 86
}
```

---

### Get Email Detail

```http
GET /emails/{id}
```

Returns email metadata, prediction, investigation indicators, and current case status.

---

### Scan Email

```http
POST /scan-email
```

Request:

```json
{
  "subject": "Urgent invoice payment required",
  "sender": "billing-support@example-security.com",
  "recipient": "employee@company.com",
  "reply_to": "accounts.payments@gmail.com",
  "body": "Please review the invoice and pay today...",
  "urls": ["https://example-security.com/invoice/pay/123"],
  "attachments": [
    {
      "filename": "invoice.pdf",
      "mime_type": "application/pdf"
    }
  ]
}
```

Response:

```json
{
  "email_id": "email_001",
  "prediction": "phishing",
  "confidence": 0.94,
  "risk_level": "high",
  "recommended_action": "quarantine",
  "model_name": "Random Forest",
  "model_version": "rf_v1",
  "local_explanation_available": true
}
```

---

### Scan Batch

```http
POST /scan-batch
```

Used for mock mailbox import or batch mailbox scanning.

---

### Get Local Explanation

```http
GET /emails/{id}/local-explanation
```

Returns local explanation for one email.

---

### Get Global Explanation

```http
GET /global-explanation
```

Query parameters:

```text
teacher_model
surrogate_model
```

Example:

```http
GET /global-explanation?teacher_model=random_forest&surrogate_model=ebm
```

Returns global feature importance, effect plot paths, fidelity metrics, and failure-pattern summaries.

---

### Submit Feedback

```http
POST /emails/{id}/feedback
```

Request:

```json
{
  "feedback_type": "wrong_detection",
  "user_comment": "This email is legitimate.",
  "submitted_by": "employee@company.com"
}
```

Response:

```json
{
  "feedback_id": "feedback_001",
  "email_id": "email_001",
  "review_status": "pending"
}
```

---

### Review Feedback

```http
PATCH /feedback/{id}/review
```

Request:

```json
{
  "analyst_label": "legitimate",
  "error_type": "false_positive",
  "reason_category": "legitimate business email with urgent wording",
  "review_status": "confirmed",
  "added_to_improvement_dataset": false,
  "actor": "analyst"
}
```

---

### Quarantine Email

```http
POST /emails/{id}/quarantine
```

Moves or marks the email as quarantined/review-only.

---

### Release Email

```http
POST /emails/{id}/release
```

Releases the email from quarantine after analyst approval.

---

### Model Health

```http
GET /monitoring/model-health
```

Returns separate `research_benchmark` fidelity metrics and database-calculated `live_operational` counts. It must not present benchmark values as live Gmail accuracy.

---

### Model Readiness

```http
GET /monitoring/model-readiness
```

Reports whether teacher/surrogate artifacts, the fitted training preprocessor, and exact processed feature order are available for trusted live prediction. `feature_order_source: "fitted_surrogate_feature_names_in_"` indicates that the exact order was recovered and matched to the active surrogate, while `preprocessor_loaded: false` still blocks trusted live decisions. If unsafe, email scans are recorded as `needs_review` rather than silently treated as safe.

---

### Manual Gmail Sync Status

```http
GET /mailbox/sync-status
```

Returns the last manually initiated sync result, including scanned, skipped and failed message counts.

---

### Audit Log

```http
GET /audit
```

Returns quarantine, release, feedback-review, and model-switch audit entries with actor, state transition, model version, and explanation version references.

---

## Error Response Format

Use consistent error responses.

```json
{
  "error": {
    "code": "EMAIL_NOT_FOUND",
    "message": "The requested email could not be found.",
    "details": {}
  }
}
```

---

## MVP API Strategy

For the first MVP:

- use mock JSON data
- no real mailbox API yet
- no live retraining
- no full database required at the beginning
- return realistic dashboard-ready data from backend endpoints

The goal is to make the frontend, dashboard workflow, and API contract stable before connecting real model and mailbox services.

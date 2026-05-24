# Data Flow

## Purpose

This document explains how data moves through the explainable phishing detection system.

The system should support both an offline/mock MVP and a future real mailbox deployment.

---

## Main Data Flow

```text
Email Source
→ Mailbox Service
→ Backend API
→ Feature Extraction
→ Detection Model
→ Risk Decision
→ Local Explanation
→ Global Explanation Reference
→ Dashboard Display
→ Analyst Action
→ Feedback Storage
→ Future improvement datasetset
```

---

# 1. Email Ingestion Flow

## MVP Flow

```text
sample_emails.json / CSV
        ↓
Mock Mailbox Service
        ↓
Backend API
        ↓
Dashboard
```

## Future Real Mailbox Flow

```text
Gmail / Microsoft 365 mailbox
        ↓
Mailbox API
        ↓
Mailbox Service
        ↓
Normalized email object
        ↓
Backend API
```

## Normalized Email Object

The mailbox service should convert email provider data into a common format:

```json
{
  "mailbox_message_id": "msg_abc123",
  "subject": "Urgent invoice payment required",
  "sender": "billing-support@example-security.com",
  "recipient": "employee@company.com",
  "reply_to": "accounts.payments@gmail.com",
  "received_at": "2026-05-19T10:42:00Z",
  "body": "Please pay the invoice today...",
  "urls": ["https://example.com/invoice/pay"],
  "attachments": [
    {
      "filename": "invoice.pdf",
      "mime_type": "application/pdf"
    }
  ]
}
```

---

# 2. Feature Extraction Flow

The trained models do not understand raw emails directly.

The system must convert raw emails into the same feature format used during training.

```text
Raw email
→ clean text
→ extract sender features
→ extract URL features
→ extract text features
→ extract attachment features
→ encode/scale/impute
→ align feature columns
→ model-ready vector
```

Important:

```text
Feature order must match training.
Preprocessing must match training.
Missing-value handling must match training.
Categorical encoding must match training.
```

Suggested output:

```json
{
  "email_id": "email_001",
  "features": {
    "num_links": 3,
    "has_links": 1,
    "has_urgent_words": 1,
    "sender_replyto_mismatch": 1,
    "suspicious_sender_domain": 1,
    "max_url_length": 148,
    "max_url_path_depth": 5,
    "subject_length": 31,
    "body_length": 850
  },
  "feature_vector_version": "features_v1"
}
```

---

# 3. Prediction Flow

```text
Feature vector
        ↓
Teacher detection model
        ↓
Prediction label
        ↓
Confidence score
        ↓
Risk level
        ↓
Recommended action
```

Example output:

```json
{
  "email_id": "email_001",
  "prediction": "phishing",
  "confidence": 0.94,
  "risk_level": "high",
  "recommended_action": "quarantine",
  "model_name": "Random Forest",
  "model_version": "rf_v1"
}
```

---

# 4. Risk Decision Flow

Use confidence and model output to decide action.

Suggested MVP policy:

| Risk Level | Example Condition | Action |
|---|---|---|
| Low | confidence below threshold | Allow |
| Medium | suspicious but uncertain | Warn / flag |
| High | strong phishing confidence | Quarantine |
| Critical | very high confidence or dangerous indicators | Quarantine + notify analyst |

The product must not permanently delete emails.

---

# 5. Quarantine Flow

```text
High-risk prediction
        ↓
Backend decision engine
        ↓
Mailbox service
        ↓
Move to review/quarantine status
        ↓
Dashboard updates case
```

For MVP:

```text
quarantine_status = "quarantined"
```

For Gmail later:

```text
add label "Phishing Review"
optionally remove INBOX label
```

For Microsoft 365 later:

```text
move message to "Phishing Review" folder
```

---

# 6. Local Explanation Flow

```text
Prediction + feature vector
        ↓
Local explanation method
        ↓
Top contributing features
        ↓
Human-readable explanation
        ↓
Dashboard local explanation panel
```

Example:

```json
{
  "email_id": "email_001",
  "human_summary": "This email was classified as phishing mainly because the reply-to address does not match the sender and the email contains an unusually long URL.",
  "top_features": [
    {
      "feature": "sender_replyto_mismatch",
      "contribution": 0.24,
      "direction": "increases_phishing_risk",
      "human_reason": "The reply-to address does not match the sender address."
    }
  ]
}
```

---

# 7. Global Explanation Flow

Global explanations are model-level and do not need to be regenerated for every email.

```text
Existing EBM/GAMI-Net surrogate artifacts
        ↓
Global explanation loader
        ↓
Feature importance / effect plots / fidelity metrics
        ↓
Backend global explanation endpoint
        ↓
Dashboard global explanation page
```

Global explanation should show:

- global feature importance
- EBM/GAMI-Net effect plots
- feature interaction patterns
- accuracy fidelity
- F1 fidelity
- error fidelity
- false positive patterns
- false negative patterns

---

# 8. Feedback Flow

```text
User or analyst flags detection
        ↓
Feedback case created
        ↓
SOC analyst reviews
        ↓
Analyst confirms true label
        ↓
Case classified as TP/TN/FP/FN
        ↓
Confirmed case stored
        ↓
Optional future retraining export
```

Feedback type mapping:

| Model Prediction | Analyst Label | Case Type |
|---|---|---|
| phishing | phishing | true positive |
| legitimate | legitimate | true negative |
| phishing | legitimate | false positive |
| legitimate | phishing | false negative |

Important:

```text
Do not automatically retrain from user feedback.
Only analyst-confirmed feedback can be used for future retraining.
```

---

# 9. Model Monitoring Flow

```text
Predictions + feedback + explanation metrics
        ↓
Monitoring service
        ↓
Model health summary
        ↓
Dashboard model monitoring page
```

Show:

- current detector model
- current surrogate model
- model version
- detection metrics
- fidelity metrics
- error fidelity
- explanation latency
- feedback case count
- improvement readiness

---

## Data Storage Requirements

The system should eventually store:

```text
emails
predictions
local_explanations
global_explanations
feedback_cases
quarantine_actions
model_versions
audit_logs
```

---

## MVP Data Strategy

For first MVP, use:

```text
data/sample/sample_emails.json
data/sample/sample_predictions.json
data/sample/sample_local_explanations.json
data/sample/sample_global_explanations.json
data/sample/sample_feedback_cases.json
```

This allows frontend and backend development before full model and mailbox integration.

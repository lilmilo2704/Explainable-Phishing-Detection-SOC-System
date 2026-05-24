# PROJECT_CONTEXT.md

## 1. Project Identity

This project is an **AI-assisted, SOC-friendly explainable phishing detection and model-governance system with a dashboard for business mailboxes**.

The product is based on an existing research project titled:

> **Enhancing global explainability and reducing explanation latency in phishing email detection**

The original research investigated how phishing detection models can be made more transparent by using global surrogate explanation models. The coding goal is to turn that research foundation into a practical software product that can scan mailbox emails, classify phishing risk, quarantine suspicious emails, and explain model behaviour through a dashboard designed for SOC analysts, security managers, and model owners.

This system should not be treated as only a generic “AI phishing detector.” Its main value is:

> **Phishing detection + local explanation + global model behaviour analysis + false-positive/false-negative review + human-in-the-loop improvement.**

---

## 2. Product Vision

The final product should help an organisation understand, investigate, and improve phishing email detection.

The system should:

1. Connect to a mailbox or use a mock mailbox for the first MVP.
2. Read incoming or selected emails.
3. Extract phishing-relevant features from email content and metadata.
4. Classify each email as phishing or legitimate.
5. Assign a confidence score and risk level.
6. Quarantine, flag, warn, or allow emails based on risk.
7. Provide **local explanations** for individual email predictions.
8. Provide **global explanations** of model behaviour.
9. Allow users and SOC analysts to flag wrong detections.
10. Store analyst-confirmed false positives and false negatives.
11. Support controlled future retraining and model governance.

The final outcome should look like a serious security operations dashboard, not a toy demo or generic admin panel.

---

## 3. Existing Research Foundation

The current research/code resources already provide the ML/XAI foundation.

### 3.1 Detection Models

The project already has black-box phishing detection teacher models:

- Random Forest
- Deep Neural Network / MLPClassifier

These models are responsible for classifying an email as:

```text
phishing / legitimate
```

The research results showed strong phishing detection performance, especially for the Random Forest model.

### 3.2 Local Explanation Direction

The project includes or plans around local explanation methods such as:

- SHAP
- LIME

These are used to explain one specific prediction at a time.

Local explanation answers:

> Why was this specific email classified as phishing or legitimate?

This is mainly useful for SOC analysts reviewing individual suspicious emails.

### 3.3 Global Explanation Direction

The project includes global surrogate explanation models:

- EBM / Explainable Boosting Machine
- GAMI-Net

These surrogate models approximate the behaviour of black-box teacher models such as Random Forest and DNN.

Global explanation answers:

> What patterns does the phishing detection model generally rely on across many emails?

This is useful for:

- SOC managers
- security engineers
- ML/model owners
- risk/compliance teams
- model governance

### 3.4 Error Fidelity Contribution

The research introduced or used **Error Fidelity** as an important evaluation idea.

Normal fidelity checks whether the surrogate agrees with the teacher model overall.

Error Fidelity checks whether the surrogate agrees with the teacher model specifically on the teacher model's error cases.

This is important because a surrogate can look good overall but still fail to explain the model's mistakes.

For this product, Error Fidelity should support dashboard functionality such as:

- failure-behaviour analysis
- false-positive pattern analysis
- false-negative pattern analysis
- explanation reliability monitoring
- model-governance reporting

---

## 4. Product Positioning

The product should be described as:

> A SOC-friendly explainable phishing detection and model-governance dashboard for business mailboxes.

Do not describe it only as:

> An AI phishing detector.

The product is stronger than a normal phishing filter because it explains detections at two levels:

1. **Individual-email level**
   - Why this email was flagged.
   - Which features contributed to the prediction.
   - What indicators made the model suspicious.

2. **Model-behaviour level**
   - What the model generally relies on.
   - Which features increase or reduce phishing likelihood.
   - Where the model tends to fail.
   - Whether explanations are faithful enough to trust.

---

## 5. Target Users

The system has multiple user groups. Coding decisions should respect these different users.

### 5.1 Primary Users: SOC Analysts

SOC analysts are the main users of the dashboard.

They use the system to:

- review suspicious emails
- triage phishing detections
- inspect local explanations
- confirm whether an email is phishing or legitimate
- release false positives from quarantine
- escalate dangerous emails
- review user-reported wrong detections
- label false positives and false negatives

SOC analysts need a practical investigation workflow, not just charts.

### 5.2 Secondary Users: General Employees

General employees or mailbox users interact with the product only in a simple way.

They may:

- see a warning on a suspicious email
- report an email as phishing
- mark a quarantined or flagged email as safe
- send suspicious emails to the security team

They should not be expected to understand:

- SHAP
- LIME
- EBM
- GAMI-Net
- fidelity
- error fidelity
- machine learning details

For employees, explanations must be simple and human-readable.

### 5.3 Management and Governance Users

Security managers, CISOs, risk officers, and compliance teams use the system for oversight.

They care about:

- detection volume
- quarantine volume
- false positive rate
- false negative rate
- model reliability
- model behaviour trends
- global feature importance
- explanation credibility
- whether the model is safe to deploy

They should use the global explanation and model monitoring sections.

### 5.4 Technical Users

ML engineers, data scientists, and security engineers use the product to improve the model.

They care about:

- confirmed false positives
- confirmed false negatives
- feature contribution patterns
- model versioning
- improvement dataset
- fidelity metrics
- error-fidelity metrics
- drift indicators
- old vs new model comparison

---

## 6. Recommended Product Architecture

The intended high-level architecture is:

```text
Mailbox / Email Server
        ↓
Email Ingestion Service
        ↓
Feature Extraction Pipeline
        ↓
Phishing Detection Model
        ↓
Decision Engine
  ┌───────────────┬────────────────┐
  ↓               ↓                ↓
Allow Email   Warn User       Quarantine Email
        ↓
Explanation Service
  ┌───────────────────────────┬───────────────────────────┐
  ↓                           ↓
Local Explanation             Global Explanation
for one email                 for model behaviour
        ↓
SOC Analyst Dashboard
        ↓
Analyst Feedback / False Positive / False Negative Review
        ↓
Periodic Model Retraining and Surrogate Updating
```

For the first MVP, use mock data and a mock mailbox. Real Gmail or Microsoft 365 integration should come later.

---

## 7. Required Technical Stack

The system must be built using the following stack to ensure it remains maintainable by the system owner:

### Frontend
- **Language**: JavaScript
- **Framework**: React
- **Styling**: Tailwind CSS (Optional, but stick to JS/React ecosystem)

### Backend
- **Language**: Python
- **Framework**: FastAPI
- **Database**: SQL (SQLite for local development MVP, PostgreSQL for production)

### ML/XAI
- **Language**: Python
- **Libraries**: scikit-learn, pandas, SHAP, LIME, interpretML (EBM), GAMI-Net implementation

*Note: Do not introduce languages or major frameworks outside of Python, JavaScript, React, and SQL unless explicitly authorized, to keep the codebase familiar.*

### Mailbox
Development order:
1. Mock mailbox (JSON/CSV in database/seed/)
2. Gmail API
3. Microsoft Graph / Outlook

---

## 8. Important System Boundaries

Coding agents must keep these responsibilities separated.

### Frontend

Frontend code belongs in:

```text
apps/frontend/
```

The frontend should:

- display dashboard pages
- call backend APIs
- render charts, cards, tables, and explanations
- allow analyst actions

The frontend should not:

- load pickle model files
- run ML prediction directly
- connect directly to Gmail or Microsoft Graph
- store secrets
- hardcode business logic that belongs in backend services

### Backend

Backend code belongs in:

```text
apps/backend/
```

The backend should:

- expose API endpoints
- validate requests and responses
- coordinate services
- store and retrieve database records
- call ML service logic
- handle feedback workflow
- handle quarantine/release requests

Backend route files should stay thin. Put business logic in service files.

### ML Service

ML/XAI code belongs in:

```text
services/ml-service/
```

The ML service should:

- load trained teacher models
- load preprocessors and feature columns
- extract features from emails
- run prediction
- calculate risk level
- generate local explanation
- expose global explanation artifacts
- generate human-readable explanation summaries
- support future improvement recommendation generations

### Mailbox Service

Mailbox integration belongs in:

```text
services/mailbox-service/
```

Start with:

```text
services/mailbox-service/mock-mailbox/
```

Only add Gmail or Outlook after the offline flow is working.

### Models and Artifacts

Model artifacts belong in:

```text
models/
```

Suggested model artifact folders:

```text
models/teacher-models/
models/surrogate-models/
models/preprocessors/
models/explanation-artifacts/
```

Do not scatter model pickle files across frontend/backend folders.

---

## 9. Core Product Features

### 9.1 Email Scanning

The system should scan emails from a mailbox or sample dataset.

Each scanned email should produce:

- email ID
- subject
- sender
- recipient
- reply-to
- received time
- body summary or selected metadata
- extracted features
- prediction
- confidence score
- risk level
- recommended action
- model version

### 9.2 Risk Decision

The system should classify risk into operational levels.

Suggested risk policy:

```text
Low risk → allow
Medium risk → keep in inbox but warn
High risk → move to “Phishing Review” folder
Critical risk → quarantine and notify SOC
```

Never permanently delete emails.

### 9.3 Local Explanation

Local explanation should show why one specific email was classified a certain way.

It should include:

- top contributing features
- contribution values
- direction of contribution
- human-readable reasons
- explanation method used
- model version
- explanation snapshot timestamp

Example local explanation output:

```json
{
  "email_id": "abc123",
  "prediction": "phishing",
  "confidence": 0.94,
  "top_features": [
    {
      "feature": "sender_replyto_mismatch",
      "contribution": 0.24,
      "direction": "increases_phishing_risk",
      "human_reason": "The reply-to address does not match the sender."
    },
    {
      "feature": "max_url_length",
      "contribution": 0.18,
      "direction": "increases_phishing_risk",
      "human_reason": "The email contains an unusually long URL."
    }
  ],
  "human_summary": "This email was classified as phishing mainly because the reply-to address does not match the sender and the email contains an unusually long URL."
}
```

### 9.4 Global Explanation

Global explanation should show how the model behaves overall.

It should include:

- global feature importance
- EBM main effect plots
- GAMI-Net effect plots
- interaction effects
- accuracy fidelity
- F1 fidelity
- error fidelity
- model comparison
- surrogate comparison
- false positive pattern summaries
- false negative pattern summaries

Global explanation is for model governance and analyst trust.

### 9.5 Human-Readable Explanation Layer

Raw explanation values should not be shown alone.

The product must translate numerical explanation outputs into clear SOC-friendly text.

Example:

Raw:

```text
max_url_length contribution = +0.31
sender_replyto_mismatch contribution = +0.25
has_urgent_words contribution = +0.11
```

Dashboard explanation:

```text
This email was classified as phishing mainly because it contains an unusually long URL, the reply-to address does not match the sender, and the message uses urgent wording.
```

Explanation text should be clear but not overconfident. It should say what influenced the model, not claim absolute proof of malicious intent.

---

## 10. Dashboard Requirements

The dashboard should follow the SOC analyst workflow.

Recommended sidebar navigation:

```text
Overview
Detection Queue
Quarantine
Email Investigation
Local Explanation
Global Explanation
Feedback Review
Model Monitoring
Settings
```

### 10.1 Overview Page

Purpose:

Give quick visibility into mailbox threat activity and model health.

Show:

- total emails scanned
- phishing detected
- quarantined emails
- high-risk emails awaiting review
- false positive reports
- false negative reports
- average model confidence
- detection trend over time
- phishing vs legitimate distribution
- top risky sender domains
- top risky URL domains
- confidence distribution
- recent high-risk detections

### 10.2 Detection Queue Page

Purpose:

Show suspicious emails as investigation cases.

Columns should include:

- received time
- sender
- subject
- prediction
- confidence
- risk level
- action taken
- review status
- assigned analyst
- short explanation summary

Filters should include:

- risk level
- prediction
- quarantine status
- reviewed/unreviewed
- false positive reports
- false negative reports
- sender domain
- date range
- attachment presence
- URL presence

### 10.3 Quarantine Page

Purpose:

Show emails that were moved to a safe review/quarantine area.

Actions:

- open investigation
- confirm phishing
- release email
- mark false positive
- escalate

### 10.4 Email Investigation Page

Purpose:

Give a detailed view of one email.

Show:

- subject
- sender
- reply-to
- recipient
- received time
- model prediction
- confidence
- risk level
- quarantine status
- sender analysis
- URL analysis
- attachment analysis
- body indicators
- local explanation
- analyst action buttons

### 10.5 Local Explanation Page or Panel

Purpose:

Explain one prediction.

Show:

- prediction and confidence
- top positive features
- top negative features
- feature contribution bar chart
- human-readable explanation
- raw feature values
- explainer method
- model version
- explanation timestamp

### 10.6 Global Explanation Page

Purpose:

Explain overall model behaviour.

Show:

- global feature importance
- EBM plots
- GAMI-Net plots
- main effect plots
- interaction plots
- fidelity metrics
- error fidelity metrics
- teacher/surrogate comparison
- false-positive pattern summary
- false-negative pattern summary

### 10.7 Feedback Review Page

Purpose:

Support human-in-the-loop improvement.

Show:

- user-reported wrong detections
- original model prediction
- original confidence
- original local explanation snapshot
- user feedback
- analyst-confirmed label
- error type
- reason category
- review status
- action buttons

Actions:

- confirm phishing
- confirm legitimate
- mark false positive
- mark false negative
- release from quarantine
- escalate
- reject feedback
- export to improvement dataset

### 10.8 Model Monitoring Page

Purpose:

Track model health, explanation quality, and version history.

Show:

- current detector model
- current surrogate model
- model version
- accuracy
- precision
- recall
- F1-score
- false positive rate
- false negative rate
- accuracy fidelity
- F1 fidelity
- error fidelity
- explanation latency
- confirmed feedback case count
- pending review count
- improvement history
- old vs new model comparison

---

## 11. Human-in-the-Loop Improvement

The product must support feedback, but it must not automatically learn from every user flag.

Reason:

- users may be wrong
- attackers may attempt feedback poisoning
- incorrect feedback can damage the model
- cybersecurity systems need controlled validation

Safe workflow:

```text
User flags email
→ SOC analyst reviews it
→ Analyst confirms true label
→ System records true positive / true negative / false positive / false negative
→ Confirmed case is stored in feedback dataset
→ Model owner reviews failure patterns
→ Export confirmed feedback for future offline retraining
→ Detection model is evaluated
→ Generate improvement recommendations
→ New model is deployed only if validated
```

Feedback types:

| Model Prediction | Analyst Label | Case Type |
|---|---|---|
| phishing | phishing | true positive |
| legitimate | legitimate | true negative |
| phishing | legitimate | false positive |
| legitimate | phishing | false negative |

Feedback records should store:

- email ID
- model prediction
- confidence
- model version
- explanation snapshot
- user feedback
- analyst-confirmed label
- error type
- review status
- analyst ID
- timestamp
- action taken

---

## 12. Safety and Security Rules

All coding agents must follow these rules.

1. Do not permanently delete emails.
   - Move suspicious emails to a review/quarantine folder.

2. Do not trust user feedback automatically.
   - SOC analyst validation is required before model improvement.

3. Do not store secrets in code.
   - Use `.env` files and `.env.example` placeholders.

4. Do not print full email bodies in logs.
   - Logs should avoid sensitive content.

5. Do not store unnecessary email content.
   - Prefer metadata and extracted features where possible.

6. Preserve model version for every prediction.
   - Explanations must match the model version that created the prediction.

7. Preserve explanation snapshots.
   - If the model changes later, historical explanations should still explain historical decisions.

8. Do not present explanations as absolute proof.
   - They show which features influenced the model.

9. Build mock mailbox first.
   - Real Gmail/Outlook integration comes later.

10. Prioritise offline dashboard MVP before production deployment.

---

## 13. Recommended API Endpoints

The backend should eventually support these endpoints:

```text
GET    /dashboard/summary
GET    /emails
GET    /emails/{id}
POST   /scan-email
POST   /scan-batch
GET    /emails/{id}/local-explanation
GET    /global-explanation
POST   /emails/{id}/feedback
POST   /emails/{id}/quarantine
POST   /emails/{id}/release
GET    /feedback
PATCH  /feedback/{id}/review
GET    /monitoring/model-health
GET    /monitoring/model-versions
GET    /monitoring/fidelity
```

During the first MVP, endpoints can return sample/mock data.

---

## 14. Recommended Data Models

The system should eventually store these entities:

### Email

- id
- mailbox_message_id
- subject
- sender
- recipient
- reply_to
- received_at
- body_preview
- url_count
- attachment_count
- quarantine_status
- created_at

### Prediction

- id
- email_id
- prediction_label
- confidence
- risk_level
- recommended_action
- model_name
- model_version
- created_at

### Local Explanation

- id
- email_id
- prediction_id
- explainer_type
- top_features
- human_summary
- explanation_snapshot
- created_at

### Global Explanation

- id
- model_name
- model_version
- surrogate_name
- global_feature_importance
- effect_plot_paths
- interaction_plot_paths
- accuracy_fidelity
- f1_fidelity
- error_fidelity
- created_at

### Feedback Case

- id
- email_id
- prediction_id
- user_feedback
- analyst_label
- error_type
- reason_category
- review_status
- reviewed_by
- reviewed_at
- added_to_improvement_dataset
- created_at

### Model Version

- id
- model_name
- model_type
- version
- artifact_path
- deployed_at
- metrics
- active

---

# MVP Scope

## Purpose

This document defines the scope of the first minimum viable product for the explainable phishing detection dashboard.

The MVP should prove the product workflow before implementing real mailbox integration or retraining.

---

## MVP Goal

The MVP should demonstrate that the product can:

```text
show scanned emails
show phishing predictions
show risk levels
show quarantine status
show local explanations
show global explanation metrics
support feedback review
simulate analyst decision workflow
```

The MVP should focus on dashboard experience and system flow, not production infrastructure.

---

## MVP Must Include

### 1. Mock Email Dataset

Use sample email records stored locally.

Recommended file:

```text
data/sample/sample_emails.json
```

Each sample email should include:

- email ID
- subject
- sender
- recipient
- reply-to
- received time
- body preview
- URL count
- attachment count
- quarantine status
- review status

---

### 2. Mock Predictions

Use sample prediction records.

Recommended file:

```text
data/sample/sample_predictions.json
```

Each prediction should include:

- email ID
- prediction label
- confidence
- risk level
- recommended action
- model name
- model version

---

### 3. Mock Local Explanations

Use sample local explanation records.

Recommended file:

```text
data/sample/sample_local_explanations.json
```

Each local explanation should include:

- email ID
- top contributing features
- contribution values
- direction
- human-readable reasons
- human-readable summary
- explainer type
- model version

---

### 4. Mock Global Explanations

Use sample global explanation records.

Recommended file:

```text
data/sample/sample_global_explanations.json
```

Global explanations should include:

- teacher model
- surrogate model
- accuracy fidelity
- F1 fidelity
- error fidelity
- global feature importance
- effect plot references
- failure pattern summaries

---

### 5. Mock Feedback Cases

Use sample feedback records.

Recommended file:

```text
data/sample/sample_feedback_cases.json
```

Feedback cases should include:

- original prediction
- user feedback
- analyst label
- error type
- review status
- explanation snapshot
- added to retraining flag

---

## MVP Dashboard Pages

The MVP should include these pages:

```text
Overview
Detection Queue
Email Investigation
Local Explanation Panel
Global Explanation
Feedback Review
Model Monitoring
```

The Quarantine and Settings pages can be basic placeholders if time is limited.

---

## MVP Backend

The backend should provide mock API endpoints:

```text
GET /dashboard/summary
GET /emails
GET /emails/{id}
GET /emails/{id}/local-explanation
GET /global-explanation
GET /feedback
PATCH /feedback/{id}/review
POST /emails/{id}/quarantine
POST /emails/{id}/release
GET /monitoring/model-health
```

For MVP, these endpoints can read from local JSON files.

---

## MVP Frontend

The frontend should show:

- dark SOC-style layout
- left navigation
- metric cards
- detection queue
- email detail page
- local explanation panel
- global explanation charts/metrics
- feedback review table
- model monitoring cards

The dashboard should follow the UI guidance in:

```text
docs/dashboard/dashboard-pages.md
docs/dashboard/wireframe-notes.md
docs/dashboard/inspiration/README.md
```

---

## MVP Model Integration

For the earliest MVP, model inference can be mocked.

After the UI/API flow works, integrate existing model artifacts from:

```text
models/teacher-models/
models/surrogate-models/
models/preprocessors/
models/explanation-artifacts/
```

Do not retrain models.

---

## MVP Mailbox Integration

Use mock mailbox only.

Recommended location:

```text
services/mailbox-service/mock-mailbox/
```

Do not implement Gmail or Microsoft 365 yet.

---

## MVP Feedback Workflow

The MVP should support:

```text
analyst opens feedback case
→ analyst confirms phishing or legitimate
→ system marks true positive / true negative / false positive / false negative
→ feedback status updates
```

The MVP should not support automatic model updating.

---

## Out of Scope for MVP

Do not build these in the first MVP:

- real Gmail integration
- real Microsoft 365 integration
- automatic model updating
- production authentication
- production deployment
- real-time continuous mailbox scanning
- attachment content scanning
- advanced threat intelligence enrichment
- multi-tenant organisation support

---

## MVP Definition of Done

The MVP is complete when:

- dashboard pages render correctly
- mock API endpoints return realistic data
- detection queue can open email details
- local explanations are visible and human-readable
- global explanation page shows fidelity/error-fidelity metrics
- feedback review workflow works
- quarantine/release simulation works
- model monitoring page displays current model information
- tests cover core dashboard/API flows

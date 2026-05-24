# AGENTS.md

## Project Summary

This project is a SOC-friendly explainable phishing detection and model-governance system with web dashboard for business mailboxes.

The product extends an existing explainable phishing detection research project into an operational software system. The existing research/code foundation already includes phishing detection models and explanation mechanisms. The goal of this product is to scan mailbox emails, classify phishing risk, quarantine suspicious emails, and provide both local and global explanations through a dashboard designed for SOC analysts, security managers, and model owners.

This product should not be treated as only an “AI phishing detector.”

The main product value is:

```text
Phishing detection
+ local explanation for individual emails
+ global explanation of model behaviour
+ quarantine/release workflow
+ false-positive/false-negative review
+ human-in-the-loop improvement support
```

---

## Core Product Goal

The system should eventually be able to:

1. Connect to a mailbox or mock mailbox.
2. Read incoming or selected emails.
3. Extract phishing-relevant features.
4. Classify emails as phishing or legitimate.
5. Assign confidence score and risk level.
6. Quarantine or flag high-risk emails.
7. Provide local explanations for single-email predictions.
8. Provide global explanations of model behaviour.
9. Allow users/analysts to flag incorrect detections.
10. Store analyst-confirmed false positives and false negatives.
11. Support Future model improvement and model governance.

---

## Existing Research Foundation

The project already has:

- Random Forest phishing detection model.
- Deep Neural Network / MLP phishing detection model.
- SHAP/LIME local explanation direction.
- EBM global surrogate explanation model.
- GAMI-Net global surrogate explanation model.
- Accuracy, precision, recall, F1 results.
- Accuracy Fidelity.
- F1 Fidelity.
- Error Fidelity.
- Research results showing global surrogate models can approximate black-box phishing detectors.

Do not rebuild the research from scratch unless explicitly requested.

The first coding goal is productisation:

```text
Existing models and explanation artifacts
→ backend API
→ dashboard
→ mock mailbox workflow
→ explanation display
→ feedback review
```

---

## Global Rules for All Agents

All agents must follow these rules:

1. Read `PROJECT_CONTEXT.md` before making major implementation decisions.
2. Read `OUTCOME_REQUIREMENTS.md` before implementing product features.
3. Keep frontend, backend, model integration, mailbox integration, and tests separated.
4. Build the offline/mock dashboard MVP before real Gmail or Outlook integration.
5. Do not permanently delete emails.
6. Move suspicious emails to a quarantine/review state instead.
7. Do not automatically retrain models from user feedback.
8. User feedback must be validated by a SOC analyst before it can be used for future retraining.
9. Store model version for every prediction.
10. Store explanation snapshot for every prediction.
11. Convert raw explanation values into human-readable SOC analyst language.
12. Do not present explanations as absolute proof of phishing.
13. Do not commit secrets, API keys, OAuth tokens, or mailbox credentials.
14. Do not print full sensitive email bodies in logs.
15. Write tests for important workflows.
16. Prefer small, modular, testable changes.
17. Do not remove local explanation, global explanation, feedback review, or model monitoring features from scope.

---

## Recommended Directory Boundaries

Agents should respect these boundaries:

```text
apps/frontend/                  Frontend dashboard
apps/backend/                   FastAPI backend
services/ml-service/            Model loading, prediction, explainability
services/mailbox-service/       Mock mailbox, Gmail, Outlook integration
models/                         Existing model and explanation artifacts
data/                           Sample data, feedback data, exports
database/                       Schema, migrations, seed data
docs/                           Product, architecture, API, workflow docs
tests/                          Unit, integration, e2e, AI eval tests
.agent/                         Agent instructions, workflows, memory, patterns
agents/                         Detailed agent definitions
```

---

## Agent List

This project uses the following agents:

1. Product Architect Agent
2. Frontend Dashboard Agent
3. Backend API Agent
4. Mailbox Integration Agent
5. Model Integration & Explainability Agent
6. Testing / QA Agent
7. Reviewer Agent

---

# 1. Product Architect Agent

## Role

You are responsible for keeping the whole system aligned with the product vision.

The product must remain:

```text
A SOC-friendly explainable phishing detection and model-governance dashboard.
```

## Responsibilities

- Maintain the overall architecture.
- Ensure implementation follows `PROJECT_CONTEXT.md` and `OUTCOME_REQUIREMENTS.md`.
- Decide where new features belong.
- Keep frontend, backend, model integration, mailbox integration, and tests separated.
- Prevent overengineering.
- Keep the MVP focused on mock mailbox and offline dashboard first.
- Maintain architecture documentation.
- Ensure local explanation, global explanation, feedback review, quarantine, and model monitoring remain in scope.

## Main Files

```text
PROJECT_CONTEXT.md
OUTCOME_REQUIREMENTS.md
AGENTS.md
docs/architecture/
docs/product/
docs/workflows/
.agent/memory/
.agent/patterns/
```

## Must Avoid

- Do not allow the project to become only a generic phishing classifier.
- Do not allow Gmail/Outlook integration before the mock mailbox flow works.
- Do not remove explanation or feedback features.
- Do not mix frontend, backend, and model logic in the same files.

---

# 2. Frontend Dashboard Agent

## Role

You are responsible for building the SOC analyst dashboard UI.

## Work Areas

```text
apps/frontend/src/pages/
apps/frontend/src/components/
apps/frontend/src/api/
apps/frontend/src/types/
apps/frontend/src/hooks/
apps/frontend/src/utils/
packages/ui/
```

## Required Pages

- Overview Page
- Detection Queue Page
- Quarantine Page
- Email Investigation Page
- Local Explanation Page or Panel
- Global Explanation Page
- Feedback Review Page
- Model Monitoring Page
- Settings Page

## Responsibilities

- Build a professional SOC/security dashboard.
- Show scanned emails, phishing detections, quarantined emails, false positives, false negatives, confidence distribution, and high-risk cases.
- Build detection queue tables with filtering and sorting.
- Build email investigation views.
- Display local explanations in readable form.
- Display global explanations using feature importance charts, fidelity metrics, and explanation summaries.
- Build feedback review UI for analyst-confirmed false positives and false negatives.
- Use backend APIs or mock data only.
- Keep components modular and reusable.

## UI Style

The UI should be:

- professional
- clean
- SOC-friendly
- enterprise SaaS style
- serious cybersecurity style

Avoid childish “hacker movie” visuals.

## Must Avoid

- Do not load model files in frontend.
- Do not connect directly to Gmail or Outlook.
- Do not hardcode model prediction logic in React.
- Do not store sensitive email bodies unnecessarily in frontend state.

---

# 3. Backend API Agent

## Role

You are responsible for building the FastAPI backend that powers the dashboard.

## Work Areas

```text
apps/backend/app/main.py
apps/backend/app/api/
apps/backend/app/services/
apps/backend/app/schemas/
apps/backend/app/models/
apps/backend/app/repositories/
apps/backend/app/utils/
```

## Core API Endpoints

The backend should eventually support:

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

## Responsibilities

- Build API routes for dashboard data.
- Validate request and response schemas.
- Keep route files thin.
- Put business logic in service files.
- Use repositories for database access when persistence is added.
- Serve mock/sample data first for MVP.
- Connect to model integration service when real inference is added.
- Store prediction, confidence, risk level, model version, and explanation snapshot.
- Support quarantine and release actions.
- Support analyst feedback review.
- Return dashboard-ready JSON.

## Must Avoid

- Do not put large model or explainability logic directly in API route files.
- Do not permanently delete emails.
- Do not automatically retrain models from user feedback.
- Do not expose secrets or mailbox tokens through API responses.

---

# 4. Mailbox Integration Agent

## Role

You are responsible for mailbox ingestion, quarantine simulation, and later real mailbox API integration.

## Work Areas

```text
services/mailbox-service/mock-mailbox/
services/mailbox-service/gmail/
services/mailbox-service/microsoft365/
```

## Development Priority

1. Mock mailbox first.
2. Gmail API prototype later.
3. Microsoft Graph / Outlook integration after the product flow works.

## Responsibilities

- Read sample/mock emails from JSON or CSV.
- Provide mailbox-like email objects to the backend.
- Simulate moving suspicious emails into a `Phishing Review` or `Quarantine` folder.
- Simulate releasing emails back to inbox.
- Preserve original mailbox message ID and folder/label status.
- Later implement Gmail label-based workflow.
- Later implement Microsoft 365 folder-based workflow.

## Safe Quarantine Rule

Never permanently delete emails.

Allowed actions:

```text
allow
warn
move to review folder
move to quarantine folder
release from quarantine
```

## Must Avoid

- Do not permanently delete emails.
- Do not store mailbox credentials in code.
- Do not request excessive mailbox permissions.
- Do not build real Gmail/Outlook integration before mock mailbox flow works.

---

# 5. Model Integration & Explainability Agent

## Role

You are responsible for integrating existing trained phishing detection models and explanation mechanisms into the product.

This is not a model-training agent. The project already has trained detection models and explanation resources. Your job is to make those resources usable by the backend and dashboard.

## Work Areas

```text
services/ml-service/
services/ml-service/feature-engineering/
services/ml-service/inference/
services/ml-service/explainability/
services/ml-service/monitoring/
models/teacher-models/
models/surrogate-models/
models/preprocessors/
models/explanation-artifacts/
```

## Existing Model Resources

The research foundation includes:

- Random Forest teacher model.
- Deep Neural Network / MLP teacher model.
- SHAP/LIME local explanation direction.
- EBM global surrogate model.
- GAMI-Net global surrogate model.
- Accuracy Fidelity.
- F1 Fidelity.
- Error Fidelity.

## Responsibilities

- Load existing Random Forest and DNN model artifacts.
- Load existing EBM and GAMI-Net surrogate explanation artifacts.
- Load preprocessing artifacts such as encoders, scalers, and feature columns.
- Convert raw or mock emails into the same feature format expected by trained models.
- Run phishing/legitimate prediction.
- Return confidence score, risk level, recommended action, and model version.
- Generate local explanation output for individual emails.
- Prepare global explanation data from EBM/GAMI-Net outputs.
- Convert raw explanation values into dashboard-ready JSON.
- Convert technical explanation outputs into human-readable SOC analyst language.
- Ensure every prediction records model version and explanation snapshot.
- Support fidelity and error-fidelity display for model monitoring.

## Expected Prediction Output

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

## Expected Local Explanation Output

```json
{
  "email_id": "email_001",
  "top_features": [
    {
      "feature": "sender_replyto_mismatch",
      "contribution": 0.24,
      "direction": "increases_phishing_risk",
      "human_reason": "The reply-to address does not match the sender address."
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

## Must Avoid

- Do not train new models unless explicitly asked.
- Do not change existing model artifacts without approval.
- Do not automatically retrain from user feedback.
- Do not output only raw SHAP/LIME values without human-readable explanation text.
- Do not present explanations as absolute proof of phishing.

---

# 6. Testing / QA Agent

## Role

You are responsible for testing the product and validating that the implementation matches the requirements.

## Work Areas

```text
tests/unit/
tests/integration/
tests/e2e/
apps/backend/app/tests/
services/ml-service/tests/
apps/frontend/e2e/
```

## Responsibilities

- Write unit tests for backend services.
- Write unit tests for feature extraction and prediction logic.
- Write API tests for backend endpoints.
- Write integration tests for scan-email flow.
- Write integration tests for local explanation flow.
- Write integration tests for feedback review flow.
- Write tests for quarantine and release actions.
- Write frontend/e2e tests for key dashboard flows.
- Check that mock data works before real mailbox integration.

## Required Test Flows

### Scan Email Flow

```text
Sample email is loaded
→ email is scanned
→ prediction is generated
→ risk level is assigned
→ local explanation is generated
→ email appears in detection queue
```

### Feedback Flow

```text
Analyst opens email case
→ analyst marks result as false positive or false negative
→ feedback case is stored
→ feedback review page updates
→ model monitoring count updates
```

### Quarantine Flow

```text
High-risk email is detected
→ email is moved to quarantine/review status
→ analyst releases or confirms it
→ status updates correctly
```

## Must Avoid

- Do not test only happy paths.
- Do not skip feedback workflow tests.
- Do not skip explanation output tests.
- Do not ignore security/privacy rules during testing.

---

# 7. Reviewer Agent

## Role

You are responsible for reviewing code quality, architecture consistency, safety, and requirement alignment before changes are considered complete.

## Review Sources

Always compare implementation against:

```text
PROJECT_CONTEXT.md
OUTCOME_REQUIREMENTS.md
AGENTS.md
docs/
```

## Responsibilities

- Check that implementation matches the product goal.
- Check that local explanation and global explanation are preserved.
- Check that frontend, backend, model integration, and mailbox integration are separated.
- Check that route files are not too large.
- Check that business logic is placed in services.
- Check that model logic is not placed in frontend.
- Check that mailbox logic is not placed in frontend.
- Check that explanations are human-readable.
- Check that every prediction stores model version and explanation snapshot.
- Check that feedback is analyst-confirmed before model improvement.
- Check that no permanent email deletion is implemented.
- Check that tests are included for important workflows.
- Recommend refactoring when files become messy or duplicated.

## Must Avoid

- Do not approve code that violates safety rules.
- Do not approve code that removes explanation functionality.
- Do not approve direct automatic model updating from user feedback.
- Do not approve hardcoded secrets.
- Do not approve frontend code that directly loads model artifacts.

---
## Definition of Done

A task is not done unless:

- the implementation matches `PROJECT_CONTEXT.md` and `OUTCOME_REQUIREMENTS.md`
- the correct agent boundaries are respected
- important workflows have tests
- no secrets are committed
- no permanent email deletion is implemented
- predictions include model version
- explanations include explanation snapshot
- local explanations are human-readable
- global explanations are dashboard-ready
- reviewer checks have passed

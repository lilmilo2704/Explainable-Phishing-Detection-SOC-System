# Testing Rules

## General Testing Requirements

All important product workflows must have tests.

Prioritise tests for:
- API endpoints
- feature extraction
- prediction output shape
- local explanation output shape
- global explanation output shape
- feedback review workflow
- quarantine/release workflow
- dashboard data flow

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

### Feedback Review Flow

```text
Analyst opens email case
→ analyst marks result as false positive or false negative
→ feedback case is stored
→ review status updates
→ model monitoring count updates
```

### Quarantine Flow

```text
High-risk email is detected
→ email is moved to quarantine/review state
→ analyst releases or confirms it
→ status updates correctly
```

## Testing Boundaries

Backend tests belong in `apps/backend/app/tests/` or `tests/integration/`.
ML-service tests belong in `services/ml-service/tests/`.
Frontend e2e tests belong in `tests/e2e/` or `apps/frontend/e2e/`.

## Must Avoid

Do not test only happy paths.
Do not skip explanation tests.
Do not skip feedback tests.
Do not skip quarantine tests.
Do not ignore security/privacy rules during testing.
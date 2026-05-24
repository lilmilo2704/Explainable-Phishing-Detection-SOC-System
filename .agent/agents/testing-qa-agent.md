# 6. Testing / QA Agent

**Purpose:** Tests whether the system works end-to-end.

This agent should make sure changes do not break the scanning, explanation, dashboard, or feedback workflow.

**Responsibilities:**

```md
# Testing / QA Agent

## Role

You are responsible for testing the product and validating that the implementation matches the project requirements.

## Work Areas

- `tests/unit/`
- `tests/integration/`
- `tests/e2e/`
- `apps/backend/app/tests/`
- `services/ml-service/tests/`
- `apps/frontend/e2e/`

## Core Responsibilities

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
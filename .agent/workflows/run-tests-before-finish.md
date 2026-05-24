# Workflow: Run Tests Before Finish

Before marking any task complete, run or reason through the relevant tests.

## Backend

Run backend tests when backend files changed.

Suggested:

```bash
pytest apps/backend/app/tests
pytest tests/integration
```

## ML Service

Run ML-service tests when model integration, feature extraction, or explanation files changed.

Suggested:

```bash
pytest services/ml-service/tests
```

## Frontend

Run frontend checks when React files changed.

Suggested:

```bash
cd apps/frontend
npm run lint
npm test
npm run build
```

## E2E

Run e2e tests for dashboard workflow changes.

Suggested:

```bash
npm run test:e2e
```

## Required Manual Checks

Check that:

- no secrets are committed
- no permanent email deletion is added
- no automatic model updating from user feedback is added
- predictions include model version
- explanations include explanation snapshot
- local explanation text is human-readable
- global explanation data is dashboard-ready
- route files are not too large
- logic is in the correct layer

## If Tests Cannot Be Run

If the environment does not support running tests, clearly report:

- which tests should be run
- why they were not run
- what files changed
- what risks remain

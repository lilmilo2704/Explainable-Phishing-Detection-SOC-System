# Backend API Agent

## Role

You are responsible for building the FastAPI backend that powers the explainable phishing detection dashboard.

## Work Areas

- `apps/backend/app/main.py`
- `apps/backend/app/api/`
- `apps/backend/app/services/`
- `apps/backend/app/schemas/`
- `apps/backend/app/models/`
- `apps/backend/app/repositories/`
- `apps/backend/app/utils/`

## Core API Endpoints

- `GET /dashboard/summary`
- `GET /emails`
- `GET /emails/{id}`
- `POST /scan-email`
- `POST /scan-batch`
- `GET /emails/{id}/local-explanation`
- `GET /global-explanation`
- `POST /emails/{id}/feedback`
- `POST /emails/{id}/quarantine`
- `POST /emails/{id}/release`
- `GET /feedback`
- `PATCH /feedback/{id}/review`
- `GET /monitoring/model-health`
- `GET /monitoring/model-versions`
- `GET /monitoring/fidelity`

## Core Responsibilities

- Build API routes for dashboard data.
- Validate request and response schemas.
- Keep route files thin.
- Put business logic in service files.
- Use repositories for database access when persistence is added.
- Serve mock/sample data first for MVP.
- Connect to model integration service when real model inference is added.
- Store prediction, confidence, risk level, model version, and explanation snapshot.
- Support quarantine and release actions.
- Support analyst feedback review.
- Return dashboard-ready JSON.

## Must Avoid

- Do not put large ML logic directly in API route files.
- Do not permanently delete emails.
- Do not automatically retrain models from user feedback.
- Do not expose secrets or mailbox tokens through API responses.
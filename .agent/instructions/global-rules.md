# Global Rules

## Product Identity

This project is a SOC-friendly explainable phishing detection and model-governance dashboard for business mailboxes.

The product must support:
- phishing email detection
- local explanations for individual emails
- global explanations of model behaviour
- quarantine/release workflow
- false-positive/false-negative review
- human-in-the-loop improvement support

Do not reduce the product into only a generic phishing classifier.

## Required Reading

Before making major changes, coding agents must read:
- `PROJECT_CONTEXT.md`
- `OUTCOME_REQUIREMENTS.md`
- `AGENTS.md`
- `IMPLEMENTATION_PLAN.md`

## Architecture Rules

Keep responsibilities separated:

- `apps/frontend/` = React dashboard only
- `apps/backend/` = FastAPI backend and API logic
- `services/ml-service/` = model loading, feature extraction, prediction, explainability
- `services/mailbox-service/` = mock mailbox, Gmail, Outlook integration
- `models/` = saved model artifacts and explanation artifacts
- `database/` = schema and seed data
- `tests/` = unit, integration, and e2e tests

## MVP Rule

Build the offline/mock MVP first.

The first MVP should use:
- mock mailbox/sample emails
- mock predictions
- mock local explanations
- mock global explanations
- feedback review UI
- quarantine simulation

Do not start with real Gmail or Microsoft 365 integration.

## Model Rule

The project already has trained models and explanation resources.

Do not retrain models unless explicitly requested.

The first goal is to integrate existing models and artifacts into the product.

## Explanation Rule

Every prediction must support:
- model version
- explanation snapshot
- local explanation
- dashboard-readable explanation summary

Global explanation must support:
- feature importance
- EBM/GAMI-Net explanation artifacts
- fidelity metrics
- error-fidelity metrics

## Coding Style

- Prefer small, modular, testable changes.
- Keep route files thin.
- Put business logic in services.
- Put data access logic in repositories when persistence is added.
- Keep UI components reusable.
- Avoid hardcoded demo values inside production components.
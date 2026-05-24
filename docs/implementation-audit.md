# Implementation Audit - Live Gmail Prototype

Date: 2026-05-25

## Product Positioning

This repository implements a SOC-friendly explainable phishing detection and model-governance dashboard as a live Gmail prototype. The intended operating mode is manually initiated Gmail sync, shadow-mode analysis, reversible quarantine for trusted high-risk decisions, analyst feedback review, and auditable actions.

## Current Architecture

| Area | Runtime location | Current state |
| --- | --- | --- |
| Frontend | `apps/frontend/src/` | React/Vite dashboard with overview, queue, quarantine, investigation, explanations, feedback, monitoring, and settings pages. |
| Backend | `apps/backend/app/main.py`, `apps/backend/app/api/endpoints.py` | FastAPI API backed by SQLite and service modules. |
| Model serving | `apps/backend/app/services/model_manager.py`, `services/ml-service/` | Teacher/surrogate artifacts loaded locally and invoked in-process. |
| Mailbox | `apps/backend/app/services/mailbox_integration.py` | Mock provider and Gmail API adapter with manual sync route. |
| Persistence | `apps/backend/app/models.py`, `database/phishguard.db` | SQLite stores email, prediction, explanation, feedback and model records. |

## Findings

### Backend And Data Flow

- API routes currently orchestrate scanning, feedback, quarantine, and monitoring directly; core persistence helpers exist but audit and sync-run persistence are absent.
- Email prediction snapshots are appended on repeated syncs, with no explicit latest-state constraint or content/model deduplication.
- The email record stores a preview, but not the full prototype body, URL list, attachment metadata, feature snapshot, or content fingerprint.
- Monitoring currently mixes hardcoded research/demo metrics with operational counts.

### Model Loading And Preprocessing

- Random Forest and surrogate model registry entries exist; active configuration must be fixed to Random Forest with EBM for the Gmail prototype default.
- The runtime expects 292 processed features.
- At audit time, the exact fitted training preprocessor and processed feature-column order artifact were not present in the runtime model/preprocessor directory.
- The processed feature-column order has since been recovered from the fitted EBM surrogate's embedded `feature_names_in_` metadata and validated against the Random Forest feature count.
- The fitted training preprocessor has since been deterministically reconstructed from the original GitHub Git LFS training data and validated against every row of the saved processed split dataset.
- The current fallback pads missing categorical/one-hot columns with zeros and proceeds with inference. This does not establish schema equivalence to training and is unsafe for trusted live decisions.

### Gmail And Mock Mailbox Flow

- Gmail message parsing extracts URLs internally, but mailbox sync currently sends `urls: []` into inference and does not persist the URL list.
- Gmail quarantine currently adds a review label but does not remove `INBOX`; release removes the review label but does not restore `INBOX`.
- Gmail sync is manually invoked; the dashboard now explicitly submits the Gmail provider and refreshes live views after each completed sync.
- Model failure during sync currently falls back to an allowed/legitimate result rather than a needs-review failure state.

### Dashboard And Performance

- The frontend has reusable table/badge/card components and reasonable page separation.
- Model-readiness and last-sync status are not shown.
- Operational and benchmark metrics are not distinguished for users.
- Repeated mailbox sync can generate duplicate prediction/explanation records; this is the most important database and API efficiency issue.
- Some queue screens poll state despite the desired manual mailbox sync workflow.

### Tests

- Backend tests cover core API flows, model pairing, feedback governance, mock sync, and a minimal Gmail adapter.
- Test coverage does not yet verify URL preservation through sync, deduplication, safe preprocessing readiness, Gmail label transitions, audit logging, or failure-safe sync handling.
- Frontend has build tooling but no focused test suite for new operational status views.

### Configuration And Security Risk

| Risk | Path/area | Severity |
| --- | --- | --- |
| Local Gmail credential/token artifacts exist and must remain untracked and be rotated if ever exposed. Contents were not inspected. | `secrets/`, `apps/backend/secrets/` | Critical if committed/exposed |
| Gmail provider relies on default local credential paths rather than explicit environment configuration. | `apps/backend/app/services/mailbox_integration.py` | High |
| CORS allows all origins with credentials enabled. | `apps/backend/app/main.py` | High |
| Quarantine/release/feedback/model switching lack an audit trail. | backend persistence/API | High |
| Full message content is sensitive and must not appear in logs. | sync/API logging | Medium |

## Documentation Versus Runtime Mismatch

- The mock mailbox remains available for deterministic tests, while normal configured live views now scope records and metrics to Gmail.
- Requirements call for model version and explanation snapshots, but latest prediction state and audit relationships are not enforced.
- Requirements call for human-readable, uncertainty-aware explanations; current explanations are sparse and do not warn about unsafe preprocessing.
- Requirements call for truthful live monitoring; fixed performance numbers are currently displayed without benchmark labeling.

## Implementation Direction

This hardening pass adds configuration hygiene, model readiness validation, explicit untrusted/needs-review behaviour, Gmail URL preservation and reversible labels, deduplicated latest prediction state, sync status and action auditing, benchmark/live metric separation, and visible frontend warnings. It intentionally avoids full authentication, background Gmail sync, automatic retraining, and new email-authentication features.

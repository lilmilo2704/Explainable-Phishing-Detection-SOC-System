# Known Issues and Risks

## Runtime Status Correction (2026-05-26)

The early integration risks below are retained as historical design context. Runtime now validates recovered preprocessing/feature order and can serve active model readiness. Mailbox sync is manually triggered; no background auto-sync worker is active. Confirmed-feedback export remains intentionally disabled in this prototype.

Current open priorities are authentication/role enforcement for state-changing actions, data-retention controls for stored message bodies, and persistence of ad-hoc `/scan-email` submissions when they are used as investigation cases.

## 1. Historical Model Artifact Integration Risk

The project originally required:
- artifact placement
- loader functions
- dependency setup
- preprocessing alignment
- feature column ordering
- prediction output wrapper

## 2. Raw Emails Are Not Model-Ready

The trained models expect processed features, not raw email text.

The product must implement:

```text
raw email
→ feature extraction
→ preprocessing/encoding/scaling
→ exact feature order
→ model prediction
```

## 3. Feature Order Risk

The model may produce meaningless predictions if feature columns are in the wrong order.

The system must keep a `feature_columns.json` or equivalent feature-order record.

## 4. Preprocessing Artifact Risk

The model likely requires the same encoders/scalers/imputers used during training.

If these artifacts are not available, the model integration agent must reconstruct or extract preprocessing logic from the training pipeline.

## 5. Explanation Output Risk

Raw SHAP/LIME/EBM/GAMI-Net outputs may be numerical and not analyst-friendly.

The product needs a human-readable explanation generation layer.

## 6. Feedback Poisoning Risk

Never update models directly from user flags.

Feedback must be analyst-confirmed before use in future retraining.

## 7. Mailbox Integration Risk

Real Gmail or Outlook integration requires OAuth and permission design.

Do not start real mailbox integration before mock mailbox workflow works.

## 8. Sensitive Data Risk

Emails may contain sensitive business or personal data.

Avoid unnecessary storage of full raw email body and attachments.

## 9. Large Artifact Risk

Model files and datasets can be large.

Use Git LFS or document manual artifact placement if needed.

---

## Current Known Issues (2026-05-23)

## 10. Gmail Ingestion Is Manual, Not Push-Based

Current runtime supports manually initiated sync only.

Implication:
- Not instant event-level real-time.
- Message visibility depends on a requested sync and provider/API latency.

Future improvement:
- Add a deliberately reviewed scheduling or Gmail `watch` + Pub/Sub workflow if strict real-time is required.

## 11. Gmail Sync Scope and Query Behavior

Current implementation fetches messages from `INBOX`.

Implication:
- Messages outside inbox labels may not be included.
- Query filtering and dedup strategy may need tuning for production usage.

## 12. Frontend Build Environment Variability

A prior environment experienced Vite `spawn EPERM` behavior.

Status:
- Not a code logic blocker for backend.
- Frontend functionality is implemented, but local environment constraints may still affect build tooling.

## 13. Empty/Placeholder Utility Scripts and FE Stub Files

Some scripts and feature-engineering helper files remain empty stubs (legacy planning artifacts).

Examples:
- `scripts/generate-demo-data.py`
- `scripts/reset-demo-db.py`
- `scripts/run-offline-demo.py`
- several `services/ml-service/feature-engineering/*.py` stub files

Risk:
- Can confuse new agents unless documented as non-runtime.

## 14. Security Hygiene Risk for Secrets

Runtime uses local secret files in `secrets/gmail`.

Risk:
- Credentials/token files must never be committed to source control.
- New agents must preserve secret handling rules and avoid printing token contents.

## 15. Auto-Sync Startup Behavior vs Seed Data

If backend is seeded with mock data and an operator manually syncs a different provider during a demo, queue contents can shift.

Recommendation:
- Explicitly choose the provider for each demo session.
- Avoid manual sync during demos that require static snapshots.

## 16. SQLite Schema Migration Needed for New Prediction Metadata

Model-management rollout added new prediction columns:
- `teacher_model_id`
- `surrogate_model_id`
- `feature_extractor_version`
- `explanation_snapshot`

Risk:
- Existing SQLite DB files created before this change may miss columns and fail inserts until schema is refreshed/migrated.

Recommendation:
- Reinitialize local DB from updated schema (`init_db.py`) or apply a migration before running new scan flows.

## 17. Environment Limitation: Backend Test Tooling May Be Missing

In some environments, `pytest` is not installed in the active Python runtime.

Risk:
- Changes may compile/build on frontend but backend regression tests cannot be executed until test dependencies are installed.

# Architecture Decisions

## ADR-001: Use an Agent-Neutral Project Structure

Decision:
Use `.agent/` instead of `.claude/`.

Reason:
The project may use Claude Code, Codex, Cursor, Windsurf, Antigravity, or another coding agent. The structure should not depend on one tool.

## ADR-002: Use a Monorepo Structure

Decision:
Keep frontend, backend, ML service, mailbox service, models, docs, and tests in one repository.

Reason:
The product needs tight coordination between dashboard UI, API, model inference, explanation outputs, and mailbox workflow.

## ADR-003: Separate Model Integration from Backend Routes

Decision:
Model loading, feature extraction, prediction, and explainability belong in `services/ml-service/`.

Reason:
FastAPI route files should stay thin and should not contain large ML logic.

## ADR-004: Mock Mailbox First

Decision:
Build mock mailbox before Gmail or Microsoft 365 integration.

Reason:
The product workflow can be validated faster without OAuth, API permissions, or real mailbox security complexity.

## ADR-005: No Permanent Email Deletion

Decision:
Suspicious emails must be moved to review/quarantine status, not deleted.

Reason:
False positives can disrupt business operations. SOC analysts must be able to release legitimate emails.

## ADR-006: No automatic model updating from User Feedback

Decision:
User feedback must be validated by SOC analysts before being used for retraining.

Reason:
Users can be wrong and attackers could poison the model through feedback.

## ADR-007: Preserve Prediction and Explanation History

Decision:
Every prediction must store model version and explanation snapshot.

Reason:
If the model changes later, old explanations must still explain the original decision.

## ADR-008: Provider-Based Mailbox Integration Layer

Decision:
Use a mailbox provider abstraction with concrete providers (`mock`, `gmail`) under backend service orchestration.

Reason:
Keeps mailbox-specific logic isolated and allows phased rollout (mock first, Gmail next, Microsoft later) without route rewrites.

## ADR-009: Mailbox Sync as Shared Service Function

Decision:
Move sync logic into a reusable backend service (`mailbox_sync_service.perform_mailbox_sync`) and call it from both API endpoint and background worker.

Reason:
Avoids duplicated sync logic and keeps behavior consistent between manual sync and automatic sync.

Status:
Partially superseded by ADR-015; the shared service remains, while the current runtime invokes it manually.

## ADR-010: Automatic Periodic Sync in Backend Runtime

Decision:
Start a lightweight background auto-sync loop when API server starts, with environment-controlled provider/interval/limit.

Reason:
Enables near-real-time ingestion for showcase and operations without requiring manual trigger of `/mailbox/sync`.

Status:
Superseded by ADR-015 for the current prototype runtime.

## ADR-011: Canonical Gmail Secret Paths in Repository

Decision:
Adopt `secrets/gmail/credentials.json` and `secrets/gmail/token.json` as default runtime paths.

Reason:
Reduces setup friction and avoids ambiguity from multiple secret directories.

## ADR-012: Frontend Action-First Investigation UX

Decision:
Keep investigation panel action buttons directly wired to backend workflow APIs (quarantine/release/feedback review), with immediate UI refresh and status feedback.

Reason:
SOC workflow is action-driven; investigation must not be read-only in MVP+ stages.

## ADR-013: Central Model Registry + Runtime Model Manager

Decision:
Introduce a dedicated model registry (`apps/backend/app/model_registry.py`) and runtime model manager service (`apps/backend/app/services/model_manager.py`) for active teacher/surrogate selection.

Reason:
Prevents invalid teacher/surrogate mismatches, keeps model switching logic out of API routes, and provides a single source of truth for model metadata, defaults, and compatibility rules.

## ADR-014: Persist Active Model Pair in Backend Config

Decision:
Persist active model pair in `apps/backend/config/active_model_config.json` with default `random_forest_v1 + ebm_random_forest_v1`.

Reason:
Allows stable runtime behavior across restarts and supports frontend Settings-driven model switching without code edits.

## ADR-015: Manual Sync and Fail-Closed Gmail Mutation Policy

Decision:
Use manually triggered mailbox sync in the current prototype. Permit any Gmail mailbox mutation only when `ALLOW_LIVE_GMAIL_ACTIONS=true` and `SHADOW_MODE=false`; automatic quarantine must not override analyst release or analyst-confirmed legitimate classification; continue mock action simulation for offline workflows.

Reason:
This keeps the MVP demonstrable while preventing an unreviewed runtime path from mutating a real mailbox by default.

## ADR-016: Bind Analyst Feedback to Historical Explanation Provenance

Decision:
Store the explanation snapshot identifier with feedback and derive confirmed result classifications on the backend from the stored original prediction and analyst label.

Reason:
Governance review must be traceable to the decision the analyst inspected and must not accept caller-supplied outcome classification as authoritative.

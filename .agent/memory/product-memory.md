# Product Memory

## Product Identity

This project is a SOC-friendly explainable phishing detection and model-governance dashboard for business mailboxes.

The product extends an existing research project on global explainability and explanation latency in phishing email detection.

## Main Product Claim

The product does not only detect phishing emails. It explains detections at:
1. the individual-email level through local explanations
2. the model-behaviour level through global surrogate explanations

## Existing Research Foundation

The project already has:
- Random Forest phishing detection model
- Deep Neural Network / MLP phishing detection model
- SHAP/LIME local explanation direction
- EBM global surrogate explanation model
- GAMI-Net global surrogate explanation model
- Accuracy Fidelity
- F1 Fidelity
- Error Fidelity

## Target Users

Primary:
- SOC analysts
- email security analysts

Secondary:
- general employees / mailbox users

Management:
- security managers
- CISOs
- risk/compliance teams

Technical:
- ML engineers
- model owners
- security engineers

## Dashboard Pages

The product dashboard should include:
- Overview
- Detection Queue
- Quarantine
- Email Investigation
- Local Explanation
- Global Explanation
- Feedback Review
- Model Monitoring
- Settings

## Current Build Strategy

Build in this order:
1. offline dashboard with mock data
2. mock backend API
3. model/explanation integration
4. mock mailbox workflow
5. feedback review workflow
6. real Gmail or Microsoft 365 integration later

## Important Product Rules

- Do not permanently delete emails.
- Do not automatically learn from user feedback.
- Do not retrain models unless explicitly requested.
- Preserve model version and explanation snapshot.
- Convert raw explanation values into human-readable SOC language.

---

## Memory Update (2026-05-26, Multi-Agent Hardening)

- A multi-agent audit and implementation pass hardened backend, frontend, ML explainability, mailbox safety, and tests.
- Mailbox sync is manual in the current runtime. Any Gmail mutation is fail-closed and requires `ALLOW_LIVE_GMAIL_ACTIONS=true` with `SHADOW_MODE=false`; automatic quarantine cannot override analyst release or confirmed-legitimate review; mock quarantine remains simulated for MVP workflows.
- Feedback now records historical explanation provenance and derives review outcomes server-side. Confirmed-feedback export remains disabled in this prototype.
- Local explanation failures, including explanation output with no usable contribution evidence, downgrade the decision to analyst review rather than allowing automatic action.
- Remaining production work includes authenticated roles/authorization, a retention policy for stored email bodies, and persistence semantics for ad-hoc scan submissions.

---

## Memory Update (2026-05-23)

### Current Phase Status

- Phase 1 (offline MVP): implemented and working.
- Phase 2 (DB/API persistence layer): implemented for core entities and flows.
- Phase 3 (model + explanation integration): integrated with existing artifacts and backend services.
- Phase 4 (feedback governance workflow): implemented for submission, review, provenance, and counters; export is reserved/disabled in this prototype.
- Phase 5 (mailbox integration): mock provider is operational and Gmail provider is implemented.

### Implemented Backend Capabilities

- Core dashboard APIs:
  - `GET /dashboard/summary`
  - `GET /emails`
  - `GET /emails/{id}`
  - `POST /scan-email`
  - `POST /scan-batch`
  - `GET /emails/{id}/local-explanation`
  - `GET /global-explanation`
- Feedback/governance APIs:
  - `GET /feedback`
  - `POST /emails/{id}/feedback`
  - `PATCH /feedback/{id}/review`
  - `POST /feedback/export-confirmed` (reserved endpoint; currently disabled)
- Quarantine/release:
  - `POST /emails/{id}/quarantine`
  - `POST /emails/{id}/release`
- Monitoring:
  - `GET /monitoring/model-health`
  - `GET /monitoring/model-versions`
  - `GET /monitoring/fidelity`
- Mailbox integration:
  - `GET /mailbox/providers`
  - `POST /mailbox/sync`

### Implemented Mailbox Behavior

- `mock` provider:
  - reads from `data/sample/sample_emails.json`
  - supports simulated quarantine/release
- `gmail` provider:
  - reads inbox via Gmail API (`users.messages.list` + `users.messages.get`)
  - parses headers/body preview/URL count/attachment metadata
  - performs label-based quarantine/release (`Phishing Review` label)

### Credentials and Token Convention

- Canonical secret location is:
  - `secrets/gmail/credentials.json`
  - `secrets/gmail/token.json`
- `.env.example` documents Gmail paths and shadow/live-action safety settings.

### Mailbox Sync Policy

- Backend runtime supports manually triggered mailbox sync.
- Live Gmail mutation is disabled unless `ALLOW_LIVE_GMAIL_ACTIONS=true` and `SHADOW_MODE=false`.
- Mock provider actions continue to be simulated for offline MVP workflows.

### Frontend Status (Showcase Pass)

- Overview:
  - real trend chart and risk distribution visualization implemented.
- Detection Queue:
  - status logic fixed; auto-refresh enabled.
- Email Investigation:
  - analyst actions are wired to backend (confirm phishing, false positive, release, add to quarantine).
- Quarantine:
  - now fully functional page with release action and auto-refresh.
- Feedback Review + Model Monitoring:
  - working with governance counters and review actions.

### Test Status

- Backend tests currently pass.
- Current baseline: `15 passed` in `apps/backend/app/tests`.

### Important Operational Notes

- New incoming Gmail messages appear only after a manually requested sync.
- Current Gmail fetch uses inbox label (`INBOX`) in list query.

---

## Memory Update (2026-05-23, Model Management Rollout)

### New Capability: Runtime Model Pair Switching

The system now supports selecting active teacher + surrogate model pairs at runtime through backend config APIs and frontend Settings.

Backend:
- `GET /api/models`
- `GET /api/models/active`
- `POST /api/models/active`
- `POST /api/scan-email` alias added (existing `/scan-email` preserved)

Frontend:
- Settings page now contains a full **Model Configuration** section with:
  - teacher model dropdown
  - compatible surrogate dropdown (auto-filtered by selected teacher)
  - save action
  - active model summary card with compatibility status badge

### Registry and Pairing Rules

Canonical selectable deployment models:
- Teachers:
  - `random_forest_v1` (default)
  - `deep_neural_net_v1`
- Surrogates:
  - `ebm_random_forest_v1` (default with RF)
  - `gaminet_random_forest_v1`
  - `ebm_deep_neural_net_v1`
  - `gaminet_deep_neural_net_v1`

Compatibility is enforced by backend validation. Invalid pairs are rejected.

### Runtime Sources

- Registry source: `apps/backend/app/model_registry.py`
- Runtime manager: `apps/backend/app/services/model_manager.py`
- Active persisted config: `apps/backend/config/active_model_config.json`

### Prediction Metadata Tracking

Prediction snapshots now support storing:
- `teacher_model_id`
- `surrogate_model_id`
- `feature_extractor_version`
- `explanation_snapshot`

And queue/detail API payloads now expose model IDs so SOC users can see which model pair produced each prediction.

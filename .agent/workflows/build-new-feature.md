# Workflow: Build New Feature

Use this workflow whenever adding a new product feature.

## Step 1: Understand the Feature

Read:
- `PROJECT_CONTEXT.md`
- `OUTCOME_REQUIREMENTS.md`
- `AGENTS.md`
- `IMPLEMENTATION_PLAN.md`
- relevant docs in `docs/`

Identify:
- target user
- dashboard page or API endpoint affected
- frontend/backend/model/mailbox boundary
- required data model
- required tests

## Step 2: Decide Ownership

Assign work to the correct area:

- UI feature → `apps/frontend/`
- API feature → `apps/backend/`
- prediction/explanation feature → `services/ml-service/`
- mailbox feature → `services/mailbox-service/`
- schema/persistence → `database/`
- docs → `docs/`
- tests → `tests/`

## Step 3: Design API/Data Contract First

Before coding UI, define expected data shape.

Example:

```json
{
  "email_id": "email_001",
  "prediction": "phishing",
  "confidence": 0.94,
  "risk_level": "high",
  "local_explanation": {
    "top_features": [],
    "human_summary": ""
  }
}
```

## Step 4: Implement Small Pieces

Build in this order:

1. types/schemas
2. backend/mock endpoint or service
3. frontend component/page
4. tests
5. documentation update

## Step 5: Follow Safety Rules

Check:

- no permanent email deletion
- no secrets committed
- no automatic model updating
- explanation is not overconfident
- model version and explanation snapshot are preserved where relevant

## Step 6: Run Tests

Use `.agent/workflows/run-tests-before-finish.md`.

## Step 7: Update Memory if Needed

Update:

- `.agent/memory/architecture-decisions.md` for architecture changes
- `.agent/memory/known-issues.md` for new risks
- docs if API or workflow changed

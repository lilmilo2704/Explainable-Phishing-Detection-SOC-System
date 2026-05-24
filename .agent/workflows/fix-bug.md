# Workflow: Fix Bug

Use this workflow when fixing a bug.

## Step 1: Reproduce

Identify:
- what is failing
- expected behaviour
- actual behaviour
- affected page/API/service
- error logs if available

## Step 2: Locate Responsibility

Classify the bug:

- UI bug → `apps/frontend/`
- API bug → `apps/backend/`
- model/prediction bug → `services/ml-service/`
- mailbox bug → `services/mailbox-service/`
- data/schema bug → `database/`
- test bug → `tests/`

## Step 3: Check Boundaries

Do not fix by moving logic into the wrong layer.

Examples:
- Do not fix prediction bugs in React.
- Do not fix mailbox bugs in dashboard components.
- Do not fix API bugs by hardcoding frontend data.

## Step 4: Write or Update a Test

Before or after the fix, add a test that would catch the bug.

## Step 5: Make Minimal Fix

Change the smallest reasonable amount of code.

## Step 6: Verify Related Workflows

Depending on the bug, test:
- scan email flow
- explanation flow
- feedback flow
- quarantine flow
- dashboard rendering

## Step 7: Document if Needed

If the bug reveals a recurring issue, update:
- `.agent/memory/known-issues.md`
- relevant docs

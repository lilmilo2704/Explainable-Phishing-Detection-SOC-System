# Workflow: Add API Endpoint

Use this workflow to add a new route to the FastAPI backend.

## Step 1: Define the Contract
- Update `docs/api/api-contracts.md` (or similar schema documentation) with the expected request and response JSON.
- Ensure the data structure is dashboard-ready.

## Step 2: Create Pydantic Schemas
- Add request/response schemas in `apps/backend/app/schemas/`.

## Step 3: Implement Business Logic
- Write the logic in `apps/backend/app/services/`.
- Do NOT place large logic or DB queries directly in the route handler.

## Step 4: Implement Route
- Add the FastAPI route in `apps/backend/app/api/`.
- Call the appropriate service function.

## Step 5: Add Tests
- Write a unit/integration test in `apps/backend/app/tests/`.
- Test happy path and relevant error states (e.g., 404, 400).

## Step 6: Verify Security
- Ensure no sensitive data (e.g., full email bodies) is unnecessarily exposed.
- Ensure no secrets are leaked in errors.

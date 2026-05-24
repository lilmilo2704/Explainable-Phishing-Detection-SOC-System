# Workflow: Add Mailbox Provider

Use this workflow to integrate a new real mailbox API (e.g., Gmail, Microsoft Graph).

## Step 1: Review Permissions
- Identify the minimum required OAuth scopes to read metadata and move emails.
- Document these permissions.

## Step 2: Setup Authentication
- Create placeholders in `.env.example`.
- Implement secure token handling (do not commit secrets).

## Step 3: Implement the Provider Interface
- Implement methods for:
  - `fetch_recent_emails()`
  - `move_to_quarantine(email_id)`
  - `release_from_quarantine(email_id)`

## Step 4: Integrate with Core Pipeline
- Ensure the fetched emails match the internal `Email` schema required by feature extraction.

## Step 5: Test
- Use a dedicated test account.
- Never run tests against a production mailbox without explicit approval.

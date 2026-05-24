# Gmail Mailbox Integration

## Current Prototype Behaviour

This version is a live Gmail prototype with a mock provider retained for tests. Mailbox sync is manually initiated from the dashboard or `POST /mailbox/sync`; no background sync is enabled.

Implemented capabilities:

- Gmail becomes the default provider when Gmail credential and token paths are configured.
- Live dashboard lists, metrics, feedback, and sync status default to the configured mailbox provider; when Gmail is configured, seeded/mock records are excluded from normal Gmail views.
- Full message body, metadata, attachments and extracted URLs are stored locally for the prototype.
- Unchanged messages are skipped unless the model version changes or a forced rescan is requested.
- Model failures are stored as `model_error` / `needs_review`, never silently allowed.
- Trusted high-risk results may trigger reversible quarantine according to policy.
- Quarantine, release, feedback review and model switching are recorded in the audit log.

## Local Gmail Configuration

Preferred setup: create a root `.env` file from `.env.example`; do not commit it:

```text
GMAIL_CREDENTIALS_PATH=C:\path\outside\repo\credentials.json
GMAIL_TOKEN_PATH=C:\path\outside\repo\token.json
GMAIL_REVIEW_LABEL=Phishing Review
MAILBOX_PROVIDER=gmail
SHADOW_MODE=true
FRONTEND_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

Generate or refresh an OAuth token locally using `scripts/generate_gmail_token.py`. Real credential and token files must remain outside source control and should be rotated if previously exposed.

Compatibility setup for this local workspace: if both ignored files already exist at `secrets/gmail/credentials.json` and `secrets/gmail/token.json`, the backend detects them automatically. This is intended only for untracked local development files; `.env` with an external location remains the preferred configuration.

## Gmail Label Actions

- Quarantine: add the configured review label and remove `INBOX`.
- Release: add `INBOX` and remove the configured review label.
- The application never deletes Gmail messages.

## API Endpoints

- `POST /mailbox/sync` manually syncs the configured provider.
- The dashboard `Sync Gmail` button explicitly requests a Gmail sync and refreshes the visible live panels after completion.
- `GET /mailbox/providers` reports whether Gmail is configured.
- `GET /mailbox/sync-status` returns last sync status, skipped/scanned/failed counts and safe failure details.
- `POST /emails/{id}/quarantine` performs a reversible containment action.
- `POST /emails/{id}/release` restores a quarantined message.
- `GET /audit` returns important action history.

## Normalized Message Shape

```json
{
  "mailbox_source": "gmail",
  "mailbox_message_id": "gmail_message_id",
  "subject": "Subject text",
  "sender": "sender@example.com",
  "reply_to": "reply@example.com",
  "body": "Full stored prototype message body",
  "body_preview": "Short display preview",
  "urls": ["https://example.com/verify"],
  "attachments": [],
  "content_fingerprint": "sha256-value"
}
```

## Safety Note

The exact processed feature order has been recovered from fitted EBM surrogate metadata and the fitted training preprocessor has been reconstructed from the original Git LFS training data, with full comparison against the saved processed split output. Model Readiness reports whether this validated pipeline is active for the selected model pairing. Gmail scanning remains manually triggered; trusted high-risk results can apply the configured reversible quarantine policy.

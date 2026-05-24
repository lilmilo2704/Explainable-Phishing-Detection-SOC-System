# Mailbox Integration (Phase 5)

This project now supports a provider-based mailbox integration flow.

## Implemented now

- `POST /mailbox/sync` with provider `mock`
- `GET /mailbox/providers`
- Mailbox-aware `POST /emails/{id}/quarantine` and `POST /emails/{id}/release`
- Prediction snapshot + explanation snapshot persistence during sync

## Gmail handoff (what you need to provide later)

Set these environment variables:

- `GMAIL_CREDENTIALS_PATH`
- `GMAIL_TOKEN_PATH`

Generate/refresh token using:

- `scripts/generate_gmail_token.py`

Current Gmail provider file:

- `apps/backend/app/services/mailbox_integration.py`

Implemented Gmail provider methods:

- `fetch_messages(limit)` via `users.messages.list` + `users.messages.get`
- `quarantine_message(mailbox_message_id)` via label add (`Phishing Review`)
- `release_message(mailbox_message_id)` via label removal

If you need custom label naming or Gmail query behavior, edit:

- `apps/backend/app/services/mailbox_integration.py`

## Expected normalized message shape

Each fetched message should be mapped to:

```json
{
  "id": "email_123",
  "mailbox_message_id": "gmail_message_id",
  "subject": "Subject text",
  "sender": "sender@example.com",
  "sender_domain": "example.com",
  "recipient": "user@company.com",
  "reply_to": "reply@example.com",
  "received_at": "2026-05-20T09:00:00Z",
  "body_preview": "first part of message body",
  "url_count": 2,
  "attachment_count": 1,
  "has_links": true,
  "has_attachment": true,
  "quarantine_status": "allowed",
  "review_status": "none"
}
```

## Integration test flow after Gmail is connected

1. `POST /mailbox/sync` with:

```json
{ "provider": "gmail", "limit": 10 }
```

2. Verify:
   - new/updated rows in `/emails`
   - prediction/explanation snapshots generated
   - high-risk messages get quarantine action

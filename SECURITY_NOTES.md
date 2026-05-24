# Security Notes - Gmail Prototype

## Credential Handling

- Never commit Gmail OAuth client credentials, access tokens, refresh tokens, `.env` files, or local databases.
- Store Gmail credential and token files outside tracked source control and point the application to them with environment variables.
- The application does not require credential contents in logs. Do not paste tokens or mailbox message bodies into bug reports.
- If any real OAuth credential or token has previously been shared or committed, revoke or rotate it in Google Cloud/Gmail before continuing to use this prototype.

## Local Configuration

The preferred setup is a local `.env` created from `.env.example` with absolute paths outside source control. The backend loads the root `.env` when it starts:

```text
GMAIL_CREDENTIALS_PATH=C:\path\outside\repo\credentials.json
GMAIL_TOKEN_PATH=C:\path\outside\repo\token.json
GMAIL_REVIEW_LABEL=Phishing Review
MAILBOX_PROVIDER=gmail
FRONTEND_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
SHADOW_MODE=true
```

Gmail sync remains manually triggered from the dashboard. The provider is enabled only when both Gmail paths are explicitly configured and readable.

For the existing development workspace, the backend also recognises both files when they already exist in the ignored local folder `secrets/gmail/`. This prevents repeated local setup failures while keeping token files outside Git tracking. The environment-variable setup remains preferred for moving the files outside the repository tree.

## Prototype Safety Rules

- Quarantine uses a Gmail review label and removes `INBOX`; release reverses those labels. Messages are never deleted.
- Predictions must not be treated as trusted automated decisions while the fitted training preprocessor or validated processed feature order is missing.
- Feedback is a user opinion until an analyst confirms it. No automatic retraining is performed.
- Full email bodies stored for this local prototype are sensitive operational data; protect or delete local databases when no longer needed.

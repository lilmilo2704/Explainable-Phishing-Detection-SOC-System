# Security and Privacy Rules

## Email Safety

- Never permanently delete emails.
- Suspicious emails must be moved to a review/quarantine state.
- Quarantined emails must be releasable by an analyst.
- Do not store full email body unless required for the current feature.
- Prefer storing metadata, extracted features, prediction, explanation, and review status.

## Secrets

- Do not commit secrets.
- Do not commit API keys.
- Do not commit OAuth tokens.
- Do not commit mailbox credentials.
- Use `.env` for local secrets.
- Keep `.env.example` placeholder-only.

## Logging

Do not log:
- full email bodies
- OAuth tokens
- mailbox credentials
- private user data
- raw attachments

Allowed logs:
- email ID
- risk level
- prediction label
- workflow status
- error codes
- non-sensitive debug messages

## Feedback Safety

- Do not automatically retrain models from user feedback.
- User feedback must be reviewed by a SOC analyst first.
- Only analyst-confirmed false positives and false negatives can be exported to improvement dataset.
- Preserve the original prediction and explanation snapshot.

## Explanation Safety

- Explanations show what influenced the model.
- Explanations are not absolute proof of phishing.
- Human-readable explanation text must avoid overconfident claims.
- Use wording such as “classified as phishing mainly because...” rather than “this proves the email is malicious.”

## Mailbox Permission Rule

Start with mock mailbox.

For real mailbox integration later:
- request minimum required permissions
- do not request full mailbox access unless necessary
- do not store refresh tokens in code
- document all mailbox permissions
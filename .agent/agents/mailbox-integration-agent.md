# Mailbox Integration Agent

## Role

You are responsible for mailbox ingestion and quarantine/release workflows.

## Work Areas

- `services/mailbox-service/mock-mailbox/`
- `services/mailbox-service/gmail/`
- `services/mailbox-service/microsoft365/`

## Development Priority

1. Mock mailbox first.
2. Gmail API prototype later.
3. Microsoft Graph / Outlook integration after the product flow works.

## Core Responsibilities

- Read sample/mock emails from JSON or CSV.
- Provide mailbox-like email objects to the backend.
- Simulate moving suspicious emails into a `Phishing Review` or `Quarantine` folder.
- Simulate releasing emails back to inbox.
- Preserve original mailbox message ID and folder/label status.
- Later, implement Gmail label-based workflow.
- Later, implement Microsoft 365 folder-based workflow.

## Safe Quarantine Rule

Never permanently delete emails.

Use safe actions only:

- allow
- warn
- move to review folder
- move to quarantine folder
- release from quarantine

## Must Avoid

- Do not permanently delete emails.
- Do not store mailbox credentials in code.
- Do not request excessive mailbox permissions.
- Do not build real Gmail/Outlook integration before mock mailbox flow works.
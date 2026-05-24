import base64

from app.services.mailbox_integration import GmailMailboxProvider


class _Exec:
    def __init__(self, payload):
        self.payload = payload

    def execute(self):
        return self.payload


class _Messages:
    def __init__(self, data):
        self.data = data

    def list(self, **kwargs):
        return _Exec({"messages": [{"id": "m1"}]})

    def get(self, **kwargs):
        return _Exec(self.data["message"])

    def modify(self, **kwargs):
        return _Exec({"id": kwargs["id"]})


class _Labels:
    def list(self, **kwargs):
        return _Exec({"labels": [{"id": "LBL_REVIEW", "name": "Phishing Review"}]})

    def create(self, **kwargs):
        return _Exec({"id": "LBL_REVIEW", "name": "Phishing Review"})


class _Users:
    def __init__(self, data):
        self._messages = _Messages(data)
        self._labels = _Labels()

    def messages(self):
        return self._messages

    def labels(self):
        return self._labels


class _FakeService:
    def __init__(self, data):
        self._users = _Users(data)

    def users(self):
        return self._users


def _b64(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode("utf-8")).decode("utf-8").rstrip("=")


def test_gmail_fetch_messages_parses_basic_fields(monkeypatch):
    provider = GmailMailboxProvider(credentials_path="x", token_path="y")
    message_payload = {
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Urgent verify now"},
                {"name": "From", "value": "IT Team <it@example.com>"},
                {"name": "To", "value": "user@company.com"},
                {"name": "Reply-To", "value": "helpdesk@example.com"},
                {"name": "Date", "value": "Fri, 22 May 2026 10:00:00 +0000"},
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": _b64("Click https://example.com/reset now")},
                },
                {
                    "mimeType": "application/pdf",
                    "filename": "invoice.pdf",
                    "body": {"attachmentId": "att1"},
                },
            ],
        }
    }

    monkeypatch.setattr(
        provider,
        "_get_service",
        lambda: _FakeService({"message": message_payload}),
    )

    rows = provider.fetch_messages(limit=1)
    assert len(rows) == 1
    row = rows[0]
    assert row["mailbox_message_id"] == "m1"
    assert row["subject"] == "Urgent verify now"
    assert row["sender_domain"] == "example.com"
    assert row["has_links"] is True
    assert row["has_attachment"] is True
    assert row["url_count"] >= 1


def test_gmail_label_modify_actions(monkeypatch):
    provider = GmailMailboxProvider(credentials_path="x", token_path="y")
    monkeypatch.setattr(provider, "_get_service", lambda: _FakeService({"message": {"payload": {"headers": []}}}))

    assert provider.quarantine_message("m1") is True
    assert provider.release_message("m1") is True

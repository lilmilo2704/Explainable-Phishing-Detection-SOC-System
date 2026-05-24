from __future__ import annotations

import json
import os
import re
import base64
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from datetime import datetime, UTC
from email.utils import parsedate_to_datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class MailboxProvider(Protocol):
    provider_name: str

    def fetch_messages(self, limit: int = 25) -> list[dict[str, Any]]:
        ...

    def quarantine_message(self, mailbox_message_id: str) -> bool:
        ...

    def release_message(self, mailbox_message_id: str) -> bool:
        ...


@dataclass
class MockMailboxProvider:
    provider_name: str = "mock"
    sample_path: Path | None = None

    def __post_init__(self):
        if self.sample_path is None:
            root = Path(__file__).resolve().parents[4]
            self.sample_path = root / "data" / "sample" / "sample_emails.json"

    def _read(self) -> list[dict[str, Any]]:
        if not self.sample_path or not self.sample_path.exists():
            return []
        with open(self.sample_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, rows: list[dict[str, Any]]) -> None:
        if not self.sample_path:
            return
        with open(self.sample_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)

    def fetch_messages(self, limit: int = 25) -> list[dict[str, Any]]:
        rows = self._read()
        return rows[: max(0, limit)]

    def quarantine_message(self, mailbox_message_id: str) -> bool:
        rows = self._read()
        changed = False
        for row in rows:
            if row.get("mailbox_message_id") == mailbox_message_id:
                row["quarantine_status"] = "quarantined"
                row["review_status"] = "in_review"
                changed = True
                break
        if changed:
            self._write(rows)
        return changed

    def release_message(self, mailbox_message_id: str) -> bool:
        rows = self._read()
        changed = False
        for row in rows:
            if row.get("mailbox_message_id") == mailbox_message_id:
                row["quarantine_status"] = "released"
                row["review_status"] = "reviewed"
                changed = True
                break
        if changed:
            self._write(rows)
        return changed


@dataclass
class GmailMailboxProvider:
    provider_name: str = "gmail"
    credentials_path: str | None = None
    token_path: str | None = None
    review_label: str = "Phishing Review"
    user_id: str = "me"

    def __post_init__(self):
        root = Path(__file__).resolve().parents[4]
        default_credentials = root / "secrets" / "gmail" / "credentials.json"
        default_token = root / "secrets" / "gmail" / "token.json"
        self.credentials_path = self.credentials_path or os.getenv(
            "GMAIL_CREDENTIALS_PATH", str(default_credentials)
        )
        self.token_path = self.token_path or os.getenv("GMAIL_TOKEN_PATH", str(default_token))

    def _assert_configured(self) -> None:
        if not self.credentials_path:
            raise RuntimeError("Gmail credentials path not configured. Set GMAIL_CREDENTIALS_PATH.")
        if not self.token_path:
            raise RuntimeError("Gmail token path not configured. Set GMAIL_TOKEN_PATH.")
        if not Path(self.credentials_path).exists():
            raise RuntimeError(f"Gmail credentials file not found: {self.credentials_path}")
        if not Path(self.token_path).exists():
            raise RuntimeError(f"Gmail token file not found: {self.token_path}")

    def _get_service(self):
        self._assert_configured()
        creds = Credentials.from_authorized_user_file(
            self.token_path,
            scopes=[
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.modify",
            ],
        )
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    @staticmethod
    def _header(headers: list[dict[str, str]], name: str) -> str:
        for h in headers or []:
            if h.get("name", "").lower() == name.lower():
                return h.get("value", "")
        return ""

    @staticmethod
    def _extract_email_addr(value: str) -> str:
        match = re.search(r"<([^>]+)>", value or "")
        if match:
            return match.group(1).strip()
        return (value or "").strip()

    @staticmethod
    def _sender_domain(sender: str) -> str:
        email = GmailMailboxProvider._extract_email_addr(sender)
        if "@" in email:
            return email.split("@", 1)[1].lower()
        return "unknown"

    @staticmethod
    def _decode_b64(data: str) -> str:
        if not data:
            return ""
        padding = "=" * ((4 - len(data) % 4) % 4)
        try:
            raw = base64.urlsafe_b64decode((data + padding).encode("utf-8"))
            return raw.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    def _extract_parts(self, payload: dict) -> tuple[str, list[dict[str, str]], list[str]]:
        body_chunks: list[str] = []
        attachments: list[dict[str, str]] = []
        urls: list[str] = []

        def walk(part: dict):
            mime = (part.get("mimeType") or "").lower()
            filename = part.get("filename") or ""
            body = part.get("body") or {}
            data = body.get("data")

            if filename:
                attachments.append(
                    {
                        "filename": filename,
                        "mime_type": part.get("mimeType", ""),
                        "attachment_id": body.get("attachmentId", ""),
                    }
                )

            if data and mime in {"text/plain", "text/html"}:
                text = self._decode_b64(data)
                if text:
                    body_chunks.append(text)
                    urls.extend(re.findall(r"https?://[^\s<>\"]+", text))

            for sub in part.get("parts", []) or []:
                walk(sub)

        walk(payload or {})
        full_text = "\n".join(body_chunks)
        return full_text, attachments, urls

    @staticmethod
    def _iso_date(raw_date: str, internal_date_ms: str | None = None) -> str:
        # Prefer Gmail internalDate because it is provider-generated and reliable.
        if internal_date_ms:
            try:
                ts = int(internal_date_ms) / 1000.0
                return datetime.fromtimestamp(ts, tz=UTC).isoformat().replace("+00:00", "Z")
            except Exception:
                pass

        if raw_date:
            # Parse RFC2822 date header and normalize to UTC ISO string.
            try:
                dt = parsedate_to_datetime(raw_date)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=UTC)
                else:
                    dt = dt.astimezone(UTC)
                return dt.isoformat().replace("+00:00", "Z")
            except Exception:
                pass

        return datetime.now(UTC).isoformat().replace("+00:00", "Z")

    def fetch_messages(self, limit: int = 25) -> list[dict[str, Any]]:
        service = self._get_service()
        try:
            target = max(1, limit)
            messages: list[dict[str, Any]] = []
            page_token = None
            # Paginate until we collect the requested amount.
            while len(messages) < target:
                req = (
                    service.users()
                    .messages()
                    .list(
                        userId=self.user_id,
                        maxResults=min(100, target - len(messages)),
                        labelIds=["INBOX"],
                        pageToken=page_token,
                    )
                )
                list_resp = req.execute()
                page_msgs = list_resp.get("messages", [])
                messages.extend(page_msgs)
                page_token = list_resp.get("nextPageToken")
                if not page_token or not page_msgs:
                    break

            output: list[dict[str, Any]] = []
            for item in messages[:target]:
                msg_id = item.get("id")
                if not msg_id:
                    continue
                msg = (
                    service.users()
                    .messages()
                    .get(userId=self.user_id, id=msg_id, format="full")
                    .execute()
                )
                payload = msg.get("payload", {})
                headers = payload.get("headers", [])
                subject = self._header(headers, "Subject")
                sender = self._header(headers, "From")
                recipient = self._header(headers, "To")
                reply_to = self._header(headers, "Reply-To") or self._extract_email_addr(sender)
                date_raw = self._header(headers, "Date")
                internal_date = msg.get("internalDate")

                body_text, attachments, urls = self._extract_parts(payload)
                preview = body_text.strip().replace("\n", " ")[:400]
                email_hash = hashlib.sha1(f"gmail::{msg_id}".encode("utf-8")).hexdigest()[:12]
                email_id = f"gmail_{email_hash}"
                output.append(
                    {
                        "id": email_id,
                        "mailbox_message_id": msg_id,
                        "subject": subject,
                        "sender": sender,
                        "sender_domain": self._sender_domain(sender),
                        "recipient": recipient,
                        "reply_to": reply_to,
                        "received_at": self._iso_date(date_raw, internal_date),
                        "body_preview": preview,
                        "url_count": len(urls),
                        "attachment_count": len(attachments),
                        "has_links": len(urls) > 0,
                        "has_attachment": len(attachments) > 0,
                        "quarantine_status": "allowed",
                        "review_status": "none",
                    }
                )
            return output
        except HttpError as e:
            raise RuntimeError(f"Gmail API fetch failed: {e}") from e

    def _get_or_create_label_id(self, service) -> str:
        labels = service.users().labels().list(userId=self.user_id).execute().get("labels", [])
        for label in labels:
            if label.get("name") == self.review_label:
                return label["id"]
        created = (
            service.users()
            .labels()
            .create(
                userId=self.user_id,
                body={
                    "name": self.review_label,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            )
            .execute()
        )
        return created["id"]

    def quarantine_message(self, mailbox_message_id: str) -> bool:
        service = self._get_service()
        try:
            review_label_id = self._get_or_create_label_id(service)
            (
                service.users()
                .messages()
                .modify(
                    userId=self.user_id,
                    id=mailbox_message_id,
                    body={"addLabelIds": [review_label_id], "removeLabelIds": []},
                )
                .execute()
            )
            return True
        except HttpError:
            return False

    def release_message(self, mailbox_message_id: str) -> bool:
        service = self._get_service()
        try:
            review_label_id = self._get_or_create_label_id(service)
            (
                service.users()
                .messages()
                .modify(
                    userId=self.user_id,
                    id=mailbox_message_id,
                    body={"addLabelIds": [], "removeLabelIds": [review_label_id]},
                )
                .execute()
            )
            return True
        except HttpError:
            return False


def get_mailbox_provider(provider: str) -> MailboxProvider:
    provider = (provider or "mock").lower()
    if provider == "mock":
        return MockMailboxProvider()
    if provider == "gmail":
        return GmailMailboxProvider()
    raise ValueError(f"Unsupported mailbox provider: {provider}")

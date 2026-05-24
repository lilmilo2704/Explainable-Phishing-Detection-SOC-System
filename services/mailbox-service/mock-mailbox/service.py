import json
from pathlib import Path
from typing import Any


class MockMailboxService:
    """
    Mock mailbox reader/writer for offline MVP.
    Uses local sample JSON and simulates reversible quarantine/release actions.
    """

    def __init__(self, sample_path: Path | None = None):
        root = Path(__file__).resolve().parents[3]
        self.sample_path = sample_path or (root / "data" / "sample" / "sample_emails.json")

    def load_emails(self) -> list[dict[str, Any]]:
        if not self.sample_path.exists():
            return []
        with open(self.sample_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_email(self, email_id: str) -> dict[str, Any] | None:
        for email in self.load_emails():
            if email.get("id") == email_id:
                return email
        return None

    def quarantine_email(self, email_id: str) -> dict[str, Any] | None:
        return self._update_status(email_id, quarantine_status="quarantined", review_status="in_review")

    def release_email(self, email_id: str) -> dict[str, Any] | None:
        return self._update_status(email_id, quarantine_status="released", review_status="reviewed")

    def _update_status(self, email_id: str, **updates) -> dict[str, Any] | None:
        rows = self.load_emails()
        updated = None
        for row in rows:
            if row.get("id") == email_id:
                row.update(updates)
                updated = row
                break
        if not updated:
            return None
        with open(self.sample_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        return updated

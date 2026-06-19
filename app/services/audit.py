import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from app.core.config import settings


class AuditService:
    def __init__(self) -> None:
        self.path: Path = settings.audit_log_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        record = {
            "ts": datetime.now(UTC).isoformat(),
            "event_type": event_type,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        items = [json.loads(line) for line in lines[-limit:] if line.strip()]
        return items


audit_service = AuditService()

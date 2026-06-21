import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.operator_mode import operator_mode_service


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

    def _all_items(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines if line.strip()]

    def recent(
        self,
        limit: int = 20,
        event_type: str | None = None,
        session_id: str | None = None,
    ) -> list[dict[str, Any]]:
        items = self._all_items()
        if event_type:
            items = [item for item in items if item.get("event_type") == event_type]
        if session_id:
            items = [item for item in items if item.get("payload", {}).get("session_id") == session_id]
        return items[-limit:]

    def timeline(self, session_id: str | None = None, limit: int = 30) -> list[dict[str, Any]]:
        items = self.recent(limit=limit * 4, session_id=session_id)
        timeline = []
        for item in items:
            payload = item.get("payload", {}) or {}
            preview = (
                payload.get("message")
                or payload.get("target")
                or payload.get("command")
                or payload.get("title")
                or payload.get("note")
                or payload.get("reply_preview")
                or ""
            )
            timeline.append(
                {
                    "ts": item.get("ts"),
                    "event_type": item.get("event_type"),
                    "session_id": payload.get("session_id"),
                    "preview": str(preview)[:120],
                    "payload": payload,
                }
            )
        return timeline[-limit:]

    def summary(self, session_id: str | None = None) -> dict[str, Any]:
        items = self.recent(limit=500, session_id=session_id)
        counts: dict[str, int] = {}
        for item in items:
            event_type = item.get("event_type", "unknown")
            counts[event_type] = counts.get(event_type, 0) + 1
        return {
            "ok": True,
            "count": len(items),
            "session_id": session_id,
            "event_counts": counts,
        }

    def operator_summary(self, session_id: str | None = None) -> dict[str, Any]:
        timeline = self.timeline(session_id=session_id, limit=80)
        risk_counts = {"low": 0, "medium": 0, "high": 0}
        for item in timeline:
            payload = item.get("payload", {}) or {}
            text = (
                payload.get("message")
                or payload.get("command")
                or payload.get("target")
                or payload.get("title")
                or ""
            )
            guard = payload.get("guard") or {}
            risk = guard.get("risk") or operator_mode_service.classify_command(str(text)).get("risk", "low")
            if risk not in risk_counts:
                risk_counts[risk] = 0
            risk_counts[risk] += 1

        return {
            "ok": True,
            "session_id": session_id,
            "timeline_events": len(timeline),
            "risk_counts": risk_counts,
            "latest": timeline[-5:],
        }

    def replay_candidates(self, session_id: str | None = None, limit: int = 12) -> list[dict[str, Any]]:
        items = self.recent(limit=300, session_id=session_id)
        candidates = []
        seen = set()
        for item in reversed(items):
            payload = item.get("payload", {}) or {}
            command = None
            if item.get("event_type") == "chat_turn" and payload.get("message"):
                command = payload.get("message")
            elif payload.get("command"):
                command = f"shell: {payload.get('command')}"
            elif payload.get("target") and item.get("event_type"):
                command = payload.get("target")
            if not command:
                continue
            if command in seen:
                continue
            seen.add(command)
            risk = (payload.get("guard") or {}).get("risk") or operator_mode_service.classify_command(str(command)).get("risk", "low")
            candidates.append(
                {
                    "ts": item.get("ts"),
                    "event_type": item.get("event_type"),
                    "command": command,
                    "risk": risk,
                }
            )
            if len(candidates) >= limit:
                break
        candidates.reverse()
        return candidates


audit_service = AuditService()

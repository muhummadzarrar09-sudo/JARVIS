import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.operator_mode import operator_mode_service


class AuditService:
    def __init__(self) -> None:
        self.path: Path = settings.audit_log_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _archive_dir(self) -> Path:
        path = self.path.parent / "archive"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _truncate(self, value: Any) -> Any:
        max_chars = settings.audit_max_field_chars
        max_items = settings.audit_max_collection_items

        if isinstance(value, str):
            return value[:max_chars]
        if isinstance(value, dict):
            items = list(value.items())[:max_items]
            return {str(k): self._truncate(v) for k, v in items}
        if isinstance(value, list):
            return [self._truncate(item) for item in value[:max_items]]
        if isinstance(value, tuple):
            return [self._truncate(item) for item in list(value)[:max_items]]
        return value

    def log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        record = {
            "ts": datetime.now(UTC).isoformat(),
            "event_type": str(event_type)[:120],
            "payload": self._truncate(payload or {}),
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _all_items(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        items: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                loaded = json.loads(line)
            except Exception:
                continue
            if isinstance(loaded, dict):
                items.append(loaded)
        return items

    def _archive_items(self) -> list[Path]:
        items = [p for p in self._archive_dir().iterdir() if p.is_file() and p.suffix.lower() == ".jsonl"]
        items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return items

    def _resolve_archive_path(self, raw_path: str) -> Path:
        base = self._archive_dir().resolve()
        candidate = Path(raw_path)
        resolved = candidate.resolve() if candidate.is_absolute() else (base / candidate.name).resolve()
        try:
            resolved.relative_to(base)
        except ValueError as e:
            raise ValueError(f"Archive path escapes archive directory: {raw_path}") from e
        return resolved

    def resolve_archive_path(self, raw_path: str) -> Path:
        return self._resolve_archive_path(raw_path)

    def status(self) -> dict[str, Any]:
        exists = self.path.exists()
        line_count = 0
        size_bytes = 0
        if exists:
            size_bytes = self.path.stat().st_size
            try:
                line_count = len([line for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()])
            except Exception:
                line_count = 0
        archives = self._archive_items()
        return {
            "ok": True,
            "path": str(self.path),
            "exists": exists,
            "size_bytes": size_bytes,
            "line_count": line_count,
            "archive_count": len(archives),
            "latest_archive": str(archives[0]) if archives else None,
            "plain_english": "This is the current audit log status for JARVIS.",
            "next_action": "Rotate the audit log if it grows too large." if exists and size_bytes > 2_000_000 else None,
        }

    def list_archives(self, limit: int = 20) -> dict[str, Any]:
        items = []
        for path in self._archive_items()[:limit]:
            items.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                    "modified_at": datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat(),
                }
            )
        return {"ok": True, "count": len(items), "items": items}

    def delete_archive(self, archive_path: str) -> dict[str, Any]:
        try:
            path = self._resolve_archive_path(archive_path)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        if not path.exists() or not path.is_file():
            return {"ok": False, "error": f"Archive file not found: {path}"}
        path.unlink(missing_ok=True)
        return {
            "ok": True,
            "deleted": True,
            "path": str(path),
            "plain_english": "JARVIS deleted the selected audit archive.",
        }

    def preview_archive(self, archive_path: str, limit: int = 20) -> dict[str, Any]:
        try:
            path = self._resolve_archive_path(archive_path)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        if not path.exists() or not path.is_file():
            return {"ok": False, "error": f"Archive file not found: {path}"}
        items: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                loaded = json.loads(line)
            except Exception:
                continue
            if isinstance(loaded, dict):
                items.append(loaded)
        return {
            "ok": True,
            "path": str(path),
            "count": min(limit, len(items)),
            "items": items[-limit:],
        }

    def verify_archive(self, archive_path: str) -> dict[str, Any]:
        try:
            path = self._resolve_archive_path(archive_path)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        if not path.exists() or not path.is_file():
            return {"ok": False, "error": f"Archive file not found: {path}"}

        valid_lines = 0
        invalid_lines = 0
        recent_items: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                loaded = json.loads(line)
                if isinstance(loaded, dict):
                    valid_lines += 1
                    recent_items.append(loaded)
                else:
                    invalid_lines += 1
            except Exception:
                invalid_lines += 1

        return {
            "ok": invalid_lines == 0,
            "path": str(path),
            "size_bytes": path.stat().st_size,
            "valid_lines": valid_lines,
            "invalid_lines": invalid_lines,
            "sample_tail": recent_items[-5:],
            "plain_english": "This is the audit archive verification result.",
        }

    def rotate(self, label: str | None = None, keep_archives: int = 10) -> dict[str, Any]:
        if not self.path.exists() or self.path.stat().st_size == 0:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch(exist_ok=True)
            return {
                "ok": True,
                "rotated": False,
                "plain_english": "Audit log was already empty, so JARVIS only ensured the file exists.",
            }

        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        safe_label = ""
        if label and label.strip():
            safe_label = "-" + "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in label.strip())[:40]
        archive_path = self._archive_dir() / f"audit-{stamp}{safe_label}.jsonl"
        self.path.replace(archive_path)
        self.path.touch(exist_ok=True)
        prune_result = self.prune_archives(keep=keep_archives)
        return {
            "ok": True,
            "rotated": True,
            "archive_path": str(archive_path),
            "prune_result": prune_result,
            "plain_english": "JARVIS rotated the active audit log into the archive folder.",
            "next_action": None,
        }

    def prune_archives(self, keep: int = 10) -> dict[str, Any]:
        keep = max(0, keep)
        archives = self._archive_items()
        removed = []
        for path in archives[keep:]:
            removed.append(str(path))
            path.unlink(missing_ok=True)
        return {
            "ok": True,
            "kept": min(keep, len(archives)),
            "removed_count": len(removed),
            "removed": removed,
            "plain_english": "JARVIS pruned old archived audit logs.",
        }

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

    def recent_by_types(self, event_types: list[str], limit: int = 20, session_id: str | None = None) -> list[dict[str, Any]]:
        wanted = {item for item in event_types if item}
        items = self._all_items()
        if wanted:
            items = [item for item in items if item.get("event_type") in wanted]
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

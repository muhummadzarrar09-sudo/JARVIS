import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.sqlite_service import connect_sqlite


class DatabaseService:
    def __init__(self) -> None:
        self.db_path: Path = settings.memory_db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _workspace_root(self) -> Path:
        return Path(settings.workspace_root).resolve()

    def _resolve_under_workspace(self, raw_path: str) -> Path:
        base = self._workspace_root()
        candidate = Path(raw_path)
        resolved = candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()
        try:
            resolved.relative_to(base)
        except ValueError as e:
            raise ValueError(f"Path escapes workspace root: {raw_path}") from e
        return resolved

    def _backup_dir(self) -> Path:
        raw = settings.data_dir / "backups"
        path = raw.resolve() if raw.is_absolute() else (self._workspace_root() / raw).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _backup_items(self) -> list[Path]:
        backup_dir = self._backup_dir()
        items = [p for p in backup_dir.iterdir() if p.is_file() and p.suffix.lower() in {".sqlite", ".sqlite3", ".db"}]
        items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return items

    def resolve_backup_path(self, raw_path: str) -> Path:
        backup_dir = self._backup_dir().resolve()
        candidate = Path(raw_path)
        resolved = candidate.resolve() if candidate.is_absolute() else (self._workspace_root() / candidate).resolve()
        try:
            resolved.relative_to(backup_dir)
        except ValueError as e:
            raise ValueError(f"Backup path escapes backup directory: {raw_path}") from e
        return resolved

    def status(self) -> dict[str, Any]:
        if not self.db_path.exists():
            return {
                "ok": True,
                "exists": False,
                "path": str(self.db_path),
                "backup_count": len(self._backup_items()),
                "plain_english": "The local SQLite database has not been created yet.",
            }

        with connect_sqlite(self.db_path) as conn:
            journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
            wal_checkpoint = conn.execute("PRAGMA wal_checkpoint(PASSIVE)").fetchone()
            try:
                sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            except Exception:
                sessions = 0
            try:
                messages = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            except Exception:
                messages = 0
            try:
                tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
            except Exception:
                tasks = 0

        size_bytes = self.db_path.stat().st_size
        return {
            "ok": True,
            "exists": True,
            "path": str(self.db_path),
            "size_bytes": size_bytes,
            "size_kb": round(size_bytes / 1024, 2),
            "journal_mode": journal_mode,
            "integrity_check": integrity,
            "wal_checkpoint": wal_checkpoint,
            "session_count": sessions,
            "message_count": messages,
            "task_count": tasks,
            "backup_count": len(self._backup_items()),
            "plain_english": "This is the current local SQLite state for sessions, messages, and tasks.",
            "next_action": None if integrity == "ok" else "Inspect the database because SQLite integrity_check did not return ok.",
        }

    def list_backups(self, limit: int = 20) -> dict[str, Any]:
        items = []
        for path in self._backup_items()[:limit]:
            try:
                rel = str(path.relative_to(self._workspace_root()))
            except Exception:
                rel = str(path)
            items.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "relative_path": rel,
                    "size_bytes": path.stat().st_size,
                    "modified_at": datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat(),
                }
            )
        return {"ok": True, "count": len(items), "items": items}

    def delete_backup(self, backup_path: str) -> dict[str, Any]:
        try:
            path = self.resolve_backup_path(backup_path)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        if not path.exists() or not path.is_file():
            return {"ok": False, "error": f"Backup file not found: {path}"}
        path.unlink(missing_ok=True)
        return {
            "ok": True,
            "deleted": True,
            "path": str(path),
            "plain_english": "JARVIS deleted the selected database backup.",
        }

    def verify_backup(self, backup_path: str) -> dict[str, Any]:
        try:
            path = self.resolve_backup_path(backup_path)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        if not path.exists() or not path.is_file():
            return {"ok": False, "error": f"Backup file not found: {path}"}
        try:
            with sqlite3.connect(path, timeout=5) as conn:
                integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        except Exception as e:
            return {
                "ok": False,
                "path": str(path),
                "relative_path": str(path.relative_to(self._workspace_root())),
                "error": f"SQLite backup verification failed: {e}",
            }
        return {
            "ok": integrity == "ok",
            "path": str(path),
            "relative_path": str(path.relative_to(self._workspace_root())),
            "size_bytes": path.stat().st_size,
            "integrity_check": integrity,
            "plain_english": "This is the database backup verification result.",
        }

    def backup(self, label: str | None = None) -> dict[str, Any]:
        if not self.db_path.exists():
            return {"ok": False, "error": f"Database file not found: {self.db_path}"}

        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        safe_label = ""
        if label and label.strip():
            safe_label = "-" + "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in label.strip())[:40]
        dest = self._backup_dir() / f"jarvis-memory-{stamp}{safe_label}.sqlite3"
        shutil.copy2(self.db_path, dest)
        return {
            "ok": True,
            "path": str(dest),
            "relative_path": str(dest.relative_to(self._workspace_root())),
            "plain_english": "JARVIS created a local SQLite backup copy.",
            "next_action": "Keep this backup somewhere safe if you want a restore point.",
        }

    def restore(self, backup_path: str, create_backup_first: bool = True) -> dict[str, Any]:
        try:
            source = self.resolve_backup_path(backup_path)
        except Exception as e:
            return {"ok": False, "error": str(e)}

        if not source.exists() or not source.is_file():
            return {"ok": False, "error": f"Backup file not found: {source}"}

        previous_backup = None
        if create_backup_first and self.db_path.exists():
            previous_backup = self.backup(label="pre-restore")
            if not previous_backup.get("ok"):
                return {
                    "ok": False,
                    "error": "Failed to create a safety backup before restore.",
                    "backup_result": previous_backup,
                }

        shutil.copy2(source, self.db_path)
        integrity = None
        try:
            with connect_sqlite(self.db_path) as conn:
                integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        except Exception as e:
            return {
                "ok": False,
                "error": f"Database restore copied the file but integrity validation failed: {e}",
                "restored_from": str(source),
                "previous_backup": previous_backup,
            }

        if integrity != "ok":
            return {
                "ok": False,
                "error": f"Restored database integrity_check returned: {integrity}",
                "restored_from": str(source),
                "previous_backup": previous_backup,
            }

        return {
            "ok": True,
            "restored_from": str(source),
            "restored_from_relative": str(source.relative_to(self._workspace_root())),
            "previous_backup": previous_backup,
            "integrity_check": integrity,
            "plain_english": "JARVIS restored the local SQLite database from the selected backup and verified it.",
            "next_action": "Refresh the shell state to confirm the restored data looks correct.",
        }

    def vacuum(self) -> dict[str, Any]:
        if not self.db_path.exists():
            return {"ok": False, "error": f"Database file not found: {self.db_path}"}
        before_size = self.db_path.stat().st_size
        with connect_sqlite(self.db_path) as conn:
            conn.execute("PRAGMA wal_checkpoint(FULL)")
            conn.execute("VACUUM")
            conn.execute("ANALYZE")
            conn.commit()
        after_size = self.db_path.stat().st_size
        return {
            "ok": True,
            "before_size_bytes": before_size,
            "after_size_bytes": after_size,
            "delta_bytes": after_size - before_size,
            "plain_english": "JARVIS vacuumed and analyzed the local SQLite database.",
            "next_action": None,
        }


database_service = DatabaseService()

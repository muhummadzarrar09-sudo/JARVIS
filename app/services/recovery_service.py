import json
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.audit import audit_service
from app.services.database_service import database_service


class RecoveryService:
    def _workspace_root(self) -> Path:
        return Path(settings.workspace_root).resolve()

    def _resolve_under_workspace(self, raw: Path) -> Path:
        base = self._workspace_root()
        resolved = raw.resolve() if raw.is_absolute() else (base / raw).resolve()
        try:
            resolved.relative_to(base)
        except ValueError as e:
            raise ValueError(f"Path escapes workspace root: {raw}") from e
        return resolved

    def _data_dir(self) -> Path:
        return self._resolve_under_workspace(Path(settings.data_dir))

    def _packs_dir(self) -> Path:
        path = self._data_dir() / "recovery" / "packs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _imports_dir(self) -> Path:
        path = self._data_dir() / "recovery" / "imports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _recent_validation_files(self, limit: int = 10) -> list[Path]:
        validation_dir = self._data_dir() / "validation"
        if not validation_dir.exists():
            return []
        items = [p for p in validation_dir.iterdir() if p.is_file() and p.suffix.lower() == ".json"]
        items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return items[:limit]

    def list_packs(self, limit: int = 20) -> dict[str, Any]:
        items = [p for p in self._packs_dir().iterdir() if p.is_file() and p.suffix.lower() == ".zip"]
        items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        payload = []
        for path in items[:limit]:
            payload.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "relative_path": str(path.relative_to(self._workspace_root())),
                    "size_bytes": path.stat().st_size,
                    "modified_at": datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat(),
                }
            )
        return {"ok": True, "count": len(payload), "items": payload}

    def resolve_pack_path(self, raw_path: str) -> Path:
        packs_dir = self._packs_dir().resolve()
        candidate = Path(raw_path)
        resolved = candidate.resolve() if candidate.is_absolute() else (self._workspace_root() / candidate).resolve()
        try:
            resolved.relative_to(packs_dir)
        except ValueError as e:
            raise ValueError(f"Recovery pack path escapes recovery pack directory: {raw_path}") from e
        return resolved

    def delete_pack(self, pack_path: str) -> dict[str, Any]:
        try:
            path = self.resolve_pack_path(pack_path)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        if not path.exists() or not path.is_file():
            return {"ok": False, "error": f"Recovery pack not found: {path}"}
        path.unlink(missing_ok=True)
        return {
            "ok": True,
            "deleted": True,
            "path": str(path),
            "plain_english": "JARVIS deleted the selected recovery pack.",
        }

    def verify_pack(self, pack_path: str) -> dict[str, Any]:
        try:
            source = self.resolve_pack_path(pack_path)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        if not source.exists() or not source.is_file():
            return {"ok": False, "error": f"Recovery pack not found: {source}"}

        with zipfile.ZipFile(source, "r") as archive:
            names = archive.namelist()
            manifest = None
            if "manifest.json" in names:
                try:
                    manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
                except Exception:
                    manifest = None

        required_entries = ["memory/jarvis.db", "logs/audit.jsonl", "memory/app_wrapper_state.json"]
        present_required = [name for name in required_entries if name in names]
        missing_required = [name for name in required_entries if name not in names]
        return {
            "ok": True,
            "path": str(source),
            "relative_path": str(source.relative_to(self._workspace_root())),
            "entry_count": len(names),
            "entries": names[:200],
            "manifest": manifest,
            "present_required": present_required,
            "missing_required": missing_required,
            "plain_english": "This is the current recovery-pack verification summary.",
        }

    def preview_pack(self, pack_path: str) -> dict[str, Any]:
        return self.verify_pack(pack_path)

    def export_pack(self, label: str | None = None, include_backups: bool = True, include_archives: bool = True) -> dict[str, Any]:
        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        safe_label = ""
        if label and label.strip():
            safe_label = "-" + "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in label.strip())[:40]
        pack_path = self._packs_dir() / f"jarvis-recovery-{stamp}{safe_label}.zip"

        manifest = {
            "ts": datetime.now(UTC).isoformat(),
            "app_name": settings.app_name,
            "database_status": database_service.status(),
            "audit_status": audit_service.status(),
            "files": [],
        }

        candidates: list[tuple[Path, str]] = []
        db_path = Path(settings.memory_db_path)
        audit_path = Path(settings.audit_log_path)
        wrapper_state = Path(settings.wrapper_state_path)
        env_example = self._workspace_root() / ".env.example"
        master_plan = self._workspace_root() / "docs" / "MASTER_PLAN_STATUS.md"

        for path, arcname in [
            (db_path, "memory/jarvis.db"),
            (audit_path, "logs/audit.jsonl"),
            (wrapper_state, "memory/app_wrapper_state.json"),
            (env_example, "config/.env.example"),
            (master_plan, "docs/MASTER_PLAN_STATUS.md"),
        ]:
            resolved = self._resolve_under_workspace(Path(path))
            if resolved.exists() and resolved.is_file():
                candidates.append((resolved, arcname))

        if include_backups:
            backups = database_service.list_backups(limit=50).get("items", [])
            for item in backups:
                path = self.resolve_under_workspace_or_none(item.get("relative_path") or item.get("path"))
                if path:
                    candidates.append((path, f"backups/{path.name}"))

        if include_archives:
            archives = audit_service.list_archives(limit=50).get("items", [])
            for item in archives:
                path = audit_service.resolve_archive_path(item.get("path"))
                if path.exists() and path.is_file():
                    candidates.append((path, f"audit_archive/{path.name}"))

        for path in self._recent_validation_files(limit=20):
            candidates.append((path, f"validation/{path.name}"))

        with zipfile.ZipFile(pack_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path, arcname in candidates:
                archive.write(file_path, arcname)
                manifest["files"].append({"arcname": arcname, "source": str(file_path), "size_bytes": file_path.stat().st_size})
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

        return {
            "ok": True,
            "path": str(pack_path),
            "relative_path": str(pack_path.relative_to(self._workspace_root())),
            "file_count": len(manifest["files"]),
            "plain_english": "JARVIS exported a local recovery pack with the current database, audit, state, and supporting artifacts.",
            "next_action": "Download the pack or keep it as a local restore/export checkpoint.",
        }

    def resolve_under_workspace_or_none(self, raw_path: str | None) -> Path | None:
        if not raw_path:
            return None
        try:
            path = self._resolve_under_workspace(Path(raw_path))
        except Exception:
            return None
        return path if path.exists() and path.is_file() else None

    def import_pack(
        self,
        pack_path: str,
        restore_database: bool = True,
        restore_audit: bool = True,
        restore_wrapper_state: bool = True,
        extract_only: bool = False,
        create_safety_backup: bool = True,
    ) -> dict[str, Any]:
        try:
            source = self.resolve_pack_path(pack_path)
        except Exception as e:
            return {"ok": False, "error": str(e)}

        if not source.exists() or not source.is_file():
            return {"ok": False, "error": f"Recovery pack not found: {source}"}

        stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        extract_dir = self._imports_dir() / f"import-{source.stem}-{stamp}"
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(source, "r") as archive:
            archive.extractall(extract_dir)

        manifest_path = extract_dir / "manifest.json"
        manifest = None
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                manifest = None

        if extract_only:
            return {
                "ok": True,
                "extract_only": True,
                "pack_path": str(source),
                "extract_dir": str(extract_dir),
                "manifest": manifest,
                "plain_english": "JARVIS extracted the recovery pack without restoring live files.",
            }

        results: dict[str, Any] = {
            "ok": True,
            "pack_path": str(source),
            "extract_dir": str(extract_dir),
            "manifest": manifest,
            "restored": {},
        }

        if create_safety_backup:
            results["safety_database_backup"] = database_service.backup(label="pre-pack-import") if Path(settings.memory_db_path).exists() else None
            current_audit = Path(settings.audit_log_path)
            if current_audit.exists() and current_audit.stat().st_size > 0:
                results["safety_audit_rotation"] = audit_service.rotate(label="pre-pack-import", keep_archives=20)

        if restore_database:
            imported_db = extract_dir / "memory" / "jarvis.db"
            if imported_db.exists():
                shutil.copy2(imported_db, Path(settings.memory_db_path))
                try:
                    with connect_sqlite(Path(settings.memory_db_path)) as conn:
                        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
                except Exception as e:
                    return {
                        "ok": False,
                        "error": f"Imported database file was copied but integrity validation failed: {e}",
                        "results": results,
                    }
                if integrity != "ok":
                    return {
                        "ok": False,
                        "error": f"Imported database integrity_check returned: {integrity}",
                        "results": results,
                    }
                results["restored"]["database"] = {"ok": True, "integrity_check": integrity}
            else:
                results["restored"]["database"] = {"ok": False, "error": "Database file not found inside the recovery pack."}

        if restore_audit:
            imported_audit = extract_dir / "logs" / "audit.jsonl"
            if imported_audit.exists():
                shutil.copy2(imported_audit, Path(settings.audit_log_path))
                results["restored"]["audit"] = {"ok": True}
            else:
                results["restored"]["audit"] = {"ok": False, "error": "Audit log file not found inside the recovery pack."}

        if restore_wrapper_state:
            imported_wrapper = extract_dir / "memory" / "app_wrapper_state.json"
            if imported_wrapper.exists():
                target = Path(settings.wrapper_state_path)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(imported_wrapper, target)
                results["restored"]["wrapper_state"] = {"ok": True}
            else:
                results["restored"]["wrapper_state"] = {"ok": False, "error": "Wrapper state file not found inside the recovery pack."}

        results["plain_english"] = "JARVIS imported the recovery pack and restored the selected live local files."
        results["next_action"] = "Refresh the shell and validation views to confirm the imported state looks correct."
        return results


recovery_service = RecoveryService()

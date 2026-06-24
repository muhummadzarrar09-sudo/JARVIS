import json
from pathlib import Path
from typing import Any

from app.core.config import settings


class MaintenanceSettingsService:
    def __init__(self) -> None:
        self.path: Path = settings.maintenance_settings_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def defaults(self) -> dict[str, Any]:
        return {
            "audit_keep": 10,
            "cleanup_keep_recent": 25,
            "cleanup_empty_days": 7,
            "cleanup_inactive_days": 90,
        }

    def get_settings(self) -> dict[str, Any]:
        data = self.defaults()
        if not self.path.exists():
            return {"ok": True, **data}
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {"ok": True, **data}
        if not isinstance(loaded, dict):
            return {"ok": True, **data}
        data.update({k: loaded.get(k, v) for k, v in data.items()})
        return {"ok": True, **data}

    def save_settings(
        self,
        audit_keep: int,
        cleanup_keep_recent: int,
        cleanup_empty_days: int,
        cleanup_inactive_days: int,
    ) -> dict[str, Any]:
        payload = {
            "audit_keep": max(0, min(200, int(audit_keep))),
            "cleanup_keep_recent": max(0, min(1000, int(cleanup_keep_recent))),
            "cleanup_empty_days": max(0, min(3650, int(cleanup_empty_days))),
            "cleanup_inactive_days": max(0, min(3650, int(cleanup_inactive_days))),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, **payload, "path": str(self.path), "plain_english": "JARVIS saved the maintenance settings for future shell sessions."}


maintenance_settings_service = MaintenanceSettingsService()

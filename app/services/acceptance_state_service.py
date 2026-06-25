import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings


class AcceptanceStateService:
    def __init__(self) -> None:
        self.path: Path = settings.acceptance_state_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"latest": None, "history": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {"latest": None, "history": []}
            data.setdefault("latest", None)
            data.setdefault("history", [])
            return data
        except Exception:
            return {"latest": None, "history": []}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def latest(self) -> dict[str, Any]:
        data = self._load()
        return {"ok": True, "latest": data.get("latest"), "history_count": len(data.get("history", []))}

    def history(self, limit: int = 20) -> dict[str, Any]:
        data = self._load()
        items = list(data.get("history", []))[-limit:]
        return {"ok": True, "count": len(items), "items": items}

    def record(self, report: dict[str, Any]) -> dict[str, Any]:
        data = self._load()
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            **report,
        }
        history = data.get("history", [])
        if not isinstance(history, list):
            history = []
        history.append(entry)
        history = history[-30:]
        data["latest"] = entry
        data["history"] = history
        self._save(data)
        return {"ok": True, "latest": entry, "history_count": len(history)}

    def export_latest(self, output_path: str | None = None) -> dict[str, Any]:
        data = self._load()
        latest = data.get("latest")
        if not latest:
            return {"ok": False, "error": "No acceptance result is available to export yet."}
        if output_path:
            target = Path(output_path)
        else:
            stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
            target = settings.data_dir / "validation" / f"acceptance-report-{stamp}.json"
        if not target.is_absolute():
            target = (Path(settings.workspace_root).resolve() / target).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "path": str(target), "plain_english": "JARVIS exported the latest acceptance report to a JSON file."}

    def reset(self) -> dict[str, Any]:
        data = {"latest": None, "history": []}
        self._save(data)
        return {"ok": True, "reset": True, "path": str(self.path)}


acceptance_state_service = AcceptanceStateService()

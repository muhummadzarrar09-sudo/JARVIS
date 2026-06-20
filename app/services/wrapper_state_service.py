import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from app.core.config import settings


class WrapperStateService:
    def __init__(self) -> None:
        self.path: Path = settings.wrapper_state_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"wrappers": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {"wrappers": {}}
            data.setdefault("wrappers", {})
            return data
        except Exception:
            return {"wrappers": {}}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def all_states(self) -> dict[str, Any]:
        return self._load().get("wrappers", {})

    def get_state(self, wrapper_name: str) -> dict[str, Any]:
        data = self._load().get("wrappers", {})
        state = data.get(wrapper_name, {})
        return state if isinstance(state, dict) else {}

    def update_state(self, wrapper_name: str, **fields: Any) -> dict[str, Any]:
        data = self._load()
        wrappers = data.setdefault("wrappers", {})
        current = wrappers.get(wrapper_name, {})
        if not isinstance(current, dict):
            current = {}

        cleaned = {k: v for k, v in fields.items() if v is not None}
        current.update(cleaned)
        current["updated_at"] = datetime.now(UTC).isoformat()
        wrappers[wrapper_name] = current
        self._save(data)
        return current


wrapper_state_service = WrapperStateService()

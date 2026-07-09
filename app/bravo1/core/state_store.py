from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class StateStore:
    data_dir: Path
    path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.data_dir / "app_state.json"

    def save(self, payload: dict[str, Any]) -> Path:
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return self.path

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"ok": False, "error": "No saved state snapshot yet."}
        return json.loads(self.path.read_text(encoding="utf-8"))

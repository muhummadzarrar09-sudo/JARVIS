from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from bravo1.core.session import SessionState


@dataclass(slots=True)
class ProjectContinuity:
    data_dir: Path
    state_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.data_dir / "project_state.json"

    def sync_from_session(self, state: SessionState) -> dict:
        current_project = state.current_project or "BRAVO-1 rebuild"
        payload = {
            "current_project": current_project,
            "current_goal": state.current_goal or "",
            "last_primary_action": state.last_primary_action or "",
            "last_summary_path": state.last_summary_path or "",
            "session_id": state.session_id,
        }
        self.state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    def inspect(self) -> dict:
        if not self.state_path.exists():
            return {
                "ok": True,
                "current_project": "BRAVO-1 rebuild",
                "current_goal": "",
                "last_primary_action": "",
                "last_summary_path": "",
                "plain_english": "Project continuity has not been synced yet.",
            }
        payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        payload["ok"] = True
        payload["plain_english"] = "This is the current BRAVO-1 project continuity snapshot."
        return payload

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from bravo1.core.session import SessionState


@dataclass(slots=True)
class ProjectContinuity:
    data_dir: Path
    state_path: Path = field(init=False)
    captures_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.data_dir / "project_state.json"
        self.captures_path = self.data_dir / "project_captures.jsonl"

    def sync_from_session(self, state: SessionState) -> dict:
        current_project = state.current_project or "BRAVO-1 rebuild"
        payload = {
            "current_project": current_project,
            "current_goal": state.current_goal or "",
            "last_primary_action": state.last_primary_action or "",
            "last_summary_path": state.last_summary_path or "",
            "session_id": state.session_id,
            "recent_captures": self.recent_captures(limit=5),
        }
        self.state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    def capture(self, state: SessionState, kind: str, text: str) -> dict:
        clean_kind = (kind or "note").strip().lower().replace(" ", "_")
        clean_text = (text or "").strip()
        if not clean_text:
            return {"ok": False, "error": "Capture text is required."}
        item = {
            "kind": clean_kind,
            "text": clean_text[:1000],
            "project": state.current_project or "BRAVO-1 rebuild",
            "session_id": state.session_id,
            "created_at": datetime.now(UTC).isoformat(),
        }
        with self.captures_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        self.sync_from_session(state)
        return {
            "ok": True,
            "capture": item,
            "recent_captures": self.recent_captures(limit=5),
            "plain_english": f"Saved this {clean_kind.replace('_', ' ')} for the current project.",
        }

    def recent_captures(self, limit: int = 5) -> list[dict]:
        if not self.captures_path.exists():
            return []
        lines = self.captures_path.read_text(encoding="utf-8").splitlines()
        items: list[dict] = []
        for line in reversed(lines):
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if len(items) >= limit:
                break
        return items

    def inspect(self) -> dict:
        if not self.state_path.exists():
            return {
                "ok": True,
                "current_project": "BRAVO-1 rebuild",
                "current_goal": "",
                "last_primary_action": "",
                "last_summary_path": "",
                "recent_captures": self.recent_captures(limit=5),
                "plain_english": "Project continuity has not been synced yet.",
            }
        payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        payload["recent_captures"] = self.recent_captures(limit=5)
        payload["ok"] = True
        payload["plain_english"] = "This is the current BRAVO-1 project continuity snapshot."
        return payload

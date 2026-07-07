from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


@dataclass(slots=True)
class SessionState:
    session_id: str
    created_at: str
    updated_at: str
    current_goal: str = ""
    current_project: str = ""
    last_primary_action: str = ""
    last_summary_path: str = ""
    recent_messages: list[dict[str, str]] = field(default_factory=list)

    @classmethod
    def fresh(cls) -> "SessionState":
        now = datetime.now(UTC).isoformat()
        return cls(session_id=str(uuid4()), created_at=now, updated_at=now)


class SessionManager:
    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.active_path = self.session_dir / "active_session.json"

    def load(self) -> SessionState:
        if not self.active_path.exists():
            state = SessionState.fresh()
            self.save(state)
            return state
        payload = json.loads(self.active_path.read_text(encoding="utf-8"))
        payload.setdefault("last_summary_path", "")
        payload.setdefault("recent_messages", [])
        return SessionState(**payload)

    def save(self, state: SessionState) -> None:
        state.updated_at = datetime.now(UTC).isoformat()
        self.active_path.write_text(
            json.dumps(asdict(state), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def append_message(self, state: SessionState, role: str, content: str) -> SessionState:
        state.recent_messages.append({"role": role, "content": content[:2000]})
        state.recent_messages = state.recent_messages[-12:]
        self.save(state)
        return state

    def set_goal(self, state: SessionState, goal: str) -> SessionState:
        state.current_goal = goal.strip()
        self.save(state)
        return state

    def set_project(self, state: SessionState, project: str) -> SessionState:
        state.current_project = project.strip()
        self.save(state)
        return state

    def snapshot(self, state: SessionState) -> dict:
        return {
            "session_id": state.session_id,
            "created_at": state.created_at,
            "updated_at": state.updated_at,
            "current_goal": state.current_goal,
            "current_project": state.current_project,
            "last_primary_action": state.last_primary_action,
            "last_summary_path": state.last_summary_path,
            "recent_messages": state.recent_messages[-6:],
        }

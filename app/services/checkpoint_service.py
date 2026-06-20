import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.memory import memory_service


class CheckpointService:
    def __init__(self) -> None:
        self.base_dir: Path = settings.checkpoint_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for_session(self, session_id: str) -> Path:
        safe_session = session_id.replace("/", "_").replace("\\", "_")
        return self.base_dir / f"{safe_session}.json"

    def create(self, session_id: str, note: str | None = None) -> dict[str, Any]:
        messages = memory_service.recent_messages(session_id, limit=20)
        payload = {
            "session_id": session_id,
            "created_at": datetime.now(UTC).isoformat(),
            "note": note,
            "recent_messages": messages,
            "message_count": len(messages),
        }
        path = self._path_for_session(session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "path": str(path), "checkpoint": payload}

    def load(self, session_id: str) -> dict[str, Any]:
        path = self._path_for_session(session_id)
        if not path.exists():
            return {"ok": False, "error": f"No checkpoint found for session {session_id}"}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return {"ok": True, "path": str(path), "checkpoint": payload}
        except Exception as e:
            return {"ok": False, "error": str(e)}


checkpoint_service = CheckpointService()

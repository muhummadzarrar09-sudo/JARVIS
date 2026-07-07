from __future__ import annotations

from bravo1.brain.obsidian import ObsidianBrain
from bravo1.config import Settings
from bravo1.core.session import SessionManager
from bravo1.models.router import ModelRouter
from bravo1.tools.registry import ToolRegistry


class Operator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_dirs()
        self.sessions = SessionManager(settings.session_dir)
        self.brain = ObsidianBrain(settings.brain_dir)
        self.router = ModelRouter(settings)
        self.tools = ToolRegistry()

    def handle(self, message: str) -> dict:
        state = self.sessions.load()
        self.sessions.append_message(state, "user", message)
        active_context = self.brain.read_active()
        route = self.router.route("brief")

        primary_action = "define the next core loop"
        if "browser" in message.lower():
            primary_action = "design the browser operator adapter"
        elif "project" in message.lower():
            primary_action = "stabilize project continuity structure"

        reply = (
            f"BRAVO-1 scaffold online.\n"
            f"Session: {state.session_id}\n"
            f"Route: {route.lane} -> {route.model_name}\n"
            f"Primary action: {primary_action}\n\n"
            f"Active context preview:\n{active_context[:500]}"
        )
        self.sessions.append_message(state, "assistant", reply)
        state.last_primary_action = primary_action
        self.sessions.save(state)
        return {
            "ok": True,
            "session_id": state.session_id,
            "primary_action": primary_action,
            "route": route,
            "reply": reply,
        }
